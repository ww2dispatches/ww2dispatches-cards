// POST {credential, starter?} from Google Identity Services. Finds or makes the player and sets
// the session cookie. If the browser holds a starter pack opened before sign in, it is saved
// into the dossier now (only if this account has no starter pack yet).
import { json, fail, hmac, nowIso } from '../../_lib/util.js';
import { verifyGoogleToken } from '../../_lib/google.js';
import { makeSessionCookie } from '../../_lib/session.js';
import { publicPlayer } from '../../_lib/player.js';
import { now } from '../../_lib/catalog.js';
import { readToken, saveStarter } from '../../_lib/starter.js';
import { signPending } from '../../_lib/pulls.js';

export async function onRequestPost({ request, env }) {
  let body;
  try { body = (await request.json()) || {}; } catch { return fail(400, 'bad request'); }

  let sub;
  const fakeSub = env.ALLOW_FAKE_NOW === '1' && request.headers.get('x-declass-fake-google'); // test copies only
  if (fakeSub) sub = 'test:' + fakeSub;
  else {
    try { sub = await verifyGoogleToken(body.credential, env.GOOGLE_CLIENT_ID); }
    catch (err) { return fail(401, 'sign in failed'); }
  }

  const playerId = (await hmac(env.ID_SALT, 'google:' + sub)).slice(0, 32);
  const tester = env.LAUNCHED === '1' ? 0 : 1;
  await env.DB.prepare('INSERT OR IGNORE INTO players (id, created_at, tester) VALUES (?, ?, ?)')
    .bind(playerId, nowIso(), tester).run();
  let player = await env.DB.prepare('SELECT * FROM players WHERE id = ?').bind(playerId).first();

  let starterSaved = false;
  if (body.starter && !player.starter_done) {
    const t = now(env, request);
    const picks = await readToken(env, body.starter, t);
    if (picks && (await saveStarter(env, playerId, picks, t, body.starterTurned !== false))) {
      starterSaved = true;
      await signPending(env, playerId);
      player = await env.DB.prepare('SELECT * FROM players WHERE id = ?').bind(playerId).first();
    }
  }

  return json({ player: publicPlayer(player, now(env, request)), starterSaved }, 200, { 'set-cookie': await makeSessionCookie(env, playerId) });
}
