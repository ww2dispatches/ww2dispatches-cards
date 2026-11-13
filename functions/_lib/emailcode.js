// Email sign in with a six digit code (13 Nov 2026).
// Why: links tapped in Threads, Instagram, Facebook, and TikTok open in the app's own built in browser,
// where Google refuses to sign anyone in. An email and a code work in every browser.
//
// What is kept: never the email. It is turned into a scrambled id (HMAC with ID_SALT, the same way
// Google account numbers are), used once to send the code, and dropped. A pending code is kept as a
// keyed hash for ten minutes, then deleted.
//
// Tables are created on first use, like the Code Room and tally tables (no setup step):
//   email_codes: one pending code per scrambled email id, plus one counter row per day ("_day:...").
//   aliases:     a second scrambled id that points at an existing player, so a player who signed in
//                with Google can also sign in with the same address by email, and the other way round.
import { hmac, hmacVerify } from './util.js';
import { secureInt } from './odds.js';

export const CODE_MINUTES = 10;      // a code works this long
export const MAX_TRIES = 5;          // wrong guesses before the code is thrown away
export const RESEND_SECONDS = 60;    // wait between sends to one address
export const HOURLY_SENDS = 5;       // sends to one address in an hour
const DEFAULT_DAILY_CAP = 90;        // all sends in a day (the free mail plan allows 100)

