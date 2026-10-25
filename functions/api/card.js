// GET /api/card?id=...: one posted card with its story, credits, sources, links, and film.
// An unknown card and one that hasn't posted yet get the same answer, so nothing leaks ahead.
import { json, fail } from '../_lib/util.js';
import { now, findCard, detail } from '../_lib/catalog.js';

export async function onRequestGet({ request, env }) {
  const t = now(env, request);
  const card = findCard(new URL(request.url).searchParams.get('id') || '', t);
  if (!card) return fail(404, 'no such card');
  return json({ card: detail(card, t) });
}
