// POST {ids?}: mark cards as turned. With no ids, every waiting card. Turning the last one
// unlocks the other envelopes.
import { json, fail } from '../_lib/util.js';
import { signedInPlayer } from '../_lib/player.js';

export async function onRequestPost({ request, env }) {
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');
  let body = {};
  try { body = (await request.json()) || {}; } catch {}
  const ids = Array.isArray(body.ids) ? body.ids.map(Number).filter(Number.isInteger).slice(0, 50) : null;

  if (ids && ids.length) {
    await env.DB.prepare(`UPDATE pulls SET turned = 1 WHERE player_id = ? AND turned = 0 AND id IN (${ids.map(() => '?').join(',')})`)
      .bind(player.id, ...ids).run();
  } else {
    await env.DB.prepare('UPDATE pulls SET turned = 1 WHERE player_id = ? AND turned = 0').bind(player.id).run();
  }
  const left = await env.DB.prepare('SELECT COUNT(*) AS n FROM pulls WHERE player_id = ? AND turned = 0').bind(player.id).first();
  return json({ waiting: left.n });
}
