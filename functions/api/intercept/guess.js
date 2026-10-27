// POST /api/intercept/guess {day, pick: [three card positions]}: file three cards.
// Right: the group locks with its link. Wrong: a mistake. The same three again: "already tried", no
// mistake. No near miss hint, ever. When the puzzle ends, the Intel is paid in the same batch.
import { json, fail } from '../../_lib/util.js';
import { now } from '../../_lib/catalog.js';
import { signedInPlayer } from '../../_lib/player.js';
import { interceptOpen, ensureTables, puzzleDay, todayRow, publicPuzzle, applyGuess, scoreOf, bonusOf, PLAY_INTEL, token } from '../../_lib/intercept.js';

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
  if (body && body.day && body.day !== day) return fail(409, 'expired'); // the file closed at midnight Eastern
  const row = await todayRow(db, player.id, day);
  if (!row) return fail(409, 'not started');
  if (row.status !== 'play') return json({ result: 'finished', puzzle: publicPuzzle(row, t) });

  const state = { grid: JSON.parse(row.grid), found: JSON.parse(row.found), tries: JSON.parse(row.tries), mistakes: row.mistakes, status: row.status };
  const r = applyGuess(state, body && body.pick);
  if (r.error) return fail(400, r.error);
  if (r.result === 'tried') return json({ result: 'tried', puzzle: publicPuzzle(row, t) });

  const next = r.state, done = next.status !== 'play';
  const score = done ? scoreOf(next.found.length, next.mistakes) : null;
  const intel = done ? PLAY_INTEL + bonusOf(next.status, score) : null;
  const fin = done ? token() : null, at = t.toISOString();
  const paid = 'EXISTS (SELECT 1 FROM intercept WHERE player_id = ?1 AND day = ?2 AND fin = ?3)';
  const stmts = [
    // Compare and set on the move count, so two guesses fired at once can't both land.
    db.prepare(`UPDATE intercept SET found = ?, tries = ?, mistakes = ?, status = ?, score = ?, intel = ?, fin = ?, moves = moves + 1
      WHERE player_id = ? AND day = ? AND moves = ? AND status = 'play'`)
      .bind(JSON.stringify(next.found), JSON.stringify(next.tries), next.mistakes, next.status, score, intel, fin, player.id, day, row.moves),
  ];
  if (done) {
    stmts.push(db.prepare(`UPDATE players SET intel = intel + ?4 WHERE id = ?1 AND ${paid}`).bind(player.id, day, fin, intel));
    stmts.push(db.prepare(`INSERT INTO intel_log (player_id, at, delta, reason, slot_key) SELECT ?1, ?4, ?5, 'intercept', ?6 WHERE ${paid}`)
      .bind(player.id, day, fin, at, intel, 'i:' + day));
  }
  const results = await db.batch(stmts);
  const fresh = await todayRow(db, player.id, day);
  if (!(results[0].meta && results[0].meta.changes)) return json({ result: 'stale', puzzle: publicPuzzle(fresh, t) }); // another guess landed first
  const out = { result: r.result, puzzle: publicPuzzle(fresh, t) };
  if (done) out.intel = { gained: intel, play: PLAY_INTEL, bonus: intel - PLAY_INTEL };
  return json(out);
}
