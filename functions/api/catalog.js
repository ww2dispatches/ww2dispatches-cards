// GET /api/catalog: every card that has posted, with what the dossier grid needs.
// The full text of one card comes from /api/card?id=...
import { json } from '../_lib/util.js';
import { now, postedCards, summary } from '../_lib/catalog.js';

export async function onRequestGet({ request, env }) {
  const t = now(env, request);
  return json({ now: t.toISOString(), cards: postedCards(t).map(c => summary(c, t)) });
}
