// Intercept · a Declass daily puzzle (decided 26 Oct 2026, Declass Build doc "Intercept").
// Twelve cards in four hidden groups of three. Every player gets their own grid, dealt from the master
// list (functions/_data/intercept.json): one easy, two medium, and one hard group, three cards each, with
// a conflict check so no card on the board fits two of the four links. The grid is saved on the server
// the moment it is dealt, so closing the page can never reroll it.
import data from '../_data/intercept.json';
import { released, filmReleased, findCard } from './catalog.js';
import { gameDay, addDays, zonedTime, isoSec } from './time.js';

// Launch switch. Until it is true, the home tile reads "Coming soon" and only a tester who opened the
// preview link (?intercept=preview) can play. Launching is a one line change here, no Cloudflare step.
export const INTERCEPT_LIVE = false;

export const GROUPS = data.groups.filter(g => !g.vetoed);
const ALL_GROUPS = data.groups; // vetoed groups still count as decoys: the link is still true
const BY_ID = new Map(GROUPS.map(g => [g.id, g]));
export const MAX_MISTAKES = 3;
export const PLAY_INTEL = 3;
const NEED = { easy: 1, medium: 2, hard: 1 };
const HARD_REST_DAYS = 90;
const KEEP_DAYS = 90;
const ATTEMPTS = 80; // sets of groups tried per hard group before falling back to the next one
const CARD_DRAWS = 4; // card draws tried for each set of groups
const TOTAL_TRIES = 600; // the most boards checked in one deal, which keeps it inside the server's CPU allowance
const LIVING_ONE_IN = 6; // the same living rate as an archive slot

export const fitsOf = g => new Set([...(g.cards || []), ...(g.alsoFits || [])]);
const FITS = new Map(ALL_GROUPS.map(g => [g.id, fitsOf(g)]));

// Who may play right now: everyone once live; before that, testers holding the preview flag, and any
// local test copy.
export function interceptOpen(env, request, player) {
  if (INTERCEPT_LIVE) return true;
  if (env.ALLOW_FAKE_NOW === '1') return true;
  return Boolean(player && player.tester && request.headers.get('x-intercept-preview') === '1');
}

// The game day and the moment it ends (midnight Eastern).
export const puzzleDay = t => gameDay(t);
export const closesAt = day => isoSec(zonedTime(addDays(day, 1), '00:00'));

// Groups with at least three posted cards that can be dealt from them. Dormant groups wait for cards.
export function liveGroups(t) {
  const out = [];
  for (const g of GROUPS) {
    const cards = (g.cards || []).map(id => findCard(id, t)).filter(Boolean);
    if (cards.length >= 3) out.push({ g, cards });
  }
  return out;
}

// What the board's printed details say: the series stamp and the year in the date. These are never
// links, and three cards sharing one (and only three) read like a group.
const seriesOf = c => c.flash ? 'flash' : c.series;
const yearOf = c => String(c.date || '').slice(0, 4);

function weightedPick(list, weight, rnd) {
  const ws = list.map(weight), total = ws.reduce((a, b) => a + b, 0);
  if (!(total > 0)) return null;
  let x = rnd(1000000) / 1000000 * total;
  for (let i = 0; i < list.length; i++) { x -= ws[i]; if (x < 0) return list[i]; }
  return list[list.length - 1];
}
function weightedSample(list, n, weight, rnd) {
  const pool = list.slice(), out = [];
  while (out.length < n && pool.length) {
    const p = weightedPick(pool, weight, rnd);
    out.push(p); pool.splice(pool.indexOf(p), 1);
  }
  return out;
}
function shuffle(a, rnd) { for (let i = a.length - 1; i > 0; i--) { const j = rnd(i + 1); [a[i], a[j]] = [a[j], a[i]]; } return a; }