const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS email_codes (id TEXT PRIMARY KEY, code_hash TEXT NOT NULL DEFAULT '', expires_at INTEGER NOT NULL DEFAULT 0, tries INTEGER NOT NULL DEFAULT 0, sent_at INTEGER NOT NULL DEFAULT 0, sends INTEGER NOT NULL DEFAULT 0, window_start INTEGER NOT NULL DEFAULT 0)`,
  `CREATE TABLE IF NOT EXISTS aliases (alias TEXT PRIMARY KEY, player_id TEXT NOT NULL, created_at TEXT NOT NULL)`,
];
let ready = null;
export function ensureEmailTables(db) {
  if (!ready) ready = db.batch(SCHEMA.map(s => db.prepare(s))).catch(err => { ready = null; throw err; });
  return ready;
}

// A tidy address, or '' if it does not look like one. Lower case, so Bob@ and bob@ are one player.
export function normalizeEmail(raw) {
  const s = String(raw || '').trim().toLowerCase();
  if (s.length < 6 || s.length > 254) return '';
  if (!/^[^\s@<>()",;:\\]+@[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)+$/.test(s)) return '';
  if (s.split('@')[0].length > 64) return '';
  return s;
}

// The scrambled id for an address: 32 characters, the same shape as every other player id.
export const emailId = async (env, email) => (await hmac(env.ID_SALT, 'email:' + email)).slice(0, 32);

const codeHash = (env, id, code) => hmac(env.SIGNING_KEY, 'code:' + id + ':' + code);
const sixDigits = (rnd = secureInt) => String(rnd(1000000)).padStart(6, '0');
const dayKey = t => '_day:' + t.toISOString().slice(0, 10);

// Make a code for this address if the limits allow. Returns {ok: true, code} or {ok: false, why, wait?}.
// why: 'wait' (asked again too soon), 'slow' (too many this hour), 'busy' (the whole site hit its day's cap).
export async function makeCode(env, id, t, rnd = secureInt) {
  const db = env.DB, now = Math.floor(t.getTime() / 1000);
  await ensureEmailTables(db);
  const row = await db.prepare('SELECT * FROM email_codes WHERE id = ?').bind(id).first();
  if (row && now - row.sent_at < RESEND_SECONDS) return { ok: false, why: 'wait', wait: RESEND_SECONDS - (now - row.sent_at) };
  const sameHour = row && now - row.window_start < 3600;
  if (sameHour && row.sends >= HOURLY_SENDS) return { ok: false, why: 'slow' };
  const cap = Number(env.MAIL_DAILY_CAP) > 0 ? Number(env.MAIL_DAILY_CAP) : DEFAULT_DAILY_CAP;
  const day = await db.prepare('SELECT sends FROM email_codes WHERE id = ?').bind(dayKey(t)).first();
  if (day && day.sends >= cap) return { ok: false, why: 'busy' };

  const code = sixDigits(rnd);
  await db.batch([
    db.prepare(`INSERT INTO email_codes (id, code_hash, expires_at, tries, sent_at, sends, window_start) VALUES (?, ?, ?, 0, ?, 1, ?)
      ON CONFLICT (id) DO UPDATE SET code_hash = excluded.code_hash, expires_at = excluded.expires_at, tries = 0, sent_at = excluded.sent_at,
        sends = CASE WHEN ? - window_start < 3600 THEN sends + 1 ELSE 1 END,
        window_start = CASE WHEN ? - window_start < 3600 THEN window_start ELSE excluded.window_start END`)
      .bind(id, await codeHash(env, id, code), now + CODE_MINUTES * 60, now, now, now, now),
    db.prepare(`INSERT INTO email_codes (id, sends) VALUES (?, 1) ON CONFLICT (id) DO UPDATE SET sends = sends + 1`).bind(dayKey(t)),
    // sweep: codes long expired and day counters from before yesterday
    db.prepare(`DELETE FROM email_codes WHERE (id NOT LIKE '\\_day:%' ESCAPE '\\' AND expires_at < ?) OR (id LIKE '\\_day:%' ESCAPE '\\' AND id < ?)`)
      .bind(now - 86400, dayKey(new Date(t.getTime() - 86400000))),
  ]);
  return { ok: true, code };
}

// A send that failed gives the try back, so a mail outage never locks anyone out.
export async function forgetCode(env, id) {
  await env.DB.prepare(`UPDATE email_codes SET code_hash = '', expires_at = 0, sent_at = 0, sends = MAX(0, sends - 1) WHERE id = ?`).bind(id).run();
}

// Check a code. Returns 'ok', 'wrong', 'expired' (none pending or too old), or 'locked' (too many wrong guesses).
export async function checkCode(env, id, code, t) {
  const db = env.DB, now = Math.floor(t.getTime() / 1000);
  await ensureEmailTables(db);
  const row = await db.prepare('SELECT * FROM email_codes WHERE id = ?').bind(id).first();
  if (!row || !row.code_hash || row.expires_at < now) return 'expired';
  if (row.tries >= MAX_TRIES) return 'locked';
  const clean = String(code || '').replace(/\D/g, '');
  if (clean.length !== 6 || !(await hmacVerify(env.SIGNING_KEY, 'code:' + id + ':' + clean, row.code_hash))) {
    const upd = await db.prepare('UPDATE email_codes SET tries = tries + 1 WHERE id = ? AND tries < ?').bind(id, MAX_TRIES).run();
    return row.tries + 1 >= MAX_TRIES || !(upd.meta && upd.meta.changes) ? 'locked' : 'wrong';
  }
  // used once: only the request that clears it wins, so the same code can't sign in twice at once
  const used = await db.prepare(`UPDATE email_codes SET code_hash = '', expires_at = 0 WHERE id = ? AND code_hash = ?`).bind(id, row.code_hash).run();
  return used.meta && used.meta.changes ? 'ok' : 'expired';
}

// The player an id stands for: itself if it is a player, else whoever its alias points at, else null.
export async function playerFor(db, id) {
  await ensureEmailTables(db);
  const own = await db.prepare('SELECT * FROM players WHERE id = ?').bind(id).first();
  if (own) return own;
  const a = await db.prepare('SELECT player_id FROM aliases WHERE alias = ?').bind(id).first();
  return a ? db.prepare('SELECT * FROM players WHERE id = ?').bind(a.player_id).first() : null;
}

// Point a second id at a player (never over an existing player or an existing alias).
export async function addAlias(db, alias, playerId, at) {
  if (!alias || alias === playerId) return;
  await ensureEmailTables(db);
  const taken = await db.prepare('SELECT 1 AS x FROM players WHERE id = ?').bind(alias).first();
  if (taken) return;
  await db.prepare('INSERT OR IGNORE INTO aliases (alias, player_id, created_at) VALUES (?, ?, ?)').bind(alias, playerId, at).run();
}
