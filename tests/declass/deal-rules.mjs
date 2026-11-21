// The hard group no repeat rule (Planning, 7 Nov 2026): strict no repeat first. A hard group seen in the
// last 90 days comes back only when no unseen one finds a fair board, oldest first, so a repeat only ever
// replaces what would have been a miss. Runs in plain node against the live master list:
//   node --import ./tests/declass/json-loader.mjs tests/declass/deal-rules.mjs
import { dealGrid, liveGroups, hasSameEvent, checkBoard, GROUPS } from '../../functions/_lib/intercept.js';
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

// 4. The same event rule (Planning, 19 Nov 2026; replaces the "X" and "X-spec" ids of 7 Nov): cards whose
// records share an "event" tag count as one card. Never two in a group, never two on one board, and a
// group left with fewer than three cards once they count as one stays dormant.
const byId = new Map(catalog.cards.map(c => [c.id, c]));
const EVENTS = {
  'tirpitz': ['namethis-1944-10-18-tirpitz', '1944-11-12-tirpitz', '1944-11-12-tirpitz-spec'],
  'kearny-1941': ['1941-10-17-kearny', '1941-10-17-kearny-spec'],
  'draft-lottery-1940': ['1940-10-29-draft-lottery', '1940-10-29-draft-spec'],
  'fu-go': ['1944-11-03-fugo', '1944-11-03-fugo-spec'],
  'naval-guadalcanal-1942': ['1942-11-15-kirishima', '1942-11-15-washington-spec'],
  'operation-queen': ['1944-11-16-operation-queen', '1944-11-16-duren'],
  'operation-uranus': ['1942-11-19-uranus', '1942-11-19-t34-spec', '1942-11-19-22nd-panzer'],
  'tarawa': ['1943-11-20-tarawa', '1943-11-20-betio-spec', '1943-11-21-shoup-quote'],
  'nuremberg-trial': ['1945-11-20-nuremberg-trial', '1945-11-21-jackson'],
};
for (const [ev, ids] of Object.entries(EVENTS)) {
  ok(ids.every(id => byId.get(id) && byId.get(id).event === ev), `${ev}: every card carries the tag (${ids.filter(id => !byId.get(id) || byId.get(id).event !== ev).join(', ')})`);
  ok(hasSameEvent(ids.map(id => byId.get(id))), `${ev}: counts as one event`);
}
const tagCount = new Map();
for (const c of catalog.cards) if (c.event) tagCount.set(c.event, (tagCount.get(c.event) || 0) + 1);
ok([...tagCount.values()].every(n => n >= 2), `every event tag is on at least two cards (${[...tagCount].filter(x => x[1] < 2).map(x => x[0]).join(', ')})`);
ok(!hasSameEvent([byId.get('1941-10-17-kearny'), byId.get('1941-10-31-reuben-james')]), 'Kearny and Reuben James are two events');
ok(!hasSameEvent([byId.get('1944-11-12-tirpitz'), byId.get('1944-11-13-manila-strike')]), 'two untagged events never match');
ok(!liveGroups(t).some(x => x.g.id === 'm-north-atlantic'), 'm-north-atlantic (Kearny, Kearny Specs, Reuben James) waits for a fourth card');
// A crafted board with Tirpitz Sunk in one group and Tirpitz Specs in another is refused for the event.
{
  const pick = ids => ids.map(id => byId.get(id));
  const filler = catalog.cards.filter(c => !c.event && c.kind === 'dispatch').slice(0, 10);
  const chosen = [
    { g: GROUPS[0], picked: [byId.get('1944-11-12-tirpitz'), filler[0], filler[1]] },
    { g: GROUPS[1], picked: [byId.get('1944-11-12-tirpitz-spec'), filler[2], filler[3]] },
    { g: GROUPS[2], picked: pick([]).concat(filler.slice(4, 7)) },
    { g: GROUPS[3], picked: filler.slice(7, 10) },
  ];
  ok(checkBoard(chosen).why === 'same event', `two groups holding one event each is refused (${checkBoard(chosen).why})`);
}
const late = new Date('2026-11-28T17:00:00Z');
let pairsDealt = 0, boardPairs = 0, grids4 = 0;
for (let i = 0; i < N; i++) {
  for (const when of [t, late]) {
    const g = dealGrid(when, { ...ctx(new Map()), day: when.toISOString().slice(0, 10) }); if (!g) continue; grids4++;
    for (const x of g.groups) if (hasSameEvent(x.idx.map(k => byId.get(g.cards[k].id)))) pairsDealt++;
    if (hasSameEvent(g.cards.map(c => byId.get(c.id)))) boardPairs++;
  }
}
ok(grids4 > N && pairsDealt === 0, `no group dealt with two cards of one event (${pairsDealt} in ${grids4} grids)`);
ok(boardPairs === 0, `no board shows two cards of one event (${boardPairs} in ${grids4} grids)`);

console.log(`${pass} passed, ${failN} failed`);
process.exit(failN ? 1 : 0);
