// The hard group no repeat rule (Planning, 7 Nov 2026): strict no repeat first. A hard group seen in the
// last 90 days comes back only when no unseen one finds a fair board, oldest first, so a repeat only ever
// replaces what would have been a miss. Runs in plain node against the live master list:
//   node --import ./tests/declass/json-loader.mjs tests/declass/deal-rules.mjs
import { dealGrid, liveGroups, hasSameEvent } from '../../functions/_lib/intercept.js';
import catalog from '../../functions/_data/catalog.json' with { type: 'json' };

let pass = 0, failN = 0;
const ok = (cond, msg) => { if (cond) pass++; else { failN++; console.log('FAIL:', msg); } };
const t = new Date('2026-11-07T17:00:00Z'), day = '2026-11-07';
const ctx = hardSeen => ({ day, owned: new Set(), hardSeen, recentGroups: new Map(), recentCards: new Set() });
const daysAgo = n => new Date(Date.parse(day) - n * 864e5).toISOString().slice(0, 10);
const hardOf = g => g.groups.find(x => x.d === 'hard').id;
const N = 200; // fair deal rates are the readiness check's job; these only need enough grids to judge the rule

// 1. Nothing seen: every deal is a fresh hard group, never marked a repeat.
const dealt = new Map();
let grids = 0, marked = 0;
for (let i = 0; i < N; i++) { const g = dealGrid(t, ctx(new Map())); if (!g) continue; grids++; if (g.repeat) marked++; dealt.set(hardOf(g), (dealt.get(hardOf(g)) || 0) + 1); }
ok(grids >= N * 0.9, `nothing seen: ${grids} of ${N} deals found a grid`);
ok(marked === 0, `nothing seen: no deal marked a repeat (${marked})`);
const dealable = [...dealt.keys()];
ok(dealable.length >= 5, `${dealable.length} hard groups can deal (${liveGroups(t).filter(x => x.g.difficulty === 'hard').length} live)`);

// 2. Every dealable hard group but one seen yesterday: the unseen one deals whenever it can; a seen one
// only comes back marked as a repeat, and rarely.
const keep = dealable.sort((a, b) => dealt.get(b) - dealt.get(a))[0];
const seen2 = new Map(liveGroups(t).filter(x => x.g.difficulty === 'hard' && x.g.id !== keep).map(x => [x.g.id, daysAgo(1)]));
let fresh2 = 0, rep2 = 0, bad2 = 0;
for (let i = 0; i < N; i++) {
  const g = dealGrid(t, ctx(seen2)); if (!g) continue;
  const h = hardOf(g);
  if (h === keep) { fresh2++; if (g.repeat) bad2++; } else { rep2++; if (!g.repeat || !seen2.has(h)) bad2++; }
}
ok(bad2 === 0, `one unseen: a seen hard group is only ever dealt as a marked repeat (${bad2} wrong)`);
ok(fresh2 >= N * 0.9, `one unseen: the unseen group (${keep}) dealt ${fresh2} of ${N} times`);
ok(rep2 <= N * 0.1, `one unseen: repeats only stand in for misses (${rep2} of ${N})`);

// 3. Every hard group seen, on different days: the deal still finds a grid, every one is a marked repeat,
// and the one seen longest ago comes back most often.
const order = dealable.slice();
const seen3 = new Map(liveGroups(t).filter(x => x.g.difficulty === 'hard').map(x => [x.g.id, daysAgo(1)]));
order.forEach((id, i) => seen3.set(id, daysAgo(80 - i)));
const back = new Map(); let grids3 = 0, unmarked3 = 0;
for (let i = 0; i < N; i++) { const g = dealGrid(t, ctx(seen3)); if (!g) continue; grids3++; if (!g.repeat) unmarked3++; back.set(hardOf(g), (back.get(hardOf(g)) || 0) + 1); }
ok(grids3 >= N * 0.9, `all seen: ${grids3} of ${N} deals still found a grid`);
ok(unmarked3 === 0, `all seen: every deal is marked a repeat (${unmarked3} not)`);
const top = [...back.entries()].sort((a, b) => b[1] - a[1])[0];
ok(top && top[0] === order[0], `all seen: the oldest (${order[0]}) comes back most (top ${top && top.join(' ')})`);

// 4. The same event rule (Planning, 7 Nov 2026): a story card and its spec sheet never share a group,
// and a group left with fewer than three cards once a pair counts as one stays dormant.
const byId = new Map(catalog.cards.map(c => [c.id, c]));
ok(hasSameEvent([byId.get('1941-10-17-kearny'), byId.get('1941-10-17-kearny-spec')]), 'Kearny and Kearny Specs count as one event');
ok(!hasSameEvent([byId.get('1941-10-17-kearny'), byId.get('1941-10-31-reuben-james')]), 'Kearny and Reuben James are two events');
ok(!liveGroups(t).some(x => x.g.id === 'm-north-atlantic'), 'm-north-atlantic (Kearny, Kearny Specs, Reuben James) waits for a fourth card');
let pairsDealt = 0, grids4 = 0;
for (let i = 0; i < N; i++) {
  const g = dealGrid(t, ctx(new Map())); if (!g) continue; grids4++;
  for (const x of g.groups) if (hasSameEvent(x.idx.map(k => byId.get(g.cards[k].id)))) pairsDealt++;
}
ok(grids4 > 0 && pairsDealt === 0, `no group dealt with a story card and its spec sheet (${pairsDealt} in ${grids4} grids)`);

console.log(`${pass} passed, ${failN} failed`);
process.exit(failN ? 1 : 0);
