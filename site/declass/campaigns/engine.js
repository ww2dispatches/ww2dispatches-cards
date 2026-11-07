// Campaigns rules engine (build session 1, 6 Nov 2026). Campaigns Build doc, "The engine".
// One plain module with every rule and no screen code. The page plays with it; the server imports the
// same file to replay a finished run from its seed and its list of choices, so the game and the ranking
// can never disagree. Nothing here may use Math.random, the clock, or the page: the same campaign, deck,
// seed, and choices must always give the same result.
//
// Rules: the Campaigns doc ("The rules", "Starting numbers", "The enemy"), as played in test version 12.
// A run is one chapter. State is plain JSON so it can be copied, saved, or sent.

export const ENGINE_VERSION = 1;

export const RULES = {
  startResolve: 10, resolveCap: 15, deckSize: 20, hand: 5, draw: 1,
  supplyStart: 2, supplyMax: 7, line: 5,
};

// Statecraft keywords and their fixed reach (Decided 5 Nov 2026). Catalog values: lend, backchannel, ultimatum, evac.
export const REACH = { lend: 3, ultimatum: 5, evac: 2 };
export const BACK_CHANNEL_DRAW = 2;
export const SERIES = { machine: 'blue', operation: 'battle', rally: 'home', statecraft: 'state' };

// ---------- seeded shuffle ----------
function hashSeed(s) {
  let h = 1779033703 ^ String(s).length;
  for (const ch of String(s)) { h = Math.imul(h ^ ch.codePointAt(0), 3432918353); h = (h << 13) | (h >>> 19); }
  return (h ^ (h >>> 16)) >>> 0;
}
function nextRandom(st) { // mulberry32, the state lives in the run so a copy of the run copies the stream
  let t = (st.rng = (st.rng + 0x6D2B79F5) >>> 0);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}
