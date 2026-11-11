// Display Case (designed 10 Nov 2026, Display Case doc): six slots the player fills from cards they hold,
// and an optional call sign from two word lists. Picture only: nothing here is ever shown to anyone else.
// One row per player, created on first use like the tally and Intercept tables (also migrations/0005).
import { callSignOk } from './callsigns.js';

export const CASE_SCHEMA = [
  `CREATE TABLE IF NOT EXISTS display_case (player TEXT PRIMARY KEY, call_a TEXT, call_b TEXT, slots TEXT NOT NULL DEFAULT '[]', updated_at TEXT NOT NULL)`,
];
let ready = null;
export function ensureCase(db) {
  if (!ready) ready = db.batch(CASE_SCHEMA.map(s => db.prepare(s))).catch(err => { ready = null; throw err; });
  return ready;
}

export const SLOTS = 6;
const VARIANTS = new Set(['still', 'living']);
const FINISHES = new Set(['copper', 'silver', 'gold', 'topsecret']);
const held = pulls => new Set(pulls.map(r => `${r.card_id}|${r.variant}|${r.finish}`));

// A stored or sent slot list, cleaned: six entries, each null or {card, variant, finish}.
// keep = the player's pull rows; a slot they no longer hold reads as empty.
function cleanSlots(raw, pulls) {
  const have = held(pulls), out = [];
  for (let i = 0; i < SLOTS; i++) {
    const s = Array.isArray(raw) ? raw[i] : null;
    out.push(s && have.has(`${s.card}|${s.variant}|${s.finish}`) ? { card: s.card, variant: s.variant, finish: s.finish } : null);
  }
  return out;
}

// What state sends: the call sign (null if never chosen, or if a word has since been pulled) and the slots.
export async function readCase(db, playerId, pulls) {
  await ensureCase(db);
  const row = await db.prepare('SELECT * FROM display_case WHERE player = ?').bind(playerId).first();
  let slots = [];
  try { slots = row ? JSON.parse(row.slots) : []; } catch { slots = []; }
  const ok = row && row.call_a && callSignOk(row.call_a, row.call_b);
  return { callA: ok ? row.call_a : null, callB: ok ? row.call_b : null, slots: cleanSlots(slots, pulls) };
}

// Check a save. Returns an error message, or null when it is fine.
export function checkCase(body, pulls) {
  if (!body || typeof body !== 'object') return 'bad request';
  const { callA, callB, slots } = body;
  if (callA != null || callB != null) {
    if (typeof callA !== 'string' || typeof callB !== 'string' || !callSignOk(callA, callB)) return 'call sign not allowed';
  }
  if (!Array.isArray(slots) || slots.length !== SLOTS) return 'six slots';
  const have = held(pulls), used = new Set();
  for (const s of slots) {
    if (s === null) continue;
    if (!s || typeof s !== 'object' || typeof s.card !== 'string' || !VARIANTS.has(s.variant) || !FINISHES.has(s.finish)) return 'bad slot';
    const k = `${s.card}|${s.variant}|${s.finish}`;
    if (!have.has(k)) return 'card not held';
    if (used.has(k)) return 'card twice';
    used.add(k);
  }
  return null;
}

export async function saveCase(db, playerId, body) {
  await ensureCase(db);
  const slots = body.slots.map(s => s && { card: s.card, variant: s.variant, finish: s.finish });
  await db.prepare(`INSERT INTO display_case (player, call_a, call_b, slots, updated_at) VALUES (?, ?, ?, ?, ?)
    ON CONFLICT (player) DO UPDATE SET call_a = excluded.call_a, call_b = excluded.call_b, slots = excluded.slots, updated_at = excluded.updated_at`)
    .bind(playerId, body.callA ?? null, body.callB ?? null, JSON.stringify(slots), new Date().toISOString()).run();
  return { callA: body.callA ?? null, callB: body.callB ?? null, slots };
}