// Checks a dealt board. chosen: [{g, picked:[card]}]. Returns {ok, decoys, why}.
export function checkBoard(chosen) {
  const board = [], own = new Map();
  chosen.forEach((x, gi) => x.picked.forEach(c => { board.push(c); own.set(c.id, gi); }));
  if (own.size !== 12) return { ok: false, why: 'repeat' };
  // 1. No card fits two of the four links.
  for (const c of board) {
    for (let gi = 0; gi < chosen.length; gi++) if (gi !== own.get(c.id) && FITS.get(chosen[gi].g.id).has(c.id)) return { ok: false, why: 'conflict' };
  }
  const oneGroup = list => list.every(c => own.get(c.id) === own.get(list[0].id));
  let decoys = 0;
  // 2. Printed details: a series or a year on exactly three cards. If those three are one of the real
  // groups, the board gives it away by reading, so it is refused; otherwise it is a decoy.
  for (const key of [seriesOf, yearOf]) {
    const m = new Map();
    for (const c of board) { const k = key(c); const l = m.get(k); if (l) l.push(c); else m.set(k, [c]); }
    for (const list of m.values()) {
      if (list.length !== 3) continue;
      if (oneGroup(list)) return { ok: false, why: 'giveaway' };
      if (++decoys > 1) return { ok: false, why: 'decoys' };
    }
  }
  // 3. Any other link in the master list that holds exactly three cards here, from more than one of
  // the real groups, is a decoy too. At most one decoy on a board, never more.
  const chosenIds = new Set(chosen.map(x => x.g.id));
  for (const g of ALL_GROUPS) {
    if (chosenIds.has(g.id)) continue;
    const f = FITS.get(g.id);
    let n = 0, first = -1, mixed = false;
    for (const c of board) if (f.has(c.id)) { n++; const gi = own.get(c.id); if (first < 0) first = gi; else if (gi !== first) mixed = true; }
    if (n === 3 && mixed && ++decoys > 1) return { ok: false, why: 'decoys' };
  }
  return { ok: true, decoys };
}

// A fast random source for one deal: secure random numbers fetched in a batch, not one call each.
function batchRandom() {
  const buf = new Uint32Array(512); let i = buf.length;
  return n => {
    if (!(n > 0)) return 0;
    const limit = Math.floor(0x100000000 / n) * n;
    for (;;) { if (i >= buf.length) { crypto.getRandomValues(buf); i = 0; } const v = buf[i++]; if (v < limit) return v % n; }
  };
}

// Deal a grid for one player.
// ctx: { owned: Set of card ids the player holds, hardSeen: Map group id -> last day dealt,
//        recentGroups: Map group id -> last day dealt (all groups, last 90 days),
//        recentCards: Set of card ids dealt in the last 30 days, day: today }
// Returns null when no fair grid turned up within the try budget (the page offers to try again).
export function dealGrid(t, ctx, rnd = batchRandom()) {
  const live = liveGroups(t);
  const by = { easy: [], medium: [], hard: [] };
  live.forEach(x => by[x.g.difficulty] && by[x.g.difficulty].push(x));
  if (by.easy.length < NEED.easy || by.medium.length < NEED.medium || by.hard.length < NEED.hard) return null;

  const day = ctx.day, ago = d => d ? (Date.parse(day) - Date.parse(d)) / 86400000 : Infinity;
  // Hard groups: never one the player saw in the last 90 days, unless every one has been seen; then
  // the one seen longest ago comes first.
  const fresh = shuffle(by.hard.filter(x => ago(ctx.hardSeen.get(x.g.id)) >= HARD_REST_DAYS), rnd);
  const stale = by.hard.filter(x => ago(ctx.hardSeen.get(x.g.id)) < HARD_REST_DAYS)
    .sort((a, b) => String(ctx.hardSeen.get(a.g.id)).localeCompare(String(ctx.hardSeen.get(b.g.id))));
  const groupWeight = x => { const a = ago(ctx.recentGroups.get(x.g.id)); return a < 7 ? 0.25 : a < 30 ? 0.6 : 1; };
  const cardWeight = c => (ctx.owned.has(c.id) ? 1 : 3) * (ctx.recentCards.has(c.id) ? 0.5 : 1);

  // Two groups can share a board only if each keeps three cards that don't fit the other's link.
  const memo = new Map();
  const outside = (a, b) => { const f = FITS.get(b.g.id); let n = 0; for (const c of a.cards) if (!f.has(c.id) && ++n >= 3) return true; return false; };
  const compat = (a, b) => {
    const k = a.g.id + '>' + b.g.id;
    if (!memo.has(k)) { const v = outside(a, b) && outside(b, a); memo.set(k, v); memo.set(b.g.id + '>' + a.g.id, v); }
    return memo.get(k);
  };

  let budget = TOTAL_TRIES;
  for (const hard of [...fresh, ...stale]) {
    const easies = by.easy.filter(x => compat(x, hard));
    const meds = by.medium.filter(x => compat(x, hard));
    if (!easies.length || meds.length < 2) continue;
    for (let a = 0; a < ATTEMPTS && budget > 0; a++) {
      const easy = weightedPick(easies, groupWeight, rnd);
      const m1 = weightedPick(meds.filter(x => compat(x, easy)), groupWeight, rnd);
      const m2 = m1 && weightedPick(meds.filter(x => x !== m1 && compat(x, easy) && compat(x, m1)), groupWeight, rnd);
      if (!easy || !m1 || !m2) { budget--; continue; }
      // Most constrained first: hard, then the two medium, then easy. A few card draws per set of groups.
      const order = [hard, m1, m2, easy];
      const pools = order.map(x => { const others = order.filter(o => o !== x).map(o => FITS.get(o.g.id)); return x.cards.filter(c => !others.some(f => f.has(c.id))); });
      if (pools.some(p => p.length < 3)) { budget--; continue; }
      for (let draw = 0; draw < CARD_DRAWS && budget > 0; draw++, budget--) {
        const used = new Set(), chosen = [];
        let failed = false;
        for (let k = 0; k < 4; k++) {
          const picked = weightedSample(pools[k].filter(c => !used.has(c.id)), 3, cardWeight, rnd);
          if (picked.length < 3) { failed = true; break; }
          picked.forEach(c => used.add(c.id));
          chosen.push({ g: order[k].g, picked });
        }
        if (!failed && checkBoard(chosen).ok) return buildGrid(chosen, t, rnd);
      }
    }
    if (budget <= 0) break;
  }
  return null;
}

