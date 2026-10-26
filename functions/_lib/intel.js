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
