// Intercept server tests (27 Oct 2026). Run against a local server with the test clock on and a
// throwaway database (README, steps 3 and 4), with the real catalog:
//   DB=<the local D1 sqlite file> node tests/declass/intercept.mjs
// Players I0 to I9 are created here. Reads the dealt grids straight from the database to play them.
import { cookie } from './cookie.mjs';
import { DatabaseSync } from 'node:sqlite';
const BASE = 'http://localhost:8799';
const db = new DatabaseSync(process.env.DB);
let pass = 0, failN = 0;
const ok = (cond, msg) => { if (cond) pass++; else { failN++; console.log('FAIL:', msg); } };
const id = p => p + 'x'.repeat(32 - p.length);
for (const p of ['I0', 'I1', 'I2', 'I3', 'I4', 'I5', 'I6', 'I7', 'I8', 'I9']) {
  db.prepare("INSERT OR IGNORE INTO players (id, created_at, tester) VALUES (?, '2026-10-27T00:00:00Z', 1)").run(id(p));
}
async function req(path, { player, now, body } = {}) {
  const h = { 'x-declass-key': 't' };
  if (player) h.cookie = cookie(id(player));
  if (now) h['x-declass-now'] = now;
  if (body) { h['content-type'] = 'application/json'; h.origin = BASE; }
  const r = await fetch(BASE + '/api/' + path, { method: body ? 'POST' : 'GET', headers: h, body: body ? JSON.stringify(body) : undefined });
  return { status: r.status, data: await r.json().catch(() => ({})) };
}
const grid = (p, day) => JSON.parse(db.prepare('SELECT grid FROM intercept WHERE player_id = ? AND day = ?').get(id(p), day).grid);
const intel = p => db.prepare('SELECT intel FROM players WHERE id = ?').get(id(p)).intel;
const NOW = '2026-11-01T18:00:00Z', DAY = '2026-11-01';
const guess = (p, pick, now = NOW, day = DAY) => req('intercept/guess', { player: p, now, body: { day, pick } });
// A wrong pick: one card from each of three different groups.
const wrongPick = (g, k = 0) => [g.groups[0].idx[k % 3], g.groups[1].idx[(k + 1) % 3], g.groups[2].idx[(k + 2) % 3]];

// Signed out and before dealing.
let r = await req('intercept', { now: NOW });
ok(r.data.status === 'signin', 'signed out sees signin: ' + JSON.stringify(r.data));
r = await req('intercept', { player: 'I0', now: NOW });
ok(r.data.status === 'new' && r.data.closes === '2026-11-02T05:00:00Z', 'new before dealing, closes midnight Eastern: ' + JSON.stringify(r.data));
r = await req('state', { player: 'I0', now: NOW });
ok(r.data.intercept && r.data.intercept.status === 'new', 'state carries the tile summary');

// Deal, and no reroll.
r = await req('intercept/start', { player: 'I0', now: NOW, body: {} });
ok(r.status === 200 && r.data.puzzle.cards.length === 12, 'dealt 12 cards');
ok(r.data.puzzle.groups.length === 0 && r.data.puzzle.mistakes === 0, 'no links shown before any are found');
ok(!JSON.stringify(r.data).includes('"d":') && !JSON.stringify(r.data).includes('h-'), 'difficulty and group ids never leave the server');
const g0 = grid('I0', DAY);
ok(g0.groups.length === 4 && g0.groups.map(x => x.d).sort().join() === 'easy,hard,medium,medium', 'one easy, two medium, one hard');
ok(new Set(g0.cards.map(c => c.id)).size === 12, 'twelve different cards');
const r2 = await req('intercept/start', { player: 'I0', now: NOW, body: {} });
ok(JSON.stringify(r2.data.puzzle.cards) === JSON.stringify(r.data.puzzle.cards), 'a second start returns the same grid');
const par = await Promise.all([1, 2, 3, 4, 5, 6].map(() => req('intercept/start', { player: 'I1', now: NOW, body: {} })));
ok(par.every(x => x.status === 200 && JSON.stringify(x.data.puzzle.cards) === JSON.stringify(par[0].data.puzzle.cards)), 'six starts at once all get one grid');
ok(db.prepare('SELECT COUNT(*) AS n FROM intercept WHERE player_id = ?').get(id('I1')).n === 1, 'one row for I1');

