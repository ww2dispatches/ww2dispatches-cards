// POST: the page has shown the promotion moment, so remember the rank announced. The server works out
// the rank itself from the pulls, so a page can never announce a rank the player hasn't reached.
import { json, fail } from '../_lib/util.js';
import { signedInPlayer } from '../_lib/player.js';
import { filledSlots, rankIndex, rankInfo } from '../_lib/rank.js';

export async function onRequestPost({ request, env }) {
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');
  const { results } = await env.DB.prepare('SELECT card_id, variant, finish FROM pulls WHERE player_id = ?').bind(player.id).all();
  const filled = filledSlots(results), i = rankIndex(filled);
  await env.DB.prepare('UPDATE players SET rank_seen = MAX(rank_seen, ?) WHERE id = ?').bind(i, player.id).run();
  return json({ rank: rankInfo(filled, Math.max(i, player.rank_seen || 0)) });
}
