// Campaigns page checks (build session 3). Against the same local server as server.mjs, in a phone sized
// headless browser, signed in as test player B (a tester holding a few cards):
//   DB=<the local D1 sqlite file> PLAYWRIGHT=<path to playwright's index.mjs> node tests/campaigns/page.mjs
// Walks the door, the month, a chapter, the deck builder, a run's opening hand and mulligan, the calm
// opening, a raid with a forecast that must come true, then plays the whole run out by tapping and checks the
// end screen and that the server replayed and saved it. Fails on any page error. SHOTS=<dir> saves a screenshot of each step.
import { cookie } from '../declass/cookie.mjs';
import { DatabaseSync } from 'node:sqlite';
const { chromium } = await import(process.env.PLAYWRIGHT || 'playwright');
const BASE = 'http://localhost:8799', P = 'B' + 'x'.repeat(31);
const db = new DatabaseSync(process.env.DB);
db.prepare("INSERT OR IGNORE INTO players (id, created_at, tester) VALUES (?, '2026-11-01T00:00:00Z', 1)").run(P);
for (const t of ['campaign_runs', 'campaign_progress', 'campaign_day_best', 'campaign_payouts']) { try { db.prepare(`DELETE FROM ${t} WHERE player_id = ?`).run(P); } catch (e) {} } // a fresh start for player B
let pass = 0, failN = 0;
const ok = (cond, msg) => { if (cond) pass++; else { failN++; console.log('FAIL:', msg); } };

const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
const [ck, cv] = cookie(P).split(/=(.*)/s);
await ctx.addCookies([{ name: ck, value: cv, domain: 'localhost', path: '/' }]);
const page = await ctx.newPage();
await page.addInitScript(() => { try { localStorage.setItem('declass_coach', JSON.stringify({ tour: 1, 'fm-lastcall': 1 })); } catch (e) {} });
const errs = [];
page.on('pageerror', e => errs.push(e.message));
let n = 0;
const shot = async name => { if (process.env.SHOTS) { await page.waitForTimeout(400); await page.screenshot({ path: `${process.env.SHOTS}/${String(++n).padStart(2, '0')}-${name}.png` }); } };
const text = sel => page.$eval(sel, el => el.textContent);
// Lifting a card redraws the table, so hand cards are found again by their place in the deck each time.
const litCards = () => page.$$eval('.hcard.lit', els => els.map(e => e.dataset.h));
const liftCard = h => page.click(`.hcard[data-h="${h}"]`);
const dropCard = () => page.click('#lbX').catch(() => {});

// The door only for a preview tester
await page.goto(BASE + '/declass?key=t');
await page.waitForSelector('#sHome.on', { timeout: 15000 });
await page.waitForTimeout(800);
ok(!(await page.$('#cmpTile')), 'no Campaigns door without the preview setting');
await page.goto(BASE + '/declass?campaigns=preview');
await page.waitForSelector('#cmpTile', { timeout: 15000 });
ok(/Chapter 1/.test(await text('#cmpTile')), 'the door names the open chapter');
await shot('home');

// The month, then chapter 1
await page.click('#cmpTile');
await page.waitForSelector('.chap');
ok((await page.$$('.chap')).length === 3, 'three chapters');
ok(/Win chapter 1 to open it/.test(await text('[data-ch="2"]')), 'chapter 2 waits for a win in chapter 1');
await shot('month');
await page.click('[data-ch="1"]');
ok(/came through the Channel battle at a Resolve of 6/.test(await text('#cmpBody')), 'the briefing gives the mark to beat in full words');
ok((await page.$$('.cfiles li')).length === 3, 'three files');
await shot('chapter');

// The deck builder
await page.click('#chGo');
ok(Boolean(await page.$('#dkSug1')), 'a new player is offered the suggested deck first');
ok(await page.$eval('#dkStart', el => el.disabled), 'Start waits for a full deck');
await page.click('#dkSug1');
ok(/^20/.test(await text('.dkn')), 'the suggested deck has 20 cards');
ok(/A balanced deck: 6 machines, 6 operations, 4 Home Front, 4 Statecraft/.test(await text('.dknotes')), 'the plain words check passes it');
ok(await page.$$eval('.ptile.no .pstamp', els => els.some(e => /NOT IN THIS CAMPAIGN/.test(e.textContent))), 'sea and land loaners are stamped NOT IN THIS CAMPAIGN');
await shot('deck');
// take machines out: the check speaks up
for (let k = 0; k < 3; k++) await page.click('.dchip >> nth=0');
ok(/machines?\. Most winning decks carry at least 6/.test(await text('.dknotes')), 'too few machines is said in plain words');
await page.click('#dkSug');
ok(/^20/.test(await text('.dkn')), 'Suggested refills the deck');
await page.click('.ptile.no >> nth=0');
ok(/air only|1940 or earlier|no number/.test(await text('#sheetCard')), 'tapping a greyed out card says why');
await page.click('#sheet [data-close]');

