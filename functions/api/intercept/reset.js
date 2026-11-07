// POST /api/intercept/reset: a tester's fresh start (7 Nov 2026). Brian asked to see the Code Room as a new
// player would, intro and first puzzle guide included. Testers only (flagged, or on the admin or
// TESTER_FILES list), with the preview flag on, like replay. It forgets today's puzzle, today's Code Room
// card claims, and the hard groups seen, so the next open starts at the intro with a fresh deal. Cards
// already picked stay in the dossier. Nothing here is reachable by players.
import { json, fail } from '../../_lib/util.js';
import { now } from '../../_lib/catalog.js';
import { signedInPlayer } from '../../_lib/player.js';
import { isTester } from '../../_lib/admins.js';
import { interceptOpen, ensureTables, puzzleDay } from '../../_lib/intercept.js';

export async function onRequestPost({ request, env }) {
  const t = now(env, request);
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');
  if (!interceptOpen(env, request, player) || !isTester(env, player) || request.headers.get('x-intercept-preview') !== '1') return fail(404, 'not found');
  const db = env.DB;
  await ensureTables(db);
  const day = puzzleDay(t);
  await db.batch([
    db.prepare('DELETE FROM intercept WHERE player_id = ? AND day = ?').bind(player.id, day),
    db.prepare('DELETE FROM intercept_seen WHERE player_id = ?').bind(player.id),
    db.prepare("DELETE FROM opened WHERE player_id = ? AND (slot_key = ? OR slot_key LIKE ?)").bind(player.id, 'i:' + day, 'ip:' + day + ':%'),
  ]);
  return json({ ok: true, day });
}
