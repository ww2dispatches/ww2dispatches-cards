// Email sign in with a six digit code (13 Nov 2026). Works in every browser, including the built in
// browsers of social apps, where Google sign in is refused.
//   POST {email}                         asks for a code. Always answers the same way for any address.
//   POST {email, code, starter?, ...}    checks the code, finds or makes the player, sets the session cookie,
//                                        and saves a starter pack opened before sign in (as Google sign in does).
// The email is never stored: see functions/_lib/emailcode.js.
import { json, fail, nowIso } from '../../_lib/util.js';
import { makeSessionCookie } from '../../_lib/session.js';
import { publicPlayer } from '../../_lib/player.js';
import { now } from '../../_lib/catalog.js';
import { readToken, saveStarter } from '../../_lib/starter.js';
import { signPending } from '../../_lib/pulls.js';
import { bump, sourceName } from '../../_lib/tally.js';
import { gameDay } from '../../_lib/time.js';
import { normalizeEmail, emailId, makeCode, forgetCode, checkCode, playerFor, CODE_MINUTES } from '../../_lib/emailcode.js';
import { mailMode, sendCode } from '../../_lib/mail.js';

export async function onRequestPost({ request, env }) {
  if (mailMode(env) === 'off') return fail(503, 'email sign in is off');
  let body;
  try { body = (await request.json()) || {}; } catch { return fail(400, 'bad request'); }
  const email = normalizeEmail(body.email);
  if (!email) return fail(400, 'bad email');
  const t = now(env, request), id = await emailId(env, email);

  // ---- ask for a code ----
  if (body.code === undefined || body.code === null || body.code === '') {
    const made = await makeCode(env, id, t, undefined, request.headers.get('CF-Connecting-IP') || '');
    if (!made.ok) {
      if (made.why === 'wait') return json({ error: 'wait', wait: made.wait }, 429);
      return fail(429, made.why); // 'slow', 'many', or 'busy'
    }
    const sent = await sendCode(env, email, made.code);
    if (!sent.ok) { await forgetCode(env, id).catch(() => {}); return fail(502, 'mail failed'); }
    return json(Object.assign({ sent: true, minutes: CODE_MINUTES }, sent.test ? { test: sent.test } : {}));
  }

  // ---- check the code and sign in ----
  const verdict = await checkCode(env, id, body.code, t);
  if (verdict !== 'ok') return fail(verdict === 'wrong' ? 401 : 410, verdict === 'wrong' ? 'wrong code' : verdict === 'locked' ? 'code locked' : 'code expired');

  let player = await playerFor(env.DB, id);
  if (!player) {
    const tester = env.LAUNCHED === '1' ? 0 : 1;
    const made = await env.DB.prepare('INSERT OR IGNORE INTO players (id, created_at, tester) VALUES (?, ?, ?)').bind(id, nowIso(), tester).run();
    if (made.meta && made.meta.changes) await bump(env.DB, gameDay(t), [['signup', sourceName(body.src), 1], ['signup_how', 'email', 1]]).catch(() => {});
    player = await env.DB.prepare('SELECT * FROM players WHERE id = ?').bind(id).first();
  }

  let starterSaved = false;
  if (body.starter && !player.starter_done) {
    const picks = await readToken(env, body.starter, t);
    if (picks && (await saveStarter(env, player.id, picks, t, body.starterTurned !== false))) {
      starterSaved = true;
      await signPending(env, player.id);
      player = await env.DB.prepare('SELECT * FROM players WHERE id = ?').bind(player.id).first();
    }
  }

  return json({ player: publicPlayer(player, t), starterSaved }, 200, { 'set-cookie': await makeSessionCookie(env, player.id) });
}
