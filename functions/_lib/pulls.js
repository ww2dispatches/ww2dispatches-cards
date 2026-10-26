// Pull signatures and what the page may see about a pull.
import { hmac } from './util.js';
import { findCard, summary } from './catalog.js';
import { fileNumber } from './fileno.js';

const fields = (r, playerId) =>
  ['pull', r.id, playerId, r.card_id, r.variant, r.finish, r.serial ?? '', r.slot_key, r.pulled_at].join('|');

export const signPull = (env, r, playerId) => hmac(env.SIGNING_KEY, fields(r, playerId));

// Sign any of this player's pulls still missing a signature (the second step of an open; also
// repairs one if a request was cut off between the two steps).
export async function signPending(env, playerId) {
  const { results } = await env.DB.prepare("SELECT * FROM pulls WHERE player_id = ? AND signature = ''").bind(playerId).all();
  if (!results.length) return 0;
  const stmt = env.DB.prepare('UPDATE pulls SET signature = ? WHERE id = ?');
  await env.DB.batch(await Promise.all(results.map(async r => stmt.bind(await signPull(env, r, playerId), r.id))));
  return results.length;
}

export function publicPull(r) {
  return {
    id: r.id, card: r.card_id, variant: r.variant, finish: r.finish, serial: r.serial ?? null,
    slot: r.slot_key, at: r.pulled_at, turned: Boolean(r.turned), signed: Boolean(r.signature), file: fileNumber(r), intel: r.intel || 0,
  };
}

// A pull with the card's grid details attached (null if the card ever left the catalog).
export function withCard(r, t) {
  const c = findCard(r.card_id, t);
  return { ...publicPull(r), cardInfo: c ? summary(c, t) : null };
}
