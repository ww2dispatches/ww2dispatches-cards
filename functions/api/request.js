// POST {card, variant, finish}: request a card with Intel (decided 25 Oct 2026, Envelope doc
// "Intel and requests"). Any card ever posted, in any finish, Top Secret and Flash included; never
// one of today's cards; only a slot the player doesn't hold yet. No limit, no refunds.
//
// The card comes in a small Requisition envelope ("q:" key) that the page opens with the normal tap and
// reveal. A requested Top Secret takes the next worldwide serial, the same as a pulled one. Everything is
// written in one batch: the Intel is only spent if the balance covers it, checked inside the batch.
import { json, fail } from '../_lib/util.js';
import { now, findCard, filmReleased, isTodayCard } from '../_lib/catalog.js';
import { signedInPlayer, publicPlayer } from '../_lib/player.js';
import { signPending, withCard } from '../_lib/pulls.js';
import { requestPrice } from '../_lib/intel.js';

export async function onRequestPost({ request, env }) {
  const t = now(env, request);
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');

  let body;
  try { body = await request.json(); } catch { return fail(400, 'bad request'); }
  const card = findCard(body && body.card, t);
  if (!card) return fail(404, 'no such card');
  const variant = body.variant === 'living' ? 'living' : 'still';
  const finish = String(body.finish || '');
  const price = requestPrice(card, variant, finish);
  if (!price) return fail(400, 'not offered');
  if (variant === 'living' && !filmReleased(card, t)) return fail(400, 'not offered');
  if (isTodayCard(card, t)) return fail(409, 'today');

  const db = env.DB, pid = player.id, at = t.toISOString();
  const waiting = await db.prepare('SELECT COUNT(*) AS n FROM pulls WHERE player_id = ? AND turned = 0').bind(pid).first();
  if (waiting.n > 0) return fail(409, 'cards waiting');
  const have = await db.prepare('SELECT 1 FROM pulls WHERE player_id = ? AND card_id = ? AND variant = ? AND finish = ?').bind(pid, card.id, variant, finish).first();
  if (have) return fail(409, 'already held');
  if ((player.intel || 0) < price) return fail(402, 'not enough intel');

  const rand = new Uint8Array(9); crypto.getRandomValues(rand);
  const key = 'q:' + [...rand].map(b => b.toString(16).padStart(2, '0')).join('');
  const mine = 'EXISTS (SELECT 1 FROM opened WHERE player_id = ?1 AND slot_key = ?2)';
  const serialled = finish === 'topsecret' && !card.flash; // Flash cards carry no worldwide serial
  const stmts = [
    // Balance, waiting lock, and already held are all rechecked inside the batch, so a double tap or two
    // requests at once can never charge twice or skip the lock (bug sweep, 26 Oct 2026).
    db.prepare(`INSERT INTO opened (player_id, slot_key, opened_at) SELECT ?1, ?2, ?3
      WHERE (SELECT intel FROM players WHERE id = ?1) >= ?4
        AND NOT EXISTS (SELECT 1 FROM pulls WHERE player_id = ?1 AND turned = 0)
        AND NOT EXISTS (SELECT 1 FROM pulls WHERE player_id = ?1 AND card_id = ?5 AND variant = ?6 AND finish = ?7)`).bind(pid, key, at, price, card.id, variant, finish),
    db.prepare(`UPDATE players SET intel = intel - ?3 WHERE id = ?1 AND ${mine}`).bind(pid, key, price),
  ];
  if (serialled) {
    stmts.push(db.prepare(`INSERT INTO serials (card_id, variant, last) SELECT ?3, ?4, 1 WHERE ${mine} ON CONFLICT (card_id, variant) DO UPDATE SET last = last + 1`).bind(pid, key, card.id, variant));
  }
  const serial = serialled ? '(SELECT last FROM serials WHERE card_id = ?3 AND variant = ?4)' : 'NULL';
  const pullAt = stmts.length;
  stmts.push(db.prepare(
    `INSERT INTO pulls (player_id, card_id, variant, finish, serial, slot_key, pulled_at, signature, turned, intel)
     SELECT ?1, ?3, ?4, ?5, ${serial}, ?2, ?6, '', 0, 0 WHERE ${mine} RETURNING *`
  ).bind(pid, key, card.id, variant, finish, at));
  stmts.push(db.prepare(`INSERT INTO intel_log (player_id, at, delta, reason, slot_key, card_id, variant, finish) SELECT ?1, ?3, ?4, 'request', ?2, ?5, ?6, ?7 WHERE ${mine}`)
    .bind(pid, key, at, -price, card.id, variant, finish));

  const results = await db.batch(stmts);
  if (!(results[pullAt].results || []).length) return fail(402, 'not enough intel');

  await signPending(env, pid);
  const signed = await db.prepare('SELECT * FROM pulls WHERE player_id = ? AND slot_key = ?').bind(pid, key).all();
  const fresh = await db.prepare('SELECT * FROM players WHERE id = ?').bind(pid).first();
  return json({
    envelope: { key, kind: 'request' },
    pulls: signed.results.map(r => withCard(r, t)),
    price,
    player: publicPlayer(fresh, t),
  });
}
