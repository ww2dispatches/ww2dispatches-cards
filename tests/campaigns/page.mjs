// Campaigns page checks (build session 3). Against the same local server as server.mjs, in a phone sized
// headless browser, signed in as test player B (a tester holding a few cards):
//   DB=<the local D1 sqlite file> PLAYWRIGHT=<path to playwright's index.mjs> node tests/campaigns/page.mjs
// Walks the door, the month, a chapter, the deck builder, a run's opening hand and mulligan, and the calm
// opening, and fails on any page error. SHOTS=<dir> saves a screenshot of each step.
import { cookie } from '../declass/cookie.mjs';
import { DatabaseSync } from 'node:sqlite';
const { chromium } = await import(process.env.PLAYWRIGHT || 'playwright');
const BASE = 'http://localhost:8799', P = 'B' + 'x'.repeat(31);
const db = new DatabaseSync(process.env.DB);
db.prepare("INSERT OR IGNORE INTO players (id, created_at, tester) VALUES (?, '2026-11-01T00:00:00Z', 1)").run(P);
db.prepare('DELETE FROM campaign_runs WHERE player_id = ?').run(P);
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
const lit = await page.$$('.hcard.lit');
let placed = false;
for (const h of lit) { await h.click(); const p = await page.$('.lbplay'); if (p && /Put on your line/.test(await p.textContent())) { await p.click(); placed = true; break; } await h.click(); }
ok(placed && (await page.$$('.lrow .lpiece.fresh')).length === 1, 'a machine goes on the line, SETTING UP');
ok(/0\/2|1\/2/.test(await text('.ttile.sup')), 'Supply goes down by its cost');
await shot('placed');
// Undo it, then play it again
await page.click('#cmpMenu'); await page.click('#mUndo');
ok((await page.$$('.lrow .lpiece')).length === 0, 'Undo takes the move back');
for (const h of await page.$$('.hcard.lit')) { await h.click(); const p = await page.$('.lbplay'); if (p && /Put on your line/.test(await p.textContent())) { await p.click(); break; } await h.click(); }
// A reload picks the run up where it was
await page.reload();
await page.waitForSelector('#cmpTile');
await page.click('#cmpTile');
await page.waitForSelector('#cmpResume');
await page.click('#cmpResume');
ok((await page.$$('.lrow .lpiece')).length === 1, 'a reloaded page picks the run up where it was');
await page.click('#cmpAct');
ok(/Round 2|round 3/.test(await text('.tlamp')) && (await page.$$('.lrow .lpiece.fresh')).length === 0, 'End turn: round 2, the machine has set up');
await page.click('#cmpAct');
ok(/THE RAID/.test(await text('.tlamp')) && (await page.$$('.band.chan .epiece')).length === 2, 'round 3: the raid comes into the Channel');
await page.waitForSelector('.ohand.hold');
await shot('raid');
await page.click('#holdLeave');
await page.waitForSelector('#chGo');
ok(/2 of 3 runs left today/.test(await text('#cmpBody')), 'leaving the run still counts it');

ok(errs.length === 0, 'no page errors: ' + errs.join(' | '));
await b.close();
console.log(`${pass} passed, ${failN} failed`);
process.exit(failN ? 1 : 0);
