// Campaigns server checks (build session 2). Against a local server with the test clock on and a
// throwaway database (tests/declass/README, steps 3 and 4, with migrations 0001 to 0005), real catalog:
//   DB=<the local D1 sqlite file> node --import ./tests/declass/json-loader.mjs tests/campaigns/server.mjs
// Players C0 to C9 are created here. Runs are played by the engine's automatic player.
import { cookie } from '../declass/cookie.mjs';
import { DatabaseSync } from 'node:sqlite';
import campaign from '../../functions/_data/campaigns/1940-08-battle-of-britain.json' with { type: 'json' };
import loaners from '../../functions/_data/loaners.json' with { type: 'json' };
import * as E from '../../site/declass/campaigns/engine.js';
import { playRun } from './bot.mjs';
const BASE = 'http://localhost:8799';
const db = new DatabaseSync(process.env.DB);
let pass = 0, failN = 0;
const ok = (cond, msg) => { if (cond) pass++; else { failN++; console.log('FAIL:', msg); } };
const id = p => p + 'x'.repeat(32 - p.length);
for (const p of ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9']) db.prepare("INSERT OR IGNORE INTO players (id, created_at, tester) VALUES (?, '2026-11-01T00:00:00Z', 1)").run(id(p));
async function req(path, { player, now, body, headers = {} } = {}) {
  const h = { 'x-declass-key': 't', ...headers };
  if (player) h.cookie = cookie(id(player));
  if (now) h['x-declass-now'] = now;
  if (body) { h['content-type'] = 'application/json'; h.origin = BASE; }
  const r = await fetch(BASE + '/api/' + path, { method: body ? 'POST' : 'GET', headers: h, body: body ? JSON.stringify(body) : undefined });
  return { status: r.status, data: await r.json().catch(() => ({})) };
}
const L = Object.fromEntries(loaners.loaners.map(l => [l.id, l]));
// A Fighter Command deck of loaners (19 air or neutral loaners plus a second Hurricane flight).
const AIR = loaners.loaners.filter(l => l.series === 'home' || l.series === 'state' || l.branches.includes('air')).map(l => ({ loaner: l.id }));
const DECK = [...AIR, { loaner: 'a-hurricane-flight' }];
const NOW = '2026-11-07T18:00:00Z', NEXT = '2026-11-08T18:00:00Z';
const play = async (p, ch, now = NOW, deck = DECK, cheat = null) => {
  const s = await req('campaign/start', { player: p, now, body: { chapter: ch, deck } });
  if (s.status !== 200) return { start: s };
  const engDeck = s.data.deck;
  const r = playRun(campaign, ch, engDeck, s.data.seed);
  const choices = cheat ? cheat(r.choices) : r.choices;
  const f = await req('campaign/finish', { player: p, now, body: { ticket: s.data.ticket, choices } });
  return { start: s, run: r, finish: f };
};

// Signed out, and the campaign itself
{
  const r = await req('campaign', { now: NOW });
  ok(r.status === 200 && r.data.status === 'signin' && r.data.chapters.length === 3, 'signed out: the campaign shows, sign in to play');
  const a = await req('campaign', { player: 'C0', now: NOW });
  ok(a.data.status === 'open' && a.data.chapters[0].unlocked && !a.data.chapters[1].unlocked, 'chapter 1 open, chapter 2 locked until chapter 1 is won');
  ok(a.data.chapters[0].runsLeft === 3 && a.data.loaners.length === loaners.loaners.length, 'three runs a day, the loaners listed');
  ok(DECK.length === 20 && E.deckProblems(campaign, 1, DECK.map(p => L[p.loaner])).length === 0, 'the loaner deck is legal');
}

// Deck checks on the server
{
  const r1 = await req('campaign/start', { player: 'C1', now: NOW, body: { chapter: 1, deck: DECK.slice(0, 19) } });
  ok(r1.status === 400, 'a 19 card deck is refused');
  const r2 = await req('campaign/start', { player: 'C1', now: NOW, body: { chapter: 1, deck: [...DECK.slice(0, 19), { loaner: 'a-corvette' }] } });
  ok(r2.status === 400 && r2.data.problems.some(x => /air only/.test(x)), 'a sea loaner is refused in an air chapter, with the reason');
  const r3 = await req('campaign/start', { player: 'C1', now: NOW, body: { chapter: 1, deck: [...DECK.slice(0, 19), { card: '1941-10-17-kearny' }] } });
  ok(r3.status === 400 && r3.data.problems.some(x => /not in your dossier/.test(x)), 'a card not in the dossier is refused');
  db.prepare("INSERT INTO pulls (player_id, card_id, variant, finish, slot_key, pulled_at, signature, turned) VALUES (?, '1941-10-17-kearny', 'still', 'copper', 'test', '2026-11-01T00:00:00Z', '', 1)").run(id('C1'));
  const r4 = await req('campaign/start', { player: 'C1', now: NOW, body: { chapter: 1, deck: [...DECK.slice(0, 19), { card: '1941-10-17-kearny' }] } });
  ok(r4.status === 400 && r4.data.problems.some(x => /no number yet|1940 or earlier/.test(x)), 'a dossier card with no number (or from 1941) is refused');
  // The deck builder's reasons (build session 3): the same check as the start, for every released chapter.
  const v = await req('campaign', { player: 'C1', now: NOW });
  const k = v.data.cards.find(c => c.id === '1941-10-17-kearny'), cor = v.data.loaners.find(l => l.id === 'a-corvette'), hur = v.data.loaners.find(l => l.id === 'a-hurricane-flight');
  ok(k && /1940 or earlier/.test(k.why[1]) && Object.keys(k.why).length === 3, 'the campaign view says why a dossier card is greyed out, per chapter');
  ok(cor && /air only: machines and operations need the plane/.test(cor.why[1]) && hur && hur.why[1] === '', 'a sea loaner is greyed out with the reason; an air loaner fits');
  const r5 = await req('campaign/start', { player: 'C1', now: NOW, body: { chapter: 2, deck: DECK } });
  ok(r5.status === 409, 'chapter 2 cannot start while locked');
  ok(db.prepare('SELECT COUNT(*) AS n FROM campaign_runs WHERE player_id = ?').get(id('C1')).n === 0, 'refused starts use no runs');
}

// A full run, replayed by the server
{
  const r = await play('C2', 1);
  ok(r.start.status === 200 && r.start.data.runNo === 1 && r.start.data.runsLeft === 2, 'a run starts: run 1, two left');
  ok(r.finish.status === 200 && ['won', 'lost'].includes(r.finish.data.result), 'the run finishes');
  ok(r.finish.data.outcome && r.finish.data.outcome.won === r.run.state.over.won && r.finish.data.outcome.resolve === r.run.state.over.resolve, 'the server got the same result as the page');
  ok(r.finish.data.dayRank && r.finish.data.dayRank.players === 1, 'the day histogram counts the player');
  const again = await req('campaign/finish', { player: 'C2', now: NOW, body: { ticket: r.start.data.ticket, choices: r.run.choices } });
  ok(again.data.result === 'already', 'a run can be finished only once');
  const other = await req('campaign/finish', { player: 'C3', now: NOW, body: { ticket: r.start.data.ticket, choices: r.run.choices } });
  ok(other.status === 400, 'another player cannot use the ticket');
}

// The same run number gives everyone the same seed that day; the next run and the next day differ
{
  const a = await req('campaign/start', { player: 'C4', now: NOW, body: { chapter: 1, deck: DECK } });
  const b = await req('campaign/start', { player: 'C5', now: NOW, body: { chapter: 1, deck: DECK } });
  const c = await req('campaign/start', { player: 'C5', now: NOW, body: { chapter: 1, deck: DECK } });
  const d = await req('campaign/start', { player: 'C6', now: NEXT, body: { chapter: 1, deck: DECK } });
  ok(a.data.seed === b.data.seed, 'everyone\'s first run of the day has the same seed');
  ok(c.data.seed !== b.data.seed && c.data.runNo === 2, 'the second run has the next seed');
  ok(d.data.seed !== a.data.seed, 'the next day has new seeds');
}

// Cheating is refused
{
  const r = await play('C7', 1, NOW, DECK, ch => ch.slice(0, -3));
  ok(r.finish.status === 400 && r.finish.data.result === 'refused', 'an unfinished list of choices is refused');
  const r2 = await play('C7', 1, NOW, DECK, ch => { const x = ch.slice(); const k = x.findIndex(c => c.a === 'lock'); x.splice(k, 0, { a: 'place', card: 0 }); return x; });
  ok(r2.finish.status === 400, 'an illegal choice is refused');
  const row = db.prepare("SELECT status FROM campaign_runs WHERE player_id = ? ORDER BY started_at LIMIT 1").get(id('C7'));
  ok(row.status === 'refused', 'a refused run is marked and never ranked');
}

// Runs a day, and starting over buys nothing
{
  await play('C8', 1); await play('C8', 1); await play('C8', 1);
  const r = await req('campaign/start', { player: 'C8', now: NOW, body: { chapter: 1, deck: DECK } });
  ok(r.status === 409, 'a fourth run that day is refused');
  const n = await req('campaign/start', { player: 'C8', now: NEXT, body: { chapter: 1, deck: DECK } });
  ok(n.status === 200 && n.data.runNo === 1, 'the next day brings three new runs');
  const s = await req('campaign/start', { player: 'C9', now: NOW, body: { chapter: 1, deck: DECK } });
  const s2 = await req('campaign/start', { player: 'C9', now: NOW, body: { chapter: 1, deck: DECK } });
  ok(s2.data.runNo === 2, 'an abandoned run still counts');
}

// Winning unlocks the next chapter; best runs feed the histograms once per player
{
  let won = null;
  for (let k = 0; k < 4 && !won; k++) { const day = `2026-11-${String(10 + k).padStart(2, '0')}T18:00:00Z`; for (let j = 0; j < 3 && !won; j++) { const r = await play('C3', 1, day); if (r.finish.data.result === 'won') won = { r, day }; } }
  ok(won, 'the bot won chapter 1 within a few days');
  if (won) {
    ok(won.r.finish.data.unlocked === 2, 'winning chapter 1 unlocks chapter 2');
    const a = await req('campaign', { player: 'C3', now: won.day });
    ok(a.data.chapters[0].won && a.data.chapters[1].unlocked && !a.data.chapters[2].unlocked, 'chapter 2 unlocked, chapter 3 still locked');
    const c2 = await play('C3', 2, won.day);
    ok(c2.start.status === 200, 'chapter 2 can be played');
  }
  const counts = db.prepare("SELECT kind, k, SUM(n) AS n FROM campaign_ranks WHERE chapter = 1 GROUP BY kind, k").all();
  const chapter = counts.find(c => c.kind === 'chapter');
  const players = db.prepare("SELECT COUNT(DISTINCT player_id) AS n FROM campaign_runs WHERE chapter = 1 AND status = 'done'").get().n;
  ok(chapter && chapter.n === players, `the chapter histogram counts each player once (${chapter && chapter.n} of ${players})`);
  const bad = db.prepare("SELECT COUNT(*) AS n FROM campaign_ranks WHERE n < 0").get().n;
  ok(bad === 0, 'no histogram count goes below zero');
  const rk = await req('campaign/rank?chapter=1', { player: 'C3', now: won ? won.day : NOW });
  ok(rk.status === 200 && rk.data.chapter && rk.data.chapter.top >= 1 && rk.data.chapter.top <= 100, 'the rank endpoint gives a percentile');
}

// Two finishes of the same run at once save it once
{
  const s = await req('campaign/start', { player: 'C6', now: NOW, body: { chapter: 1, deck: DECK } });
  const r = playRun(campaign, 1, s.data.deck, s.data.seed);
  const both = await Promise.all([1, 2, 3].map(() => req('campaign/finish', { player: 'C6', now: NOW, body: { ticket: s.data.ticket, choices: r.choices } })));
  ok(both.filter(x => x.data.result === 'won' || x.data.result === 'lost').length === 1, 'three finishes at once count once');
}

// Release dates and the launch gate (the library itself, since the local test clock opens everything)
{
  const C = await import('../../functions/_lib/campaigns.js');
  const slot = { campaign, year: '2027', preview: false };
  const [c1, c2, c3] = campaign.chapters;
  ok(C.chapterOpensAt(slot, c2) === '2027-08-11T04:00:00Z', 'chapter 2 opens at midnight Eastern on 11 August');
  ok(!C.chapterReleased(slot, c2, new Date('2027-08-11T03:59:00Z')) && C.chapterReleased(slot, c2, new Date('2027-08-11T04:00:00Z')), 'not a minute early');
  const pc = C.publicChapter(slot, c3, new Date('2027-08-15T12:00:00Z'), new Map());
  ok(!pc.released && !pc.waves && !pc.intro, 'an unreleased chapter shows no enemy, intro, or debriefs');
  ok(C.publicChapter({ ...slot, preview: true }, c3, new Date('2027-01-01'), new Map()).released, 'a tester preview opens every chapter');
  const req0 = { headers: new Map([['x-campaigns-preview', '1']]) }; req0.headers.get = k => (k === 'x-campaigns-preview' ? '1' : null);
  ok(!C.CAMPAIGNS_LIVE, 'Campaigns is not live yet');
  ok(!C.campaignsOpen({}, req0, { tester: 0 }) && !C.campaignsOpen({}, { headers: { get: () => null } }, { tester: 1 }) && C.campaignsOpen({}, req0, { tester: 1 }), 'before launch only a tester sending the preview header gets in');
  ok(C.campaignFor(new Date('2027-08-05'), false) === null, 'no month is scheduled yet');
}
// Month end: ranks settle and Intel is paid by band, once (build session 5). On the local copy the test
// clock lets preview runs settle; on the real site only a scheduled month does.
{
  const C = await import('../../functions/_lib/campaigns.js');
  for (const p of ['D0', 'D1']) db.prepare("INSERT OR IGNORE INTO players (id, created_at, tester) VALUES (?, '2026-11-01T00:00:00Z', 1)").run(id(p));
  ok(C.monthEndsAt(campaign, '2026').toISOString() === '2026-09-01T04:00:00.000Z' && C.monthEndsAt({ ...campaign, month: 12 }, '2026').toISOString() === '2027-01-01T05:00:00.000Z', 'the month ends at midnight Eastern on the 1st');
  ok(C.bandOf(5) === 'top5' && C.bandOf(6) === 'top25' && C.bandOf(25) === 'top25' && C.bandOf(50) === 'top50' && C.bandOf(51) === 'finished', 'the bands: top 5%, top 25%, top 50%, everyone else who finished');
  const intel = p => db.prepare('SELECT intel FROM players WHERE id = ?').get(id(p)).intel;
  const AUG = '2026-08-20T18:00:00Z';
  await play('D0', 1, AUG);
  const i0 = intel('D0');
  const before = await req('state', { player: 'D0', now: '2026-09-01T03:59:00Z' });
  ok(before.status === 200 && before.data.campaignPaid.length === 0 && intel('D0') === i0, 'nothing is paid before midnight Eastern on the 1st');
  const after = await req('state', { player: 'D0', now: '2026-09-01T04:01:00Z' });
  const paid = after.data.campaignPaid || [];
  ok(paid.length === 1 && paid[0].chapter === 1 && C.BAND_INTEL[paid[0].band] === paid[0].intel && paid[0].top >= 1, 'after the month ends the chapter pays by band: ' + JSON.stringify(paid[0]));
  ok(intel('D0') === i0 + (paid[0] ? paid[0].intel : -1) && after.data.intel.balance === intel('D0'), 'the Intel is added to the balance');
  ok(db.prepare("SELECT COUNT(*) AS n FROM intel_log WHERE player_id = ? AND reason = 'campaign'").get(id('D0')).n === 1, 'and logged as Campaigns month end');
  const again = await Promise.all([1, 2, 3].map(() => req('state', { player: 'D0', now: '2026-09-02T12:00:00Z' })));
  ok(again.every(r => r.data.campaignPaid.length === 0) && intel('D0') === i0 + (paid[0] ? paid[0].intel : 0), 'paid once, even with three loads at once; the notice shows once');
  const none = await req('state', { player: 'D1', now: '2026-09-02T12:00:00Z' });
  ok(none.data.campaignPaid.length === 0 && intel('D1') === 0, 'no run, no payout');
  const v = await req('campaign', { player: 'D0', now: NOW });
  const ch1 = v.data.chapters[0];
  ok(ch1.rank && ch1.rank.month && ch1.rank.month.top >= 1 && v.data.bands && v.data.bands.top5 === C.BAND_INTEL.top5, 'the campaign view shows the chapter rank and the bands');
}
console.log(`${pass} passed, ${failN} failed`);
process.exit(failN ? 1 : 0);
