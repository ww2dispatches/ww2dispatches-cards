// Intercept master list check, run by the Wednesday research run after editing
// functions/_data/intercept.json (Research doc, "Intercept master list"):
//   node --import ./tests/declass/json-loader.mjs tests/declass/intercept-check.mjs [YYYY-MM-DD]
// It refuses a broken list (exit 1) and reports how ready the puzzle is: groups live and dormant by
// difficulty, how often a fair grid deals, how many different grids exist, and the weak spots.
import data from '../../functions/_data/intercept.json' with { type: 'json' };
import cat from '../../functions/_data/catalog.json' with { type: 'json' };
import { dealGrid, liveGroups, scoreOf, bonusOf, applyGuess, checkBoard } from '../../functions/_lib/intercept.js';
import { rollFinishNoCopper } from '../../functions/_lib/odds.js';

let errors = 0;
const err = m => { errors++; console.log('ERROR:', m); };
const ids = new Set(cat.cards.map(c => c.id));

// 1. The list itself.
const seen = new Set();
for (const g of data.groups) {
  if (!g.id || seen.has(g.id)) err('missing or repeated id: ' + g.id);
  seen.add(g.id);
  if (!['easy', 'medium', 'hard'].includes(g.difficulty)) err(g.id + ': difficulty must be easy, medium, or hard');
  if (!g.link || /[-–—]/.test(g.link.replace(/\b[A-Z]+-\d+\b|U-boats?|B-\d+|V-2|TDR-1/g, ''))) err(g.id + ': link missing, or it has a dash');
  if (!g.source) err(g.id + ': no source note');
  const both = (g.cards || []).filter(c => (g.alsoFits || []).includes(c));
  if (both.length) err(g.id + ': in both cards and alsoFits: ' + both.join(', '));
  if (/connections/i.test(JSON.stringify(g))) err(g.id + ': never use that word');
  const planned = [...(g.cards || []), ...(g.alsoFits || [])].filter(c => !ids.has(c));
  if (planned.length) console.log(`note: ${g.id} lists ${planned.length} card(s) not in the catalog yet (planned): ${planned.join(', ')}`);
}

// 2. Readiness on a given day (default: a week from today).
const day = process.argv[2] || new Date(Date.now() + 7 * 86400000).toISOString().slice(0, 10);
const t = new Date(day + 'T17:00:00Z');
const live = liveGroups(t), liveIds = new Set(live.map(x => x.g.id));
const by = d => live.filter(x => x.g.difficulty === d).length;
const all = d => data.groups.filter(g => g.difficulty === d && !g.vetoed).length;
console.log(`\nOn ${day}: live groups easy ${by('easy')} of ${all('easy')}, medium ${by('medium')} of ${all('medium')}, hard ${by('hard')} of ${all('hard')}`);
const dormant = data.groups.filter(g => !g.vetoed && !liveIds.has(g.id));
if (dormant.length) console.log('dormant (fewer than 3 posted cards): ' + dormant.map(g => g.id).join(', '));
const thin = live.filter(x => x.cards.length < 5).map(x => `${x.g.id} (${x.cards.length})`);
if (thin.length) console.log('fewer than 5 posted cards, so the same three come up often: ' + thin.join(', '));

const ctx = { day, owned: new Set(), hardSeen: new Map(), recentGroups: new Map(), recentCards: new Set() };
const N = 400, combos = new Set(), hardUse = new Map(), cardUse = new Map();
let dealt = 0;
for (let i = 0; i < N; i++) {
  const g = dealGrid(t, ctx);
  if (!g) continue;
  dealt++;
  combos.add(g.groups.map(x => x.id).sort().join(','));
  const h = g.groups.find(x => x.d === 'hard').id; hardUse.set(h, (hardUse.get(h) || 0) + 1);
  g.cards.forEach(c => cardUse.set(c.id, (cardUse.get(c.id) || 0) + 1));
}
console.log(`deals: ${dealt} of ${N} found a fair grid; ${combos.size} different sets of four groups; ${cardUse.size} different cards used`);
const neverHard = live.filter(x => x.g.difficulty === 'hard' && !hardUse.has(x.g.id)).map(x => x.g.id);
if (neverHard.length) console.log('hard groups that never dealt (they clash with the rest or give themselves away by year or series): ' + neverHard.join(', '));
const freshHard = by('hard');
const ready = dealt / N >= 0.98 && combos.size >= 40 && freshHard >= 15;
console.log(`launch readiness (98% deals, 40 sets of groups, 15 live hard groups): ${ready ? 'READY' : 'not yet'}`);

// 3. Rules that must never drift.
const sum = (f, n = 400000) => { const c = {}; for (let i = 0; i < n; i++) { const x = f(); c[x] = (c[x] || 0) + 1; } return Object.fromEntries(Object.entries(c).map(([k, v]) => [k, +(100 * v / n).toFixed(2)])); };
const st = sum(() => rollFinishNoCopper('still')), lv = sum(() => rollFinishNoCopper('living'));
if (st.copper || Math.abs(st.silver - 79) > 0.5 || Math.abs(st.gold - 20) > 0.5 || Math.abs(st.topsecret - 1) > 0.15) err('perfect solve still odds off: ' + JSON.stringify(st));
if (lv.copper || Math.abs(lv.silver - 65) > 0.5 || Math.abs(lv.gold - 31.25) > 0.5 || Math.abs(lv.topsecret - 3.75) > 0.25) err('perfect solve living odds off: ' + JSON.stringify(lv));
if ([0, 1, 2, 3].map(m => scoreOf(4, m)).join() !== '100,90,80,70') err('scores');
if ([100, 90, 80, 70].map(s => bonusOf('solved', s)).join() !== '15,10,5,5' || bonusOf('failed', 0) !== 2) err('bonus Intel');
const fake = { grid: { cards: Array.from({ length: 12 }, (_, i) => ({ id: 'c' + i })), groups: [0, 1, 2, 3].map(k => ({ idx: [k * 3, k * 3 + 1, k * 3 + 2] })) }, found: [], tries: [], mistakes: 0, status: 'play' };
let s = applyGuess(fake, [0, 3, 6]); if (s.result !== 'wrong' || s.state.mistakes !== 1) err('wrong guess');
const again = applyGuess(s.state, [6, 0, 3]); if (again.result !== 'tried' || again.state.mistakes !== 1) err('already tried');
s = applyGuess(s.state, [2, 1, 0]); s = applyGuess(s.state, [3, 4, 5]); s = applyGuess(s.state, [8, 7, 6]);
if (s.state.status !== 'solved' || s.state.found.length !== 4 || s.state.found[3] !== 3) err('auto lock of the last group');
console.log(`\nst ${JSON.stringify(st)} living ${JSON.stringify(lv)}`);
console.log(errors ? `${errors} error(s)` : 'master list OK');
process.exit(errors ? 1 : 0);