// A perfect solve: three correct groups, the fourth locks on its own.
const before0 = intel('I0');
r = await guess('I0', g0.groups[0].idx);
ok(r.data.result === 'correct' && r.data.puzzle.groups.length === 1 && r.data.puzzle.groups[0].link === g0.groups[0].link, 'first link found and shown');
r = await guess('I0', g0.groups[0].idx);
ok(r.status === 400, 'a found group cannot be filed again');
r = await guess('I0', g0.groups[1].idx.slice().reverse());
ok(r.data.result === 'correct', 'order of the three does not matter');
r = await guess('I0', g0.groups[2].idx);
ok(r.data.result === 'correct' && r.data.puzzle.status === 'solved' && r.data.puzzle.found === 4, 'third link solves it, fourth locks itself');
ok(r.data.puzzle.score === 100 && r.data.puzzle.perfect && r.data.intel.gained === 18, 'perfect: 100 and 3 + 15 Intel: ' + JSON.stringify(r.data.intel));
ok(intel('I0') === before0 + 18, 'Intel credited once');
ok(db.prepare("SELECT COUNT(*) AS n FROM intel_log WHERE player_id = ? AND reason = 'intercept'").get(id('I0')).n === 1, 'one intel_log row');
r = await guess('I0', g0.groups[3].idx);
ok(r.data.result === 'finished', 'no guesses after the end');
r = await req('state', { player: 'I0', now: NOW });
ok(r.data.intercept.status === 'solved' && r.data.intercept.canClaim, 'tile shows solved, card to pick');
ok(r.data.intel.today >= 18, 'Intercept Intel counts in today');

// Claim: one card, Silver or better after a perfect solve, once only.
const par2 = await Promise.all([0, 1, 2, 3].map(i => req('intercept/claim', { player: 'I0', now: NOW, body: { day: DAY, index: i } })));
const won = par2.filter(x => x.status === 200);
ok(won.length === 1 && par2.filter(x => x.data.error === 'already claimed').length === 3, 'four claims at once: exactly one goes through');
const pull = won[0].data.pulls[0];
ok(pull && ['silver', 'gold', 'topsecret'].includes(pull.finish), 'perfect solve claim is Silver or better: ' + (pull && pull.finish));
ok(pull.slot === 'i:' + DAY && !pull.turned && pull.signed, 'claimed card waits to be turned, signed, under i:day');
ok(won[0].data.puzzle.claimed && won[0].data.puzzle.canClaim === false, 'puzzle records the claim');
r = await req('intercept/claim', { player: 'I0', now: NOW, body: { day: DAY, index: 5 } });
ok(r.data.error === 'already claimed', 'second claim refused');

// Mistakes: three wrong guesses end it and reveal everything; the same three again is not a mistake.
const g2 = (await req('intercept/start', { player: 'I2', now: NOW, body: {} }), grid('I2', DAY));
const before2 = intel('I2');
r = await guess('I2', wrongPick(g2, 0));
ok(r.data.result === 'wrong' && r.data.puzzle.mistakes === 1 && !('near' in r.data), 'wrong guess, one mistake, no near miss hint');
r = await guess('I2', wrongPick(g2, 0).reverse());
ok(r.data.result === 'tried' && r.data.puzzle.mistakes === 1, 'same three again: already tried, no mistake');
r = await guess('I2', g2.groups[3].idx);
ok(r.data.result === 'correct', 'a correct one between mistakes');
r = await guess('I2', wrongPick(g2, 1));
r = await guess('I2', wrongPick(g2, 2));
ok(r.data.puzzle.status === 'failed' && r.data.puzzle.mistakes === 3, 'three mistakes end it');
ok(r.data.puzzle.groups.length === 4 && r.data.puzzle.groups[0].found && r.data.puzzle.groups.slice(1).every(x => !x.found), 'all four links revealed, found ones first');
ok(r.data.intel.gained === 5 && intel('I2') === before2 + 5, 'not solved: 3 + 2 Intel');
r = await req('intercept/claim', { player: 'I2', now: NOW, body: { day: DAY, index: 0 } });
ok(r.data.error === 'not solved', 'no card when not solved');

