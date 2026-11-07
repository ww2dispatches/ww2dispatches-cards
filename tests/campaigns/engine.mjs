// Campaigns engine checks (build session 1). Run from the repo root:
//   node --import ./tests/declass/json-loader.mjs tests/campaigns/engine.mjs
// Plain node, no server. Uses the real Battle of Britain campaign file and made up test decks.
import campaign from '../../functions/_data/campaigns/1940-08-battle-of-britain.json' with { type: 'json' };
import * as E from '../../site/declass/campaigns/engine.js';
import { FIGHTER_COMMAND, STATECRAFT_HEAVY } from './decks.mjs';
import { playRun } from './bot.mjs';

let pass = 0, fail = 0;
const ok = (c, msg) => { if (c) pass++; else { fail++; console.log('FAIL:', msg); } };
const act = (st, c) => E.act(campaign, st, c);
const find = (st, pred) => st.hand.find(i => pred(st.cards[i]));

// The campaign file
ok(campaign.format === 1 && campaign.chapters.length === 3, 'campaign file has three chapters');
for (const ch of campaign.chapters) {
  ok(ch.waves.length === 3, `chapter ${ch.n} has three waves`);
  for (const w of ch.waves) for (const u of [...w.units, ...w.reinforcements.map(r => r.unit)]) ok(u.script.every(a => a >= 0 && a <= 7) && u.strength >= 1 && u.strength <= 7, `${u.name} is on the 1 to 7 scale`);
  const w1 = ch.waves[0]; ok(Math.max(...w1.units.flatMap(u => u.script)) <= 2 && !w1.reinforcements.length, `chapter ${ch.n}: the first wave stays gentle`);
}

// Deck checks
ok(E.deckProblems(campaign, 2, FIGHTER_COMMAND).length === 0, 'the test deck is legal');
ok(E.deckProblems(campaign, 2, FIGHTER_COMMAND.slice(0, 19)).length === 1, 'a 19 card deck is refused');
ok(E.deckProblems(campaign, 2, [...FIGHTER_COMMAND.slice(0, 19), { series: 'blue', value: 3, branches: ['sea'] }]).length === 1, 'a sea machine is refused in an air chapter');
ok(E.deckProblems(campaign, 2, [...FIGHTER_COMMAND.slice(0, 19), { series: 'home', value: 3, branches: [], noPlay: true }]).length === 1, 'a noPlay card is refused');
ok(E.deckProblems(campaign, 2, [...FIGHTER_COMMAND.slice(0, 19), { series: 'home', value: null, branches: [] }]).length === 1, 'a card with no number is refused');

// The same seed and choices always give the same result
{
  const a = playRun(campaign, 2, FIGHTER_COMMAND, 'day-1');
  const b = E.replay(campaign, 2, FIGHTER_COMMAND, 'day-1', a.choices);
  ok(b.ok && JSON.stringify(b.result) === JSON.stringify(a.state.over), 'replay gives the same result');
  const d = E.newRun(campaign, 2, FIGHTER_COMMAND, 'day-1'), e = E.newRun(campaign, 2, FIGHTER_COMMAND, 'day-2');
  ok(JSON.stringify(d.hand) !== JSON.stringify(e.hand) || JSON.stringify(d.draw) !== JSON.stringify(e.draw), 'different seeds shuffle differently');
  ok(JSON.stringify(E.newRun(campaign, 2, FIGHTER_COMMAND, 'day-1').draw) === JSON.stringify(d.draw), 'the same seed shuffles the same');
  const tampered = a.choices.slice(0, -1);
  ok(!E.replay(campaign, 2, FIGHTER_COMMAND, 'day-1', tampered).ok, 'an unfinished run is refused');
  ok(!E.replay(campaign, 2, FIGHTER_COMMAND, 'day-1', [{ a: 'keep' }, { a: 'lock' }]).ok, 'an illegal choice is refused');
}