function buildGrid(chosen, t, rnd) {
  const slots = shuffle(chosen.flatMap((x, gi) => x.picked.map(c => ({ c, gi }))), rnd);
  const cards = slots.map(({ c }) => ({ id: c.id, v: !c.flash && filmReleased(c, t) && rnd(LIVING_ONE_IN) === 0 ? 'living' : 'still' }));
  const groups = chosen.map((x, gi) => ({ id: x.g.id, link: x.g.link, d: x.g.difficulty, idx: slots.map((s, i) => s.gi === gi ? i : -1).filter(i => i >= 0) }));
  return { cards, groups };
}

// Scoring: 25 for each link found, minus 10 for each mistake. A solved puzzle scores 100, 90, 80, or 70.
export const scoreOf = (found, mistakes) => Math.max(0, 25 * found - 10 * mistakes);
// Intel on the result screen: 3 for playing plus the score bonus (not solved earns 2).
export function bonusOf(status, score) {
  if (status !== 'solved') return 2;
  return score >= 100 ? 15 : score >= 90 ? 10 : 5;
}

// One guess against a saved puzzle state. Pure: returns the new state and what happened.
// state: { grid, found: [group index], tries: ["i|j|k"], mistakes, status }
export function applyGuess(state, pick) {
  const n = state.grid.cards.length;
  const p = [...new Set((pick || []).map(Number))].filter(i => Number.isInteger(i) && i >= 0 && i < n);
  if (p.length !== 3) return { error: 'bad pick' };
  const taken = new Set(state.found.flatMap(gi => state.grid.groups[gi].idx));
  if (p.some(i => taken.has(i))) return { error: 'bad pick' };
  const key = p.slice().sort((a, b) => a - b).join('|');
  if (state.tries.includes(key)) return { result: 'tried', state };
  const next = { ...state, found: state.found.slice(), tries: state.tries.slice() };
  const gi = state.grid.groups.findIndex((g, i) => !state.found.includes(i) && g.idx.slice().sort((a, b) => a - b).join('|') === key);
  let result;
  if (gi >= 0) {
    result = 'correct';
    next.found.push(gi);
    // Three found: the last one locks on its own.
    if (next.found.length === 3) { next.found.push([0, 1, 2, 3].find(i => !next.found.includes(i))); next.status = 'solved'; }
  } else {
    result = 'wrong';
    next.mistakes++;
    next.tries.push(key);
    if (next.mistakes >= MAX_MISTAKES) next.status = 'failed';
  }
  return { result, state: next, group: gi >= 0 ? gi : null };
}