// Scores with mistakes: 90, 80, 70.
for (const [p, m] of [['I3', 1], ['I4', 2]]) {
  await req('intercept/start', { player: p, now: NOW, body: {} });
  const g = grid(p, DAY);
  for (let k = 0; k < m; k++) await guess(p, wrongPick(g, k));
  await guess(p, g.groups[0].idx); await guess(p, g.groups[1].idx);
  r = await guess(p, g.groups[2].idx);
  ok(r.data.puzzle.score === 100 - 10 * m && r.data.intel.gained === 3 + (m === 1 ? 10 : 5), `solved with ${m} mistakes: ${r.data.puzzle.score}, +${r.data.intel.gained}`);
}

// Guesses fired at once: only one lands.
await req('intercept/start', { player: 'I5', now: NOW, body: {} });
const g5 = grid('I5', DAY);
const race = await Promise.all([0, 1, 2].map(k => guess('I5', wrongPick(g5, k))));
const m5 = db.prepare('SELECT mistakes, moves FROM intercept WHERE player_id = ?').get(id('I5'));
ok(m5.mistakes === m5.moves && race.filter(x => x.data.result === 'wrong').length === m5.mistakes, `parallel guesses counted exactly (${m5.mistakes} landed, others stale)`);

// Midnight Eastern: yesterday's file is closed, and a new one deals.
await req('intercept/start', { player: 'I6', now: '2026-11-02T04:50:00Z', body: {} });
r = await guess('I6', [0, 1, 2], '2026-11-02T05:01:00Z', DAY);
ok(r.data.error === 'expired', 'a guess after midnight Eastern on yesterday\'s file is refused');
r = await req('intercept', { player: 'I6', now: '2026-11-02T05:01:00Z' });
ok(r.data.status === 'new' && r.data.day === '2026-11-02', 'a new day, a new puzzle');

// Hard groups never repeat within 90 days while a fresh one exists.
const hards = [];
for (let d = 0; d < 6; d++) {
  const day = new Date(Date.parse('2026-11-03T17:00:00Z') + d * 86400000).toISOString();
  r = await req('intercept/start', { player: 'I7', now: day, body: {} });
  if (r.status !== 200) { ok(false, 'deal on ' + day + ': ' + JSON.stringify(r.data)); continue; }
  hards.push(grid('I7', day.slice(0, 10)).groups.find(x => x.d === 'hard').id);
}
// With the October catalog five hard groups can be dealt (h-aid-britain's three ships all print 1941,
// a giveaway). Once they're used up, the one seen longest ago comes back first.
const firstRepeat = hards.findIndex((h, i) => hards.indexOf(h) !== i);
ok(firstRepeat === -1 || (firstRepeat >= 5 && hards[firstRepeat] === hards[0]), 'no hard repeat while a fresh one deals; then the oldest: ' + hards.join(' '));
ok(db.prepare('SELECT COUNT(*) AS n FROM intercept_seen WHERE player_id = ?').get(id('I7')).n === new Set(hards).size, 'hard groups seen recorded');

// Playing does not touch the streak; Delete my dossier removes Intercept rows.
ok(db.prepare('SELECT streak FROM players WHERE id = ?').get(id('I7')).streak === 0, 'no streak from Intercept');
r = await req('delete', { player: 'I7', now: NOW, body: {} });
ok(db.prepare('SELECT COUNT(*) AS n FROM intercept WHERE player_id = ?').get(id('I7')).n === 0 && db.prepare('SELECT COUNT(*) AS n FROM intercept_seen WHERE player_id = ?').get(id('I7')).n === 0, 'delete removes the puzzle rows and the seen list');

console.log(`${pass} passed, ${failN} failed`);
process.exit(failN ? 1 : 0);
