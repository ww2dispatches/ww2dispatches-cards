// Intel, the one currency (decided 25 Oct 2026, Envelope doc "Intel and requests").
// Earned: 5 for every envelope opened (daily, Sunday deep archive, priority, commemorative), plus
// duplicates converted at the reveal. Spent: requesting any posted card in any finish.
import { gameDay, zonedTime } from './time.js';

export const ENVELOPE_INTEL = 5;
// A duplicate converts to Intel automatically. The first copy of each slot is protected and never
// converts. Top Secret copies are never converted: each carries its own worldwide serial (and a Flash
// card is always Top Secret), so they stay in the dossier as extra copies.
export const DUPLICATE_INTEL = { copper: 1, silver: 4, gold: 15 };
export const PRICES = { copper: 20, silver: 75, gold: 250, topsecret: 750 };
export const FLASH_PRICE = 750;
export const LIVING_MULTIPLIER = 1.5;

const livingPrice = base => Math.round(base * LIVING_MULTIPLIER); // 112.5 rounds to 113

// What a request costs, or null if that card can't come in that variant and finish.
export function requestPrice(card, variant, finish) {
  if (card.flash) return variant === 'still' && finish === 'topsecret' ? FLASH_PRICE : null;
  const base = PRICES[finish];
  if (!base || (variant !== 'still' && variant !== 'living')) return null;
  return variant === 'living' ? livingPrice(base) : base;
}

export const priceTable = () => ({
  still: { ...PRICES },
  living: Object.fromEntries(Object.entries(PRICES).map(([k, v]) => [k, livingPrice(v)])),
  flash: FLASH_PRICE,
});

// The balance, what was earned today (Eastern game day), and the most recent entries.
export async function intelSummary(db, player, t) {
  const dayStart = zonedTime(gameDay(t), '00:00').toISOString();
  const [recent, today] = await db.batch([
    db.prepare('SELECT at, delta, reason, card_id, variant, finish FROM intel_log WHERE player_id = ? ORDER BY id DESC LIMIT 15').bind(player.id),
    db.prepare('SELECT COALESCE(SUM(delta), 0) AS n FROM intel_log WHERE player_id = ? AND delta > 0 AND at >= ?').bind(player.id, dayStart),
  ]);
  return {
    balance: player.intel || 0,
    today: today.results[0].n,
    recent: recent.results.map(r => ({ at: r.at, delta: r.delta, reason: r.reason, card: r.card_id, variant: r.variant, finish: r.finish })),
  };
}

// Duplicates pulled before Intel existed (25 Oct 2026) were never converted. Convert them once, the
// same way the reveal would have: the first copy of each slot stays, later Copper, Silver, and Gold
// copies turn into Intel; Top Secret never converts. Starter pack copies are left alone (the starter
// earns nothing). New pulls are always converted at the reveal, so after the first run this finds
// nothing. One batch logs, credits, and marks the rows together, so nothing is lost halfway, and a
// second state request at the same moment finds the rows already marked. Returns the Intel added.
const LEGACY = `player_id = ?1 AND intel = 0 AND finish IN ('copper', 'silver', 'gold') AND slot_key <> 's:starter'
  AND EXISTS (SELECT 1 FROM pulls p2 WHERE p2.player_id = pulls.player_id AND p2.card_id = pulls.card_id
              AND p2.variant = pulls.variant AND p2.finish = pulls.finish AND p2.id < pulls.id)`;
const VALUE = `CASE finish WHEN 'copper' THEN ${DUPLICATE_INTEL.copper} WHEN 'silver' THEN ${DUPLICATE_INTEL.silver} ELSE ${DUPLICATE_INTEL.gold} END`;
export async function convertLegacyDuplicates(db, playerId, t) {
  const found = await db.prepare(`SELECT COUNT(*) AS n FROM pulls WHERE ${LEGACY}`).bind(playerId).first();
  if (!found || !found.n) return 0;
  const at = t.toISOString();
  const [, credit] = await db.batch([
    db.prepare(`INSERT INTO intel_log (player_id, at, delta, reason, slot_key, card_id, variant, finish)
      SELECT player_id, ?2, ${VALUE}, 'duplicate', slot_key, card_id, variant, finish FROM pulls WHERE ${LEGACY}`).bind(playerId, at),
    db.prepare(`UPDATE players SET intel = intel + COALESCE((SELECT SUM(${VALUE}) FROM pulls WHERE ${LEGACY}), 0) WHERE id = ?1
      RETURNING COALESCE((SELECT SUM(${VALUE}) FROM pulls WHERE ${LEGACY}), 0) AS added`).bind(playerId),
    db.prepare(`UPDATE pulls SET intel = ${VALUE} WHERE ${LEGACY}`).bind(playerId),
  ]);
  return (credit.results && credit.results[0] && credit.results[0].added) || 0;
}
