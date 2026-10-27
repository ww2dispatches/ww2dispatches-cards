// GET /api/intercept: today's puzzle for the signed in player, without dealing one.
// status: soon (not open yet), signin, new (not dealt yet), play, solved, or failed.
import { json } from '../../_lib/util.js';
import { now } from '../../_lib/catalog.js';
import { signedInPlayer } from '../../_lib/player.js';
import { interceptOpen, ensureTables, puzzleDay, closesAt, todayRow, publicPuzzle } from '../../_lib/intercept.js';

export async function onRequestGet({ request, env }) {
  const t = now(env, request);
  const player = await signedInPlayer(env, request);
  if (!interceptOpen(env, request, player)) return json({ status: 'soon' });
  const day = puzzleDay(t), closes = closesAt(day);
  if (!player) return json({ status: 'signin', day, closes });
  await ensureTables(env.DB);
  const row = await todayRow(env.DB, player.id, day);
  if (!row) return json({ status: 'new', day, closes });
  return json({ status: row.status, day, closes, puzzle: publicPuzzle(row, t) });
}