// What the page may see. While the puzzle is open, only the links already found; once it ends, every
// group (found first, in order), so the player still learns the answers. The difficulty never leaves.
export function publicPuzzle(row, t) {
  const grid = JSON.parse(row.grid), found = JSON.parse(row.found || '[]'), tries = JSON.parse(row.tries || '[]');
  const done = row.status !== 'play';
  const order = done ? found.concat([0, 1, 2, 3].filter(i => !found.includes(i))) : found;
  const claimed = row.claimed ? JSON.parse(row.claimed) : null;
  return {
    day: row.day, closes: closesAt(row.day), status: row.status, mistakes: row.mistakes, maxMistakes: MAX_MISTAKES,
    cards: grid.cards, tried: tries.length,
    groups: order.map(gi => ({ link: grid.groups[gi].link, idx: grid.groups[gi].idx, found: found.includes(gi) })),
    found: found.length,
    score: done ? row.score : null, intel: done ? row.intel : null,
    claimed, canClaim: row.status === 'solved' && !claimed,
    perfect: row.status === 'solved' && row.mistakes === 0,
    expired: !done && gameDay(t) !== row.day,
  };
}

// The tables. Created on first use, so going live needs no step in the Cloudflare console (the same
// statements are in migrations/0003_intercept.sql for the record).
export const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS intercept (player_id TEXT NOT NULL, day TEXT NOT NULL, dealt_at TEXT NOT NULL, tok TEXT NOT NULL, grid TEXT NOT NULL, found TEXT NOT NULL DEFAULT '[]', tries TEXT NOT NULL DEFAULT '[]', mistakes INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'play', score INTEGER, intel INTEGER, fin TEXT, claimed TEXT, moves INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (player_id, day))`,
  `CREATE INDEX IF NOT EXISTS intercept_day ON intercept(day)`,
  `CREATE TABLE IF NOT EXISTS intercept_seen (player_id TEXT NOT NULL, group_id TEXT NOT NULL, last_day TEXT NOT NULL, PRIMARY KEY (player_id, group_id))`,
];
let ready = null;
export function ensureTables(db) {
  if (!ready) ready = db.batch(SCHEMA.map(s => db.prepare(s))).catch(err => { ready = null; throw err; });
  return ready;
}

// Everything the deal needs to know about this player.
export async function dealContext(db, playerId, t) {
  const day = gameDay(t), since = addDays(day, -KEEP_DAYS), since30 = addDays(day, -30);
  const [owned, seen, rows] = await db.batch([
    db.prepare('SELECT DISTINCT card_id FROM pulls WHERE player_id = ?').bind(playerId),
    db.prepare('SELECT group_id, last_day FROM intercept_seen WHERE player_id = ?').bind(playerId),
    db.prepare('SELECT day, grid FROM intercept WHERE player_id = ? AND day >= ? ORDER BY day').bind(playerId, since),
  ]);
  const recentGroups = new Map(), recentCards = new Set();
  for (const r of rows.results) {
    let g; try { g = JSON.parse(r.grid); } catch { continue; }
    g.groups.forEach(x => recentGroups.set(x.id, r.day));
    if (r.day >= since30) g.cards.forEach(c => recentCards.add(c.id));
  }
  return {
    day, owned: new Set(owned.results.map(r => r.card_id)),
    hardSeen: new Map(seen.results.map(r => [r.group_id, r.last_day])),
    recentGroups, recentCards,
  };
}

export const cleanupCutoff = t => addDays(gameDay(t), -KEEP_DAYS);
export const groupById = id => BY_ID.get(id);
export const releasedCard = (id, t) => findCard(id, t);
export { released };

// A short random code (deal and finish tokens).
export function token() { const b = new Uint8Array(9); crypto.getRandomValues(b); return [...b].map(x => x.toString(16).padStart(2, '0')).join(''); }

// Today's row for this player, or null.
export const todayRow = (db, playerId, day) => db.prepare('SELECT * FROM intercept WHERE player_id = ? AND day = ?').bind(playerId, day).first();

// The small summary the home tile needs (from /api/state).
export async function interceptSummary(env, request, player, t) {
  if (!interceptOpen(env, request, player)) return { status: 'soon' };
  const day = puzzleDay(t), closes = closesAt(day);
  if (!player) return { status: 'signin', day, closes };
  await ensureTables(env.DB);
  const row = await todayRow(env.DB, player.id, day);
  if (!row) return { status: 'new', day, closes };
  const found = JSON.parse(row.found || '[]').length;
  return { status: row.status, day, closes, found, mistakes: row.mistakes, score: row.status === 'play' ? null : row.score, claimed: Boolean(row.claimed), canClaim: row.status === 'solved' && !row.claimed };
}