function shuffle(st, a) {
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(nextRandom(st) * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}

// ---------- setup ----------
// deck: array of cards { id, series: 'blue'|'battle'|'home'|'state', value: 1..7, branches: [...], keyword }
// Cards are referred to by their place in the deck (0 to 19), so two copies of a loaner never collide.
export function deckProblems(campaign, chapterN, deck, rules = RULES) {
  const ch = chapterOf(campaign, chapterN); const out = [];
  if (!ch) return ['No such chapter.'];
  if (deck.length !== rules.deckSize) out.push(`A deck has ${rules.deckSize} cards; this one has ${deck.length}.`);
  deck.forEach((c, i) => {
    if (!c || !SERIES_OK.has(c.series)) out.push(`Card ${i + 1} can't be played in Campaigns.`);
    else if (c.noPlay) out.push(`${c.title || 'Card ' + (i + 1)} can never be played.`);
    else if (!(c.value >= 1 && c.value <= 7)) out.push(`${c.title || 'Card ' + (i + 1)} has no number yet.`);
    else if (!fitsChapter(ch, c)) out.push(`${c.title || 'Card ' + (i + 1)} has no branch that fights in this chapter.`);
  });
  return out;
}
const SERIES_OK = new Set(['blue', 'battle', 'home', 'state']);
export function chapterOf(campaign, n) { return (campaign.chapters || []).find(c => c.n === n) || null; }
export function fitsChapter(ch, c) {
  if (c.series !== 'blue' && c.series !== 'battle') return true;
  return (c.branches || []).some(b => ch.branches.includes(b));
}

export function newRun(campaign, chapterN, deck, seed, rules = RULES) {
  const ch = chapterOf(campaign, chapterN);
  if (!ch) throw new Error('No such chapter');
  const st = {
    v: ENGINE_VERSION, campaignId: campaign.id, chapter: chapterN, seed: String(seed),
    rng: hashSeed(campaign.id + '|' + chapterN + '|' + seed),
    rules: { ...rules, startResolve: campaign.startResolve ?? rules.startResolve },
    calmRounds: ch.calm ? ch.calm.rounds : 0, twist: ch.twist ? ch.twist.id : null,
    cards: deck.map(c => ({ series: c.series, value: c.value, branches: c.branches || [], keyword: c.keyword || null })),
    round: 1, phase: 'opening', wave: 0, waveRounds: 0, uid: 1,
    resolve: campaign.startResolve ?? rules.startResolve, supply: 0, scUsed: false, mulliganed: false,
    draw: [], hand: [], lost: [], line: [], units: [], arrived: [], blocks: {}, delays: {},
    over: null, events: [],
  };
  st.units = waveOf(campaign, st).units.map(u => freshUnit(st, u));
  dealOpening(st);
  st.supply = supplyFor(st, 1);
  return st;
}
function waveOf(campaign, st) { return chapterOf(campaign, st.chapter).waves[st.wave]; }
function freshUnit(st, u) {
  return { uid: 'u' + (st.uid++), id: u.id, name: u.name, piece: u.piece || null, st: u.strength, max: u.strength,
    script: u.script.slice(), i: 0, delayedNext: null, escort: !!u.escort, airfield: !!u.airfield };
}
function dealOpening(st) {
  st.draw = shuffle(st, st.cards.map((_, i) => i));
  st.hand = st.draw.splice(0, st.rules.hand);
  const ok = i => st.cards[i].series === 'blue' && st.cards[i].value <= supplyFor(st, 1);
  if (!st.hand.some(ok)) {
    const j = st.draw.findIndex(ok);
    if (j >= 0) { st.draw.push(st.hand.pop()); st.hand.push(st.draw.splice(j, 1)[0]); }
  }
}
export function supplyFor(st, round) { return Math.min(st.rules.supplyStart + round - 1, st.rules.supplyMax); }

// ---------- reading the state ----------
export const alive = st => st.units.filter(u => u.st > 0);
const unit = (st, uid) => st.units.find(u => u.uid === uid);
const machine = (st, uid) => st.line.find(m => m.uid === uid);
const scriptAtk = u => u.script[u.i % u.script.length];
export const nextAttack = u => (u.delayedNext != null ? u.delayedNext : scriptAtk(u));
export const opValue = (st, m) => (m.op != null ? st.cards[m.op].value : 0);
export function calm(st) { return st.wave === 0 && st.round <= st.calmRounds; }
// the attack landing in this raid
export function incoming(st, u) { if (st.phase !== 'enemy' || u.st <= 0 || st.delays[u.uid] != null) return 0; return nextAttack(u); }
// the attack coming in the next raid (0 if that raid is still a calm round)
export function coming(st, u) { if (u.st <= 0 || st.delays[u.uid] != null || st.round + 1 <= st.calmRounds) return 0; return nextAttack(u); }
export const canBlock = m => m.state === 'ready';
export const canAttack = (st, m) => m.state === 'ready' && m.op != null && !m.fresh && !calm(st);
export function blockersOf(st, uid) { return (st.blocks[uid] || []).map(id => machine(st, id)).filter(Boolean); }
export function blockingWhat(st, m) { return Object.keys(st.blocks).find(k => st.blocks[k].includes(m.uid)) || null; }
function shares(a, b) { return a.some(x => b.includes(x)); }
export function fitsMachine(st, m, card) { return shares(st.cards[m.card].branches, card.branches); }
function plannedOn(st, uid, except) { return st.line.filter(m => m !== except && m.mode === 'attack' && m.target === uid).reduce((a, m) => a + opValue(st, m), 0); }
export function targetsFor(st, m) {
  const al = alive(st);
  const es = al.filter(u => u.escort && plannedOn(st, u.uid, m) < u.st);
  return es.length ? es : al;
}
export function pendingReinforcements(campaign, st) {
  return waveOf(campaign, st).reinforcements.filter((r, i) => r.after > st.waveRounds && !st.arrived.includes(i));
}
export function lendable(campaign, st) {
  const ch = chapterOf(campaign, st.chapter);
  return st.draw.filter(i => { const c = st.cards[i]; return c.series === 'blue' && c.value <= REACH.lend && fitsChapter(ch, c); });
}
export const evacuable = st => st.lost.filter(i => st.cards[i].value <= REACH.evac);
export function ultimatumTargets(st) { return st.phase === 'enemy' ? alive(st).filter(u => incoming(st, u) > 0 && incoming(st, u) <= REACH.ultimatum) : []; }

// Why a card in hand can't be played right now ('' if it can). The page shows the reason; the engine
// refuses the same play for the same reason.
export function whyNot(campaign, st, i) {
  const c = st.cards[i];
  if (st.over) return 'The run is over.';
  if (st.phase === 'opening') return 'Keep your opening hand first.';
  if (!st.hand.includes(i)) return 'That card is not in your hand.';
  const ult = c.series === 'state' && c.keyword === 'ultimatum';
  if (st.phase === 'enemy' && !ult) return 'Only an Ultimatum can be played during the raid.';
  if (st.phase === 'yours' && ult) return 'An Ultimatum is played when the raid comes in.';
  if (c.series !== 'state' && c.value > st.supply) return `Not enough Supply: it costs ${c.value} and you have ${st.supply} left.`;
  if (c.series === 'blue' && st.line.length >= st.rules.line) return 'Your line is full.';
  if (c.series === 'battle') {
    if (!st.line.some(m => fitsMachine(st, m, c))) return 'No machine on your line shares a branch with it.';
    if (!st.line.some(m => fitsMachine(st, m, c) && !m.fresh)) return 'That machine was just placed and needs a turn to set up.';
  }
  if (c.series === 'state') {
    if (st.scUsed) return 'One Statecraft card a round, raid and turn together.';
    if (c.keyword === 'lend') { if (st.line.length >= st.rules.line) return 'Your line is full.'; if (!lendable(campaign, st).length) return `No machine of ${REACH.lend} or less left in your deck.`; }
    else if (c.keyword === 'evac') { if (!evacuable(st).length) return `No knocked out machine of ${REACH.evac} or less to bring back.`; }
    else if (c.keyword === 'backchannel') { if (!st.draw.length) return 'Your deck is empty.'; }
    else if (c.keyword === 'ultimatum') { if (!ultimatumTargets(st).length) return `No attack of ${REACH.ultimatum} or less is coming in this raid.`; }
    else return 'This Statecraft card has no keyword yet.';
  }
  if (c.series === 'home' && st.resolve >= st.rules.resolveCap && !st.line.some(m => m.arm < st.cards[m.card].value)) return 'Resolve is full and no machine needs repair.';
  return '';
}

// ---------- choices ----------
// act(campaign, state, choice) changes the state and returns { ok, error }. Every choice is checked; a
// refused choice changes nothing. The choices a page can send:
//   { a:'mulligan' } { a:'keep' }                                        the opening hand
//   { a:'place', card } { a:'attach', card, machine } { a:'rally', card, to:'resolve'|machine }
//   { a:'lend', card, pick } { a:'backchannel', card } { a:'evac', card, pick }   your phase
//   { a:'ultimatum', card, unit } { a:'block', unit, machines:[...] } { a:'lock' }  the raid
//   { a:'attack', machine, unit } { a:'hold', machine } { a:'end' }      your phase
// card and pick are places in the deck (0 to 19); machine and unit are the uids in the state.
export function act(campaign, st, ch) {
  const no = error => ({ ok: false, error });
  if (st.over) return no('The run is over.');
  st.events = [];
  const a = ch && ch.a;
  if (st.phase === 'opening') {
    if (a === 'mulligan') { if (st.mulliganed) return no('One mulligan a run.'); st.mulliganed = true; dealOpening(st); return { ok: true }; }
    if (a === 'keep') { st.phase = 'yours'; return { ok: true }; }
    return no('Keep your opening hand first.');
  }
  if (['place', 'attach', 'rally', 'lend', 'backchannel', 'evac', 'ultimatum'].includes(a)) {
    const i = ch.card; if (!Number.isInteger(i) || !st.cards[i]) return no('No such card.');
    const why = whyNot(campaign, st, i); if (why) return no(why);
    const c = st.cards[i];
    const kind = { place: 'blue', attach: 'battle', rally: 'home' }[a];
    if (kind && c.series !== kind) return no('That card does not do that.');
    if (['lend', 'backchannel', 'evac', 'ultimatum'].includes(a) && c.keyword !== a) return no('That card does not do that.');
    if (a === 'place') { spend(st, i); st.line.push(newMachine(st, i)); return { ok: true }; }
    if (a === 'attach') {
      const m = machine(st, ch.machine); if (!m || !fitsMachine(st, m, c) || m.fresh) return no('That machine cannot take this operation.');
      spend(st, i); if (m.op != null) st.discard = (st.discard || []).concat([m.op]); m.op = i; return { ok: true };
    }
    if (a === 'rally') {
      if (ch.to === 'resolve') { if (st.resolve >= st.rules.resolveCap) return no('Resolve is full.'); spend(st, i); st.resolve = Math.min(st.rules.resolveCap, st.resolve + c.value); return { ok: true }; }
      const m = machine(st, ch.to); if (!m || m.arm >= st.cards[m.card].value) return no('That machine needs no repair.');
      spend(st, i); m.arm = Math.min(st.cards[m.card].value, m.arm + c.value); return { ok: true };
    }
    if (a === 'lend') {
      if (!lendable(campaign, st).includes(ch.pick)) return no('That machine cannot come in by Lend Lease.');
      spend(st, i); st.scUsed = true; st.draw.splice(st.draw.indexOf(ch.pick), 1); st.line.push(newMachine(st, ch.pick)); return { ok: true };
    }
    if (a === 'backchannel') { spend(st, i); st.scUsed = true; for (let k = 0; k < BACK_CHANNEL_DRAW && st.draw.length; k++) st.hand.push(st.draw.shift()); return { ok: true }; }
    if (a === 'evac') {
      if (!evacuable(st).includes(ch.pick)) return no('That machine cannot be evacuated.');
      spend(st, i); st.scUsed = true; st.lost.splice(st.lost.indexOf(ch.pick), 1); st.hand.push(ch.pick); return { ok: true };
    }
    if (a === 'ultimatum') {
      const u = unit(st, ch.unit); if (!u || !ultimatumTargets(st).includes(u)) return no('That attack cannot be put off.');
      spend(st, i); st.scUsed = true; st.delays[u.uid] = i; delete st.blocks[u.uid]; return { ok: true };
    }
  }
  if (a === 'block') {
    if (st.phase !== 'enemy') return no('Blocks are chosen when the raid comes in.');
    const u = unit(st, ch.unit); if (!u || incoming(st, u) <= 0) return no('That unit is not attacking.');
    const ms = (ch.machines || []).map(id => machine(st, id));
    if (ms.some(m => !m || !canBlock(m)) || new Set(ch.machines).size !== ms.length) return no('Only Ready machines can block.');
    for (const k of Object.keys(st.blocks)) { st.blocks[k] = st.blocks[k].filter(id => !ch.machines.includes(id)); if (!st.blocks[k].length) delete st.blocks[k]; }
    if (ms.length) st.blocks[u.uid] = ch.machines.slice(); else delete st.blocks[u.uid];
    return { ok: true };
  }
  if (a === 'lock') {
    if (st.phase !== 'enemy') return no('There is no raid to lock in.');
    resolveRaid(campaign, st); return { ok: true };
  }
  if (a === 'attack' || a === 'hold') {
    if (st.phase !== 'yours') return no('Attacks are chosen in your turn.');
    const m = machine(st, ch.machine); if (!m) return no('No such machine.');
    if (a === 'hold') { m.mode = 'hold'; m.target = null; return { ok: true }; }
    if (!canAttack(st, m)) return no('That machine cannot attack now.');
    const u = unit(st, ch.unit); if (!u || !targetsFor(st, m).includes(u)) return no('Escorts must be attacked first.');
    m.mode = 'attack'; m.target = u.uid; return { ok: true };
  }
  if (a === 'end') {
    if (st.phase !== 'yours') return no('It is not your turn.');
    endTurn(campaign, st); return { ok: true };
  }
  return no('Unknown choice.');
}
function spend(st, i) {
  const c = st.cards[i];
  st.supply -= c.series === 'state' ? 0 : c.value;
  st.hand.splice(st.hand.indexOf(i), 1);
  if (c.series === 'home' || c.series === 'state') st.discard = (st.discard || []).concat([i]);
}
function newMachine(st, i) { return { uid: 'm' + (st.uid++), card: i, arm: st.cards[i].value, op: null, state: 'ready', fresh: true, mode: 'hold', target: null }; }

// ---------- the raid ----------
function resolveRaid(campaign, st) {
  const ev = st.events;
  // Twist: airfield raids (Battle of Britain chapter 3). An unblocked airfield raid also damages the
  // strongest Rearming machine on the ground, never below 1 armor; its full attack still hits Resolve.
  if (st.twist === 'airfield_raids') {
    for (const u of alive(st)) {
      if (!u.airfield || st.delays[u.uid] != null || (st.blocks[u.uid] || []).length) continue;
      const a = nextAttack(u); if (a <= 0) continue;
      const tg = st.line.filter(m => m.state === 'out' && m.arm > 0).sort((x, y) => y.arm - x.arm)[0];
      if (tg) { const b = tg.arm; tg.arm -= Math.min(a, tg.arm - 1); if (tg.arm < b) ev.push({ t: 'ground', unit: u.uid, machine: tg.uid, from: b, to: tg.arm }); }
    }
  }
  for (const u of alive(st)) {
    if (st.delays[u.uid] != null) {
      const a = nextAttack(u); if (u.delayedNext == null) u.i++; u.delayedNext = a + 1;
      ev.push({ t: 'heldOff', unit: u.uid, attack: a, back: a + 1, card: st.delays[u.uid] }); continue;
    }
    let a; if (u.delayedNext != null) { a = u.delayedNext; u.delayedNext = null; } else { a = scriptAtk(u); u.i++; }
    if (a <= 0) { ev.push({ t: 'climb', unit: u.uid }); continue; }
    const bs = blockersOf(st, u.uid).filter(m => m.arm > 0);
    let left = a, hit = 0; const parts = [];
    for (const m of bs) { const b = m.arm, take = Math.min(left, m.arm); m.arm -= take; left -= take; m.state = 'blocked'; parts.push({ machine: m.uid, from: b, to: m.arm }); hit += opValue(st, m); }
    const r0 = st.resolve; st.resolve -= left;
    let hitBack = null;
    if (hit) { const s0 = u.st; u.st = Math.max(0, u.st - hit); hitBack = { from: s0, to: u.st }; }
    ev.push({ t: 'attack', unit: u.uid, attack: a, blocks: parts, through: left, resolve: [r0, Math.max(0, st.resolve)], hitBack });
  }
  knockOut(st);
  st.resolve = Math.max(0, st.resolve);
  st.blocks = {}; st.delays = {};
  if (st.resolve <= 0) { finish(campaign, st, false); return; }
  earlyReinforcements(campaign, st);
  if (waveCleared(campaign, st)) { if (advanceWave(campaign, st)) return; }
  startYourPhase(st);
}
function knockOut(st) {
  for (const m of st.line.filter(m => m.arm <= 0)) {
    st.lost.push(m.card);
    if (m.op != null) st.discard = (st.discard || []).concat([m.op]);
    st.events.push({ t: 'knockedOut', machine: m.uid, card: m.card, op: m.op });
  }
  st.line = st.line.filter(m => m.arm > 0);
}
function startYourPhase(st) {
  st.phase = 'yours';
  if (st.round > 1) for (let k = 0; k < st.rules.draw; k++) if (st.draw.length) st.hand.push(st.draw.shift());
  st.supply = supplyFor(st, st.round);
  for (const m of st.line) { m.mode = 'hold'; m.target = null; if (m.state === 'out') m.state = 'ready'; }
}

// ---------- your attacks and the end of the round ----------
function endTurn(campaign, st) {
  const ev = st.events;
  for (const m of st.line.filter(m => m.mode === 'attack' && m.op != null)) {
    let t = unit(st, m.target);
    if (!t || t.st <= 0) { const al = alive(st); const es = al.filter(u => u.escort); t = (es.length ? es : al).sort((a, b) => a.st - b.st)[0]; }
    m.state = 'attacked'; m.mode = 'hold';
    if (!t) continue;
    const b = t.st; t.st = Math.max(0, t.st - opValue(st, m));
    ev.push({ t: 'strike', machine: m.uid, unit: t.uid, from: b, to: t.st });
  }
  earlyReinforcements(campaign, st);
  if (waveCleared(campaign, st)) { if (advanceWave(campaign, st)) return; }
  else {
    st.waveRounds++;
    const w = waveOf(campaign, st);
    w.reinforcements.forEach((r, i) => { if (r.after === st.waveRounds && !st.arrived.includes(i)) { st.arrived.push(i); const u = freshUnit(st, r.unit); st.units.push(u); ev.push({ t: 'arrive', unit: u.uid, why: 'reinforcement' }); } });
    const sw = chapterOf(campaign, st.chapter).sweep;
    if (sw && st.waveRounds % sw.every === 0) { const u = freshUnit(st, sw.unit); st.units.push(u); ev.push({ t: 'arrive', unit: u.uid, why: 'sweep' }); }
  }
  for (const m of st.line) { m.fresh = false; if (m.state === 'blocked') m.state = 'ready'; else if (m.state === 'attacked') m.state = 'out'; }
  st.round++; st.scUsed = false; st.blocks = {}; st.delays = {};
  if (calm(st)) startYourPhase(st); else st.phase = 'enemy';
}
function earlyReinforcements(campaign, st) {
  if (alive(st).length) return;
  waveOf(campaign, st).reinforcements.forEach((r, i) => {
    if (r.after > st.waveRounds && !st.arrived.includes(i)) { st.arrived.push(i); const u = freshUnit(st, r.unit); st.units.push(u); st.events.push({ t: 'arrive', unit: u.uid, why: 'early' }); }
  });
}
function waveCleared(campaign, st) { return !alive(st).length && !pendingReinforcements(campaign, st).length; }
// returns true when the run is over (the last wave was cleared)
function advanceWave(campaign, st) {
  const ch = chapterOf(campaign, st.chapter);
  st.events.push({ t: 'waveCleared', wave: st.wave });
  if (st.wave === ch.waves.length - 1) { finish(campaign, st, true); return true; }
  st.wave++; st.waveRounds = 0; st.arrived = []; st.blocks = {}; st.delays = {};
  st.units = waveOf(campaign, st).units.map(u => freshUnit(st, u));
  return false;
}

// ---------- the result ----------
function finish(campaign, st, won) {
  const ch = chapterOf(campaign, st.chapter);
  const w = waveOf(campaign, st);
  const total = w.units.reduce((a, u) => a + u.strength, 0) + w.reinforcements.reduce((a, r) => a + r.unit.strength, 0);
  const left = won ? 0 : alive(st).reduce((a, u) => a + u.st, 0) + pendingReinforcements(campaign, st).reduce((a, r) => a + r.unit.strength, 0);
  st.over = {
    won, resolve: won ? st.resolve : 0, rounds: st.round, wavesCleared: won ? ch.waves.length : st.wave,
    destroyed: won ? 1 : Math.max(0, Math.min(1, 1 - left / Math.max(1, total))),
    benchmark: ch.benchmark, beatHistory: won && st.resolve > ch.benchmark,
  };
  st.phase = 'over';
}
// One number that orders every run, highest best: every win above every loss; wins by Resolve, then
// fewer rounds; losses by waves cleared, then the share of the current wave destroyed (Campaigns doc, Ranking).
export function score(over) {
  if (!over) return 0;
  if (over.won) return 1_000_000 + over.resolve * 1000 + Math.max(0, 999 - over.rounds);
  return over.wavesCleared * 1000 + Math.round(over.destroyed * 999);
}

// ---------- replay (the server's check) ----------
export function replay(campaign, chapterN, deck, seed, choices, rules = RULES) {
  const st = newRun(campaign, chapterN, deck, seed, rules);
  for (let k = 0; k < choices.length; k++) {
    const r = act(campaign, st, choices[k]);
    if (!r.ok) return { ok: false, error: `Choice ${k + 1} was refused: ${r.error}`, state: st };
    if (st.over && k < choices.length - 1) return { ok: false, error: 'Choices after the end of the run.', state: st };
  }
  if (!st.over) return { ok: false, error: 'The run is not finished.', state: st };
  return { ok: true, result: st.over, score: score(st.over), state: st };
}

export function copy(st) { return JSON.parse(JSON.stringify(st)); }
