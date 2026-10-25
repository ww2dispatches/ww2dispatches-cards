// POST {credential} from Google Identity Services. Finds or makes the player and sets the session cookie.
import { json, fail, hmac, nowIso } from '../../_lib/util.js';
import { verifyGoogleToken } from '../../_lib/google.js';
import { makeSessionCookie } from '../../_lib/session.js';
import { publicPlayer } from '../../_lib/player.js';

export async function onRequestPost({ request, env }) {
  let body;
  try { body = await request.json(); } catch { return fail(400, 'bad request'); }

  let sub;
  try { sub = await verifyGoogleToken(body.credential, env.GOOGLE_CLIENT_ID); }
  catch (err) { return fail(401, 'sign in failed'); }

  const playerId = (await hmac(env.ID_SALT, 'google:' + sub)).slice(0, 32);
  const tester = env.LAUNCHED === '1' ? 0 : 1;
  await env.DB.prepare('INSERT OR IGNORE INTO players (id, created_at, tester) VALUES (?, ?, ?)')
    .bind(playerId, nowIso(), tester).run();
  const player = await env.DB.prepare('SELECT * FROM players WHERE id = ?').bind(playerId).first();

  return json({ player: publicPlayer(player) }, 200, { 'set-cookie': await makeSessionCookie(env, playerId) });
}
