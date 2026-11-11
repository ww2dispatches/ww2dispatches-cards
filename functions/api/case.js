// POST /api/case: save the Display Case. Body: { callA, callB, slots: [six of null or {card, variant, finish}] }.
// Refuses a word not on the approved lists, a blocked pair, a slot the player doesn't hold (card, variant, and
// finish must all be in their pulls), the same card twice, and anything that isn't six slots.
import { json, fail } from '../_lib/util.js';
import { signedInPlayer } from '../_lib/player.js';
import { checkCase, saveCase } from '../_lib/displaycase.js';

export async function onRequestPost({ request, env }) {
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');
  let body;
  try { body = await request.json(); } catch { return fail(400, 'bad request'); }
  const { results } = await env.DB.prepare('SELECT card_id, variant, finish FROM pulls WHERE player_id = ?').bind(player.id).all();
  const err = checkCase(body, results);
  if (err) return fail(400, err);
  return json({ case: await saveCase(env.DB, player.id, body) });
}
