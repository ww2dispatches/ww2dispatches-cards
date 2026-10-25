// Who is signed in. The home screen "state" request replaces this in build session 3.
import { json, fail } from '../_lib/util.js';
import { readSession } from '../_lib/session.js';
import { publicPlayer } from '../_lib/player.js';

export async function onRequestGet({ request, env }) {
  const playerId = await readSession(env, request);
  if (!playerId) return json({ player: null });
  const player = await env.DB.prepare('SELECT * FROM players WHERE id = ?').bind(playerId).first();
  if (!player) return json({ player: null });
  const counts = await env.DB.prepare('SELECT COUNT(*) AS n FROM pulls WHERE player_id = ?').bind(playerId).first();
  return json({ player: { ...publicPlayer(player), cards: counts.n } });
}
