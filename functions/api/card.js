// GET /api/card?id=...: one posted card with its story, credits, sources, links, and film, plus its
// Declassified file for a player holding it in Gold or better.
// An unknown card and one that hasn't posted yet get the same answer, so nothing leaks ahead.
import { json, fail } from '../_lib/util.js';
import { now, findCard, detail, opensFile } from '../_lib/catalog.js';
import { signedInPlayer } from '../_lib/player.js';

export async function onRequestGet({ request, env }) {
  const t = now(env, request);
  const card = findCard(new URL(request.url).searchParams.get('id') || '', t);
  if (!card) return fail(404, 'no such card');
  const player = card.dfile ? await signedInPlayer(env, request) : null;
  return json({ card: detail(card, t, await opensFile(env.DB, player && player.id, card.id)) });
}
