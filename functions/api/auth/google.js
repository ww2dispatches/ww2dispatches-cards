// POST {credential, starter?} from Google Identity Services. Finds or makes the player and sets
// the session cookie. If the browser holds a starter pack opened before sign in, it is saved
// into the dossier now (only if this account has no starter pack yet).
import { json, fail, hmac, nowIso } from '../../_lib/util.js';
import { verifyGoogleIdentity } from '../../_lib/google.js';
import { normalizeEmail, emailId, playerFor, addAlias } from '../../_lib/emailcode.js';
import { makeSessionCookie } from '../../_lib/session.js';
import { publicPlayer } from '../../_lib/player.js';
import { now } from '../../_lib/catalog.js';
import { readToken, saveStarter } from '../../_lib/starter.js';
import { signPending } from '../../_lib/pulls.js';
import { bump, sourceName } from '../../_lib/tally.js';
import { gameDay } from '../../_lib/time.js';

export async function onRequestPost({ request, env }) {
  let body;
  try { body = (await request.json()) || {}; } catch { return fail(400, 'bad request'); }

  let sub, gmail = '';
  const fakeSub = env.ALLOW_FAKE_NOW === '1' && request.headers.get('x-declass-fake-google'); // test copies only
  if (fakeSub) { sub = 'test:' + fakeSub; gmail = request.headers.get('x-declass-fake-email') || ''; }
  else {
    try { ({ sub, email: gmail } = await verifyGoogleIdentity(body.credential, env.GOOGLE_CLIENT_ID)); }
    catch (err) { return fail(401, 'sign in failed'); }
  }

  const googleId = (await hmac(env.ID_SALT, 'google:' + sub)).slice(0, 32);
  // One dossier however they sign in (13 Nov 2026): the account's address is scrambled into a second id.
  // If that address already has a dossier from email sign in, this Google account opens the same one.
  // Any trouble here never blocks the sign in itself.
  const mail = normalizeEmail(gmail);
  const mailId = mail ? await emailId(env, mail).catch(() => '') : '';
  let player = await playerFor(env.DB, googleId).catch(() => null);
  if (!player && mailId) {
    player = await playerFor(env.DB, mailId).catch(() => null);
    if (player) await addAlias(env.DB, googleId, player.id, nowIso()).catch(() => {});
  }
  if (!player) {
    const tester = env.LAUNCHED === '1' ? 0 : 1;
    const made = await env.DB.prepare('INSERT OR IGNORE INTO players (id, created_at, tester) VALUES (?, ?, ?)')
      .bind(googleId, nowIso(), tester).run();
    // a new account: count it by where this browser first came from (console Growth tab; a count only)
    if (made.meta && made.meta.changes) await bump(env.DB, gameDay(now(env, request)), [['signup', sourceName(body.src), 1], ['signup_how', 'google', 1]]).catch(() => {});
    player = await env.DB.prepare('SELECT * FROM players WHERE id = ?').bind(googleId).first();
  }
  if (mailId) await addAlias(env.DB, mailId, player.id, nowIso()).catch(() => {});
  const playerId = player.id;

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
