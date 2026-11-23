// POST /api/intercept/claim {day, index}: a solved puzzle lets the player pick any one of the 12 cards,
// owned or not. A perfect solve is Silver or better; otherwise the normal finish odds. A finish already
// held converts to Intel like any duplicate (Top Secret never converts). Flash cards can't be claimed.
// The card arrives waiting to be turned, and the page reveals it with the normal turn.
import { json, fail } from '../../_lib/util.js';
import { now, findCard, filmReleased } from '../../_lib/catalog.js';
import { signedInPlayer, publicPlayer } from '../../_lib/player.js';
import { signPending, withCard } from '../../_lib/pulls.js';
import { rollFinish, rollFinishNoCopper } from '../../_lib/odds.js';
import { DUPLICATE_INTEL } from '../../_lib/intel.js';
import { interceptOpen, ensureTables, puzzleDay, todayRow, publicPuzzle } from '../../_lib/intercept.js';

export async function onRequestPost({ request, env }) {
  const t = now(env, request);
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');
  if (!interceptOpen(env, request, player)) return fail(403, 'coming soon');
  let body;
  try { body = await request.json(); } catch { return fail(400, 'bad request'); }
  const db = env.DB;
  await ensureTables(db);
  const day = puzzleDay(t);
  if (body && body.day && body.day !== day) return fail(409, 'expired');
  const row = await todayRow(db, player.id, day);
  if (!row || row.status !== 'solved') return fail(409, 'not solved');
  if (row.claimed) return fail(409, 'already claimed');

  const grid = JSON.parse(row.grid), i = Number(body && body.index);
  if (!Number.isInteger(i) || !grid.cards[i]) return fail(400, 'bad pick');
  const card = findCard(grid.cards[i].id, t);
  if (!card) return fail(409, 'not available');
  if (card.flash) return fail(400, 'not offered'); // a Flash card in the grid can't be claimed (TO CONFIRM 1)
  // A card dealt as a Living Card shows its still frame in the grid and comes as the living variant.
  const variant = grid.cards[i].v === 'living' && filmReleased(card, t) ? 'living' : 'still';
  const perfect = row.mistakes === 0;
  const finish = perfect ? rollFinishNoCopper(variant) : rollFinish(variant);
  const held = await db.prepare('SELECT 1 FROM pulls WHERE player_id = ? AND card_id = ? AND variant = ? AND finish = ?').bind(player.id, card.id, variant, finish).first();
  const dup = held ? (DUPLICATE_INTEL[finish] || 0) : 0;

  const pid = player.id, key = 'i:' + day, at = t.toISOString();
  const mine = 'EXISTS (SELECT 1 FROM opened WHERE player_id = ?1 AND slot_key = ?2)';
  const claimed = JSON.stringify({ idx: i, card: card.id, variant, finish });
  const stmts = [
    // The reroll guard: one claim per player per day, enforced by the opened table's key.
    db.prepare('INSERT INTO opened (player_id, slot_key, opened_at) VALUES (?, ?, ?)').bind(pid, key, at),
    db.prepare(`UPDATE intercept SET claimed = ?2 WHERE player_id = ?1 AND day = ?3 AND claimed IS NULL AND status = 'solved'`).bind(pid, claimed, day),
  ];
  const serialled = finish === 'topsecret';
  if (serialled) stmts.push(db.prepare(`INSERT INTO serials (card_id, variant, last) SELECT ?3, ?4, 1 WHERE ${mine} ON CONFLICT (card_id, variant) DO UPDATE SET last = last + 1`).bind(pid, key, card.id, variant));
  const serial = serialled ? '(SELECT last FROM serials WHERE card_id = ?3 AND variant = ?4)' : 'NULL';
  stmts.push(db.prepare(`INSERT INTO pulls (player_id, card_id, variant, finish, serial, slot_key, pulled_at, signature, turned, intel)
    SELECT ?1, ?3, ?4, ?5, ${serial}, ?2, ?6, '', 0, ?7 WHERE ${mine}`).bind(pid, key, card.id, variant, finish, at, dup));
  if (dup) {
    stmts.push(db.prepare(`UPDATE players SET intel = intel + ?3 WHERE id = ?1 AND ${mine}`).bind(pid, key, dup));
    stmts.push(db.prepare(`INSERT INTO intel_log (player_id, at, delta, reason, slot_key, card_id, variant, finish) SELECT ?1, ?3, ?4, 'duplicate', ?2, ?5, ?6, ?7 WHERE ${mine}`)
      .bind(pid, key, at, dup, card.id, variant, finish));
  }
  try { await db.batch(stmts); }
  catch (err) {
    if (String(err && err.message).includes('UNIQUE')) return fail(409, 'already claimed');
    throw err;
  }
  await signPending(env, pid);
  const [pulls, fresh, prow] = await db.batch([
    db.prepare('SELECT * FROM pulls WHERE player_id = ? AND slot_key = ? ORDER BY id').bind(pid, key),
    db.prepare('SELECT * FROM players WHERE id = ?').bind(pid),
    db.prepare('SELECT * FROM intercept WHERE player_id = ? AND day = ?').bind(pid, day),
  ]);
  return json({
    pulls: pulls.results.map(r => withCard(r, t)),
    intel: { gained: dup, earned: dup ? [{ reason: 'duplicate', delta: dup, variant, finish }] : [], balance: fresh.results[0].intel },
    player: publicPlayer(fresh.results[0], t),
    puzzle: publicPuzzle(prow.results[0], t),
  });
}