// Start: the opening hand and the one mulligan
await page.click('#dkStart');
await page.click('#cmpStartGo');
await page.waitForSelector('.ohand');
ok((await page.$$('.orow .cface')).length === 5, 'five cards in the opening hand');
await shot('opening');
await page.click('#ohMull');
ok(await page.$eval('#ohMull', el => el.disabled), 'one mulligan a run');
const run = await page.evaluate(() => JSON.parse(localStorage.getItem('declass_cmp_run')));
ok(run && run.choices.length === 1 && run.choices[0].a === 'mulligan' && run.deck.length === 20, 'the run and its choices are kept in this browser');
await page.click('#ohKeep');
await page.waitForSelector('#cmpTele:not([hidden])');
ok(/ALL QUIET/.test(await text('#cmpTele')) && /YOUR TURN/.test(await text('.tlamp')) && /first raid in round 3/.test(await text('.tlamp')), 'the calm opening: ALL QUIET, your turn, first raid in round 3');
ok((await page.$$('.band.far .epiece')).length === 2 && (await page.$$('.band.chan .epiece')).length === 0, 'the first wave waits over France, the Channel is empty');
await shot('calm');
await page.click('#cmpTele');

// Round 1: put a machine down (the engine checks every play)
let placed = false;
for (const h of await litCards()) { await liftCard(h); const p = await page.$('.lbplay'); if (p && /Put on your line/.test(await p.textContent())) { await p.click(); placed = true; break; } await dropCard(); }
ok(placed && (await page.$$('.lrow .lpiece.fresh')).length === 1, 'a machine goes on the line, SETTING UP');
ok(/0\/2|1\/2/.test(await text('.ttile.sup')), 'Supply goes down by its cost');
await shot('placed');
// Undo it, then play it again
await page.click('#cmpMenu'); await page.click('#mUndo');
ok((await page.$$('.lrow .lpiece')).length === 0, 'Undo takes the move back');
for (const h of await litCards()) { await liftCard(h); const p = await page.$('.lslot.aim'); if (p) { await p.click(); break; } await dropCard(); }
// A reload picks the run up where it was
await page.reload();
await page.waitForSelector('#cmpTile');
await page.click('#cmpTile');
await page.waitForSelector('#cmpResume');
await page.click('#cmpResume');
ok((await page.$$('.lrow .lpiece')).length === 1, 'a reloaded page picks the run up where it was');
await page.click('#cmpAct');
ok(/Round 2|round 3/.test(await text('.tlamp')) && (await page.$$('.lrow .lpiece.fresh')).length === 0, 'End turn: round 2, the machine has set up');
// Arming by tapping the machine (Brian, 6 Nov 2026): a lifted operation lights the machines it can go on
let armed = null;
for (const h of await litCards()) {
  await liftCard(h);
  const m = await page.$('.lrow .lpiece.aim');
  if (m && /ATTACK/.test(await m.textContent())) { await shot('aim'); await m.click(); armed = true; break; }
  await dropCard();
}
if (armed) ok((await page.$$('.lrow .lpiece .batk')).length === 1, 'tapping the lit machine arms it: the red attack badge shows');
else console.log('  (no operation in hand this run, arming by tap not checked)');
await page.click('#cmpAct');
ok(/THE RAID/.test(await text('.tlamp')) && (await page.$$('.band.chan .epiece')).length === 2, 'round 3: the raid comes into the Channel');
await page.click('#cmpTele').catch(() => {});
await shot('raid');

// The raid: send a machine up under a raider; the plaque shows the result before Lock in blocks
const ready = await page.$$('.lrow .lpiece.can');
ok(ready.length >= 1, 'Ready machines are lit for blocking');
const r0 = Number(await text('#cmpRes b'));
await ready[0].click();
if (await page.$('.epiece.target')) await page.click('.epiece.target >> nth=0');
ok((await page.$$('.col .lpiece')).length === 1 && (await page.$$('.col .plq')).length >= 1, 'the blocker rises under its raider with a plotting plaque');
ok(/Resolve/.test(await text('.fcast')), 'the forecast says what the raid will do to Resolve');
await shot('blocking');
await page.click('#cmpMenu');
ok(/Sound: off/.test(await text('#mSnd')), 'sound is off until turned on in the round menu');
await page.click('#mSnd');
ok(/Sound: on/.test(await text('#mSnd')) && await page.evaluate(() => JSON.parse(localStorage.getItem('declass_cmp_sound')).on === true), 'the round menu turns sound on, and it is remembered');
ok(/THE WAR CABINET ADVISES/.test(await text('#sheetCard')) && /This raid brings \d+ attack/.test(await text('#sheetCard')), 'the War Cabinet advises in the round menu');
await page.click('#sheet [data-close]');
const plan = await page.$eval('.fcast', el => el.textContent);
await page.click('#cmpAct');
const r1 = Number(await text('#cmpRes b'));
ok(new RegExp(`Resolve (stays ${r1}|${r0} to ${r1})`).test(plan), 'the raid lands exactly as forecast');
ok(/YOUR TURN/.test(await text('.tlamp')) && (await page.$$('.lrow .lpiece.rearm')).length >= 1, 'your turn: the blocker is Rearming');
await shot('turn');

