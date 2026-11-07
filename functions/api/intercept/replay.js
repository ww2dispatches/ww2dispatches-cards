// POST /api/intercept/replay: a tester's practice round (7 Nov 2026). Brian asked to keep playing while
// testing, not once a day. Testers only (flagged, or on the admin or TESTER_FILES list), with the preview
// flag on. Today's row is replaced by a freshly dealt grid marked as practice: it pays no Intel, its card
// pick never rolls Top Secret (so no worldwide serial is used) and has its own claim key, and its hard
// groups are not recorded for the 90 day rule. The real day's Intel and card, if already paid, stay paid.
import { json, fail } from '../../_lib/util.js';
import { now } from '../../_lib/catalog.js';
import { signedInPlayer } from '../../_lib/player.js';
import { isTester } from '../../_lib/admins.js';
import { interceptOpen, ensureTables, puzzleDay, todayRow, publicPuzzle, dealContext, dealGrid, token } from '../../_lib/intercept.js';

export async function onRequestPost({ request, env }) {
  const t = now(env, request);
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');
  if (!interceptOpen(env, request, player) || !isTester(env, player) || request.headers.get('x-intercept-preview') !== '1') return fail(404, 'not found');
  const db = env.DB;
  await ensureTables(db);
  const day = puzzleDay(t);
  const row = await todayRow(db, player.id, day);
  let n = 1;
  if (row) { try { n = (JSON.parse(row.grid).practice || 0) + 1; } catch (e) {} }
  let grid = null;
  for (let tries = 0; tries < 3 && !grid; tries++) grid = dealGrid(t, await dealContext(db, player.id, t));
  if (!grid) return fail(409, 'no grid');
  grid.practice = n;
  await db.batch([
    db.prepare('DELETE FROM intercept WHERE player_id = ? AND day = ?').bind(player.id, day),
    db.prepare('INSERT INTO intercept (player_id, day, dealt_at, tok, grid) VALUES (?, ?, ?, ?, ?)').bind(player.id, day, t.toISOString(), token(), JSON.stringify(grid)),
  ]);
  return json({ puzzle: publicPuzzle(await todayRow(db, player.id, day), t) });
}
