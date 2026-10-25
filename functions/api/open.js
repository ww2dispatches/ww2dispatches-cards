// POST {slot}: open an envelope. slot is a daily key ("d:..."), a commemorative key ("c:..."),
// or "priority". The cards are decided, numbered, signed, and saved here, before the player
// sees them; turning them over afterwards is only looking.
//
// Guards: the envelope must be out now; each envelope opens once per player (the opened table's
// key, so a second try fails as a whole); nothing may be waiting to be turned; a priority
// envelope needs one waiting. Everything is written in one database batch, which either all
// happens or none of it does.
import { json, fail } from '../_lib/util.js';
import { now } from '../_lib/catalog.js';
import { signedInPlayer, publicPlayer } from '../_lib/player.js';
import { resolveEnvelope, drawCards } from '../_lib/envelopes.js';
import { streakAfterOpen } from '../_lib/streak.js';
import { signPending, withCard } from '../_lib/pulls.js';

const FINISHES = new Set(['copper', 'silver', 'gold', 'topsecret']);

export async function onRequestPost({ request, env }) {
  const t = now(env, request);
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');

  let body;
  try { body = await request.json(); } catch { return fail(400, 'bad request'); }
  const envl = resolveEnvelope(body && body.slot, t, player);
  if (!envl) return fail(409, 'not available');

  const db = env.DB;
  const waiting = await db.prepare('SELECT COUNT(*) AS n FROM pulls WHERE player_id = ? AND turned = 0').bind(player.id).first();
  if (waiting.n > 0) return fail(409, 'cards waiting');
  if (envl.kind !== 'priority') {
    const seen = await db.prepare('SELECT 1 FROM opened WHERE player_id = ? AND slot_key = ?').bind(player.id, envl.key).first();
    if (seen) return fail(409, 'already opened');
  }

  const picks = drawCards(envl, t);
  if (!picks.length) return fail(409, 'not available');

  // Test copies only: force a finish to check serials without waiting for luck.
  const forced = env.ALLOW_FAKE_NOW === '1' && request.headers.get('x-declass-force-finish');
  if (forced && FINISHES.has(forced)) picks.forEach(p => { p.finish = forced; });

  const pid = player.id, key = envl.key, at = t.toISOString();
  const mine = 'EXISTS (SELECT 1 FROM opened WHERE player_id = ?1 AND slot_key = ?2)';
  const stmts = [];

  if (envl.kind === 'priority') {
    stmts.push(db.prepare('INSERT INTO opened (player_id, slot_key, opened_at) SELECT ?1, ?2, ?3 WHERE (SELECT priority_waiting FROM players WHERE id = ?1) > 0').bind(pid, key, at));
    stmts.push(db.prepare(`UPDATE players SET priority_waiting = priority_waiting - 1 WHERE id = ?1 AND ${mine}`).bind(pid, key));
  } else {
    stmts.push(db.prepare('INSERT INTO opened (player_id, slot_key, opened_at) VALUES (?1, ?2, ?3)').bind(pid, key, at));
  }

  const pullIdx = [];
  for (const p of picks) {
    if (p.finish === 'topsecret') {
      stmts.push(db.prepare(`INSERT INTO serials (card_id, variant, last) SELECT ?3, ?4, 1 WHERE ${mine} ON CONFLICT (card_id, variant) DO UPDATE SET last = last + 1`).bind(pid, key, p.card.id, p.variant));
    }
    const serial = p.finish === 'topsecret' ? '(SELECT last FROM serials WHERE card_id = ?3 AND variant = ?4)' : 'NULL';
    pullIdx.push(stmts.length);
    stmts.push(db.prepare(
      `INSERT INTO pulls (player_id, card_id, variant, finish, serial, slot_key, pulled_at, signature, turned)
       SELECT ?1, ?3, ?4, ?5, ${serial}, ?2, ?6, '', 0 WHERE ${mine} RETURNING *`
    ).bind(pid, key, p.card.id, p.variant, p.finish, at));
  }

  // The streak counts daily envelopes only. The last_day_played check means two requests racing
  // on the same day can't both count it.
  const s = envl.kind === 'daily' ? streakAfterOpen(player, t) : null;
  if (s) {
    stmts.push(db.prepare(`UPDATE players SET streak = ?3, last_day_played = ?4, priority_waiting = priority_waiting + ?5
      WHERE id = ?1 AND last_day_played IS ?6 AND ${mine}`).bind(pid, key, s.streak, s.day, s.earned, player.last_day_played));
  }

  let results;
  try {
    results = await db.batch(stmts);
  } catch (err) {
    if (String(err && err.message).includes('UNIQUE')) return fail(409, 'already opened');
    throw err;
  }
  const rows = pullIdx.flatMap(i => results[i].results || []);
  if (!rows.length) return fail(409, 'not available');

  await signPending(env, pid);
  const signed = await db.prepare('SELECT * FROM pulls WHERE player_id = ? AND slot_key = ? ORDER BY id').bind(pid, key).all();
  const fresh = await db.prepare('SELECT * FROM players WHERE id = ?').bind(pid).first();

  return json({
    envelope: { key, kind: envl.kind, deep: Boolean(envl.deep) },
    pulls: signed.results.map(r => withCard(r, t)),
    earnedPriority: Boolean(s && s.earned && fresh.last_day_played === s.day && fresh.streak === s.streak),
    player: publicPlayer(fresh, t),
  });
}
