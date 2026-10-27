// POST /api/intercept/start: deal today's grid, or return the one already dealt. Once dealt, the grid is
// saved, so closing the page and coming back can never reroll it (the same idea as the envelope guard).
import { json, fail } from '../../_lib/util.js';
import { now } from '../../_lib/catalog.js';
import { signedInPlayer } from '../../_lib/player.js';
import { interceptOpen, ensureTables, puzzleDay, todayRow, publicPuzzle, dealContext, dealGrid, token, cleanupCutoff } from '../../_lib/intercept.js';

export async function onRequestPost({ request, env }) {
  const t = now(env, request);
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');
  if (!interceptOpen(env, request, player)) return fail(403, 'coming soon');
  const db = env.DB;
  await ensureTables(db);
  const day = puzzleDay(t);
  let row = await todayRow(db, player.id, day);
  if (row) return json({ puzzle: publicPuzzle(row, t) });

  const grid = dealGrid(t, await dealContext(db, player.id, t));
  if (!grid) return fail(409, 'no grid'); // rare: no fair grid within the try budget; the page offers a retry
  const tok = token();
  const hard = grid.groups.filter(g => g.d === 'hard').map(g => g.id);
  const mine = 'EXISTS (SELECT 1 FROM intercept WHERE player_id = ?1 AND day = ?2 AND tok = ?3)';
  await db.batch([
    // Two opens at once: the first insert wins and both answers show that grid.
    db.prepare('INSERT OR IGNORE INTO intercept (player_id, day, dealt_at, tok, grid) VALUES (?1, ?2, ?4, ?3, ?5)').bind(player.id, day, tok, t.toISOString(), JSON.stringify(grid)),
    // Hard groups seen, kept for the 90 day no repeat rule (only for the grid that was actually saved).
    ...hard.map(id => db.prepare(`INSERT INTO intercept_seen (player_id, group_id, last_day) SELECT ?1, ?4, ?2 WHERE ${mine}
      ON CONFLICT (player_id, group_id) DO UPDATE SET last_day = excluded.last_day`).bind(player.id, day, tok, id)),
    // Puzzle rows are kept 90 days (the list of hard groups seen is kept).
    db.prepare('DELETE FROM intercept WHERE day < ?').bind(cleanupCutoff(t)),
  ]);
  row = await todayRow(db, player.id, day);
  return json({ puzzle: publicPuzzle(row, t) });
}