// Play the rest of the run through the page: a plain strategy, every move made by tapping.
async function playTurn() {
  for (let k = 0; k < 8; k++) {
    let played = false;
    for (const h of await litCards()) {
      await liftCard(h);
      const t = (await page.$('.lrow .lpiece.aim')) || (await page.$('#cmpRes.aim')) || (await page.$('.lslot.aim')) || (await page.$('.lbplay'));
      if (t) { await t.click(); played = true; break; }
      await dropCard();
    }
    if (!played) break;
  }
  for (let k = 0; k < 5; k++) {
    const m = await page.$('.lrow .lpiece.can'); if (!m) break;
    await m.click();
    const t = await page.$('.epiece.target'); if (t) await t.click();
    if (await page.$('.lpiece.picked')) { await page.click('#cmpUnpick'); break; }
  }
}
async function playRaid() {
  for (let k = 0; k < 5; k++) {
    const m = await page.$('.lrow .lpiece.can'); if (!m) break;
    await m.click();
    const t = await page.$('.epiece.target'); if (t) await t.click();
    if (await page.$('.lpiece.picked')) { await page.click('#cmpUnpick'); break; }
  }
}
let debriefs = 0, guard = 0;
while (guard++ < 80) {
  if (await page.$('#cmpOver:not([hidden]) #dbGo')) { debriefs++; if (debriefs === 1) await shot('debrief'); await page.click('#dbGo'); continue; }
  if (await page.$('#endGo')) break;
  const lamp = await text('.tlamp');
  if (/YOUR TURN/.test(lamp)) await playTurn(); else if (/THE RAID/.test(lamp)) await playRaid();
  await page.click('#cmpAct');
}
await page.waitForSelector('#endGo');
const end = await text('.dbf.end');
ok(/CHAPTER WON|RUN OVER/.test(end), 'the run ends with the end screen: ' + end.slice(0, 40));
ok(/In real history, Britain came through these raids at a Resolve of 6|ran out in wave/.test(end), 'the verdict is said in full words');
await page.waitForFunction(() => !document.getElementById('endGo').disabled, null, { timeout: 15000 });
ok(/Checked and saved/.test(await text('#endRank')), 'the server replays the run and saves it: ' + (await text('#endRank')));
ok(/YOUR RANK/.test(await text('#endRank')) && /This month: top \d+% of \d+ player/.test(await text('#endRank')) && /top 5% get \d+/.test(await text('#endRank')), 'the end screen shows the rank and what each band pays');
await shot('end');
const saved = db.prepare("SELECT status, won, resolve FROM campaign_runs WHERE player_id = ? AND status = 'done'").get(P);
ok(saved && (saved.won === 1) === /CHAPTER WON/.test(end), 'the saved result matches the page');
console.log(`  played a whole run: ${/CHAPTER WON/.test(end) ? 'won' : 'lost'}, ${debriefs} debrief${debriefs === 1 ? '' : 's'}`);
await page.click('#endGo');
await page.waitForSelector('#chGo');
ok(/2 of 3 runs left today/.test(await text('#cmpBody')), 'the finished run counts: ' + (await text('#cmpBody')).match(/\d of 3 runs[^.]*|No runs[^.]*/));

// The month end notice: on this local copy the test clock lets the preview month settle, so going home
// pays the chapter and shows the results once.
await page.click('#cmpBack').catch(() => {});
if (!(await page.$('#cmpBack:not([hidden])'))) { await page.click('#chBack'); await page.click('#cmpBack'); }
await page.waitForSelector('#sheet:not([hidden])', { timeout: 6000 }).catch(() => {});
const payout = db.prepare('SELECT band, intel FROM campaign_payouts WHERE player_id = ?').get(P);
if (payout && payout.intel > 0) {
  ok(/The month's ranks are settled/.test(await text('#sheetCard')) && new RegExp(`\\+${payout.intel} Intel`).test(await text('#sheetCard')), 'the month end results show on the home screen with the Intel paid');
  await shot('paid');
  await page.click('#sheet [data-close]');
} else {
  // a lost run ranked below the top half pays nothing (the last band needs a win), so no notice
  ok(payout && payout.band === 'none' && await page.$eval('#sheet', el => el.hidden), 'a lost run outside the top half settles with no payout and no notice');
}
ok(errs.length === 0, 'no page errors: ' + errs.join(' | '));
await b.close();
console.log(`${pass} passed, ${failN} failed`);
process.exit(failN ? 1 : 0);
