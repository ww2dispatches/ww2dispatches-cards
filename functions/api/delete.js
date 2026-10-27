// POST /api/delete: Delete my dossier. Removes the player and every row about them right away,
// and signs them out. Serial numbers already issued stay used, so no one else's are renumbered.
import { json, fail } from '../_lib/util.js';
import { signedInPlayer } from '../_lib/player.js';
import { clearSessionCookie } from '../_lib/session.js';
import { ensureTables } from '../_lib/intercept.js';

export async function onRequestPost({ request, env }) {
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');
  const db = env.DB, id = player.id;
  await ensureTables(db);
  await db.batch([
    db.prepare('DELETE FROM intercept WHERE player_id = ?').bind(id),
    db.prepare('DELETE FROM intercept_seen WHERE player_id = ?').bind(id),
    db.prepare('DELETE FROM pulls WHERE player_id = ?').bind(id),
    db.prepare('DELETE FROM opened WHERE player_id = ?').bind(id),
    db.prepare('DELETE FROM months WHERE player_id = ?').bind(id),
    db.prepare('DELETE FROM intel_log WHERE player_id = ?').bind(id),
    db.prepare('DELETE FROM players WHERE id = ?').bind(id),
  ]);
  return json({ deleted: true }, 200, { 'set-cookie': clearSessionCookie() });
}
