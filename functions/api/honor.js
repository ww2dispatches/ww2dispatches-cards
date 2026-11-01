// POST {keys}: the page has shown a monthly file's stamp ceremony, so remember it for every device the player
// uses (1 Nov 2026). Stored as "h:" rows in the opened table, so no new table is needed; only month keys
// ("m:2026-10") are accepted, and a key already stored is ignored.
import { json, fail } from '../_lib/util.js';
import { signedInPlayer } from '../_lib/player.js';

export async function onRequestPost({ request, env }) {
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');
  let body;
  try { body = await request.json(); } catch { return fail(400, 'bad request'); }
  const keys = [...new Set((Array.isArray(body && body.keys) ? body.keys : []).filter(k => typeof k === 'string' && /^m:\d{4}-\d{2}$/.test(k)))].slice(0, 24);
  if (!keys.length) return json({ ok: true });
  const at = new Date().toISOString();
  await env.DB.batch(keys.map(k => env.DB.prepare('INSERT OR IGNORE INTO opened (player_id, slot_key, opened_at) VALUES (?, ?, ?)').bind(player.id, 'h:' + k, at)));
  return json({ ok: true });
}