// The opening hand
for (let s = 0; s < 200; s++) {
  const st = E.newRun(campaign, 1, FIGHTER_COMMAND, 'open-' + s);
  ok(st.hand.length === 5 && st.hand.some(i => st.cards[i].series === 'blue' && st.cards[i].value <= 2), 'the opening hand holds an affordable machine');
  if (s === 0) { ok(act(st, { a: 'mulligan' }).ok && !act(st, { a: 'mulligan' }).ok, 'one mulligan a run'); }
}

// The calm opening, setup turn, Supply, and Rearming
{
  const st = E.newRun(campaign, 2, FIGHTER_COMMAND, 'rules-1'); act(st, { a: 'keep' });
  ok(st.phase === 'yours' && st.round === 1 && st.supply === 2, 'round 1 starts with your turn and 2 Supply');
  const m1 = find(st, c => c.series === 'blue' && c.value <= 2); act(st, { a: 'place', card: m1 });
  const mach = st.line[0];
  ok(mach.fresh && mach.arm === st.cards[m1].value, 'a placed machine sets up with armor equal to its number');
  const op = find(st, c => c.series === 'battle' && c.value <= st.supply);
  if (op !== undefined) ok(!act(st, { a: 'attach', card: op, machine: mach.uid }).ok, 'a new machine cannot be armed the turn it is placed');
  act(st, { a: 'end' });
  ok(st.round === 2 && st.phase === 'yours' && st.supply === 3, 'round 2 is calm: your turn again, 3 Supply');
  ok(!mach.fresh, 'the machine has set up');
  ok(E.alive(st).every(u => E.coming(st, u) > 0 || u.script[0] === 0), 'in round 2 the raid of round 3 shows');
  const op2 = find(st, c => c.series === 'battle' && c.value <= st.supply);
  if (op2 !== undefined) { ok(act(st, { a: 'attach', card: op2, machine: mach.uid }).ok, 'the machine can be armed after setting up'); ok(!E.canAttack(st, mach), 'no attacks in the calm rounds'); }
  act(st, { a: 'end' });
  ok(st.round === 3 && st.phase === 'enemy', 'the first raid comes in round 3');
  const cardSc = find(st, c => c.series === 'state' && c.keyword !== 'ultimatum');
  if (cardSc !== undefined) ok(!act(st, { a: cardSc && st.cards[cardSc].keyword, card: cardSc }).ok, 'only an Ultimatum in the raid');
  const esc = E.alive(st).find(u => u.escort);
  ok(act(st, { a: 'block', unit: esc.uid, machines: [mach.uid] }).ok, 'a Ready machine blocks');
  const r0 = st.resolve; act(st, { a: 'lock' });
  ok(st.phase === 'yours' && st.round === 3 && st.supply === 4, 'after the raid it is your turn with 4 Supply');
  ok(mach.state === 'blocked' || !st.line.includes(mach), 'a blocker is Rearming for the rest of the round');
  if (st.line.includes(mach)) ok(!E.canAttack(st, mach), 'a blocker cannot attack that round');
  ok(st.resolve <= r0, 'the unblocked attack hit Resolve');
}

// Escorts first, attackers sit out the next raid
{
  let st, choices;
  for (let s = 0; s < 50; s++) { const r = playRun(campaign, 2, FIGHTER_COMMAND, 'esc-' + s); if (r.choices.some(c => c.a === 'attack')) { st = r.state; choices = r.choices; break; } }
  const k = choices.findIndex(c => c.a === 'attack');
  const s2 = E.newRun(campaign, 2, FIGHTER_COMMAND, st.seed); for (let j = 0; j < k; j++) E.act(campaign, s2, choices[j]);
  const m = s2.line.find(x => x.uid === choices[k].machine);
  const bomber = E.alive(s2).find(u => !u.escort), escort = E.alive(s2).find(u => u.escort);
  if (bomber && escort) ok(!E.act(campaign, s2, { a: 'attack', machine: m.uid, unit: bomber.uid }).ok, 'escorts must be attacked first');
  E.act(campaign, s2, choices[k]); let j = k + 1; while (choices[j].a !== 'end') E.act(campaign, s2, choices[j++]); E.act(campaign, s2, choices[j]);
  if (!s2.over && s2.line.includes(m)) { ok(m.state === 'out' && !E.canBlock(m), 'an attacker cannot block the next raid'); }
}

// Statecraft: free, one a round, fixed reach
{
  const deck = [...FIGHTER_COMMAND.slice(0, 16), { series: 'state', value: 7, branches: [], keyword: 'backchannel' }, { series: 'state', value: 1, branches: [], keyword: 'backchannel' }, ...FIGHTER_COMMAND.slice(18)];
  let tested = false;
  for (let s = 0; s < 300 && !tested; s++) {
    const st = E.newRun(campaign, 2, deck, 'sc-' + s); act(st, { a: 'keep' });
    const bc = st.hand.filter(i => st.cards[i].keyword === 'backchannel');
    if (bc.length < 2) continue;
    const sup = st.supply, h = st.hand.length;
    ok(act(st, { a: 'backchannel', card: bc[0] }).ok && st.supply === sup && st.hand.length === h + 1, 'Back Channel is free and draws 2');
    ok(!act(st, { a: 'backchannel', card: bc[1] }).ok, 'one Statecraft card a round');
    tested = true;
  }
  ok(tested, 'found a hand to test Statecraft');
  ok(E.REACH.lend === 3 && E.REACH.ultimatum === 5 && E.REACH.evac === 2, 'fixed reaches: Lend Lease 3, Ultimatum 5, Evacuation 2');
}

// The airfield raids twist
{
  let seen = 0, wrong = 0;
  for (let s = 0; s < 300; s++) {
    const r = playRun(campaign, 3, FIGHTER_COMMAND, 'af-' + s);
    const st = E.newRun(campaign, 3, FIGHTER_COMMAND, 'af-' + s);
    for (const c of r.choices) { const before = E.copy(st); E.act(campaign, st, c); for (const e of st.events.filter(e => e.t === 'ground')) { seen++; if (e.to < 1 || e.to >= e.from) wrong++; } }
  }
  ok(seen > 0 && wrong === 0, `airfield raids hit Rearming machines and never below 1 armor (${seen} hits)`);
  const none = E.newRun(campaign, 2, FIGHTER_COMMAND, 'af-x');
  ok(none.twist === null, 'chapter 2 has no twist');
}

// The automatic player lands where the test bench did
const rate = (ch, deck, n) => { let w = 0; for (let s = 0; s < n; s++) if (playRun(campaign, ch, deck, `bot-${ch}-${s}`).state.over.won) w++; return w / n; };
const N = Number(process.env.RUNS || 400);
const rates = {};
for (const ch of [1, 2, 3]) { rates[ch] = { fc: rate(ch, FIGHTER_COMMAND, N), sc: rate(ch, STATECRAFT_HEAVY, N) }; }
console.log('Automatic player win rates over', N, 'runs:', JSON.stringify(rates));
ok(rates[1].fc > rates[2].fc && rates[2].fc > rates[3].fc, 'the month gets harder chapter by chapter');
ok(rates[1].fc >= 0.65 && rates[1].fc <= 0.92, 'chapter 1 near the bench (about 80%)');
ok(rates[2].fc >= 0.35 && rates[2].fc <= 0.62, 'chapter 2 near the bench (about 45 to 50%)');
ok(rates[3].fc >= 0.18 && rates[3].fc <= 0.42, 'chapter 3 near the bench (about 30%)');
ok(rates[2].sc < rates[2].fc, 'the Statecraft heavy deck is harder');

// Scores order every run
ok(E.score({ won: true, resolve: 1, rounds: 20 }) > E.score({ won: false, wavesCleared: 2, destroyed: 0.99 }), 'every win ranks above every loss');
ok(E.score({ won: true, resolve: 5, rounds: 12 }) > E.score({ won: true, resolve: 4, rounds: 9 }), 'wins rank by Resolve');
ok(E.score({ won: true, resolve: 5, rounds: 10 }) > E.score({ won: true, resolve: 5, rounds: 12 }), 'then fewer rounds');
ok(E.score({ won: false, wavesCleared: 2, destroyed: 0.1 }) > E.score({ won: false, wavesCleared: 1, destroyed: 0.9 }), 'losses rank by waves cleared');

console.log(`${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
