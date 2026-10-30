import { cookie } from './cookie.mjs';
import { createHmac } from 'node:crypto';
import { readFileSync } from 'node:fs';
const BASE = 'http://localhost:8799';
const cat = JSON.parse(readFileSync(new URL('../../functions/_data/catalog.json', import.meta.url))).cards;
const byId = new Map(cat.map(c => [c.id, c]));
let pass = 0, failN = 0;
const ok = (cond, msg) => { if (cond) pass++; else { failN++; console.log('FAIL:', msg); } };
const id = p => p + 'x'.repeat(31);
async function req(path, { player, now, body, headers = {}, key = 't', origin = BASE } = {}) {
  const h = { 'x-declass-key': key, ...headers };
  if (player) h.cookie = cookie(id(player));
  if (now) h['x-declass-now'] = now;
  if (body) { h['content-type'] = 'application/json'; if (origin) h.origin = origin; }
  const r = await fetch(BASE + '/api/' + path, { method: body ? 'POST' : 'GET', headers: h, body: body ? JSON.stringify(body) : undefined });
  return { status: r.status, data: await r.json() };
}
const state = (player, now) => req('state', { player, now }).then(r => r.data);
const open = (player, now, slot, headers) => req('open', { player, now, body: { slot }, headers });
const turn = (player, now) => req('turn', { player, now, body: {} });
const H = 3600000, DAY = 24 * H;
const iso = ms => new Date(ms).toISOString();

// A: daily player, 35 days from Mon 9 Nov 2026, opening every envelope about an hour after it posts.
let priorityEarned = 0, lastStreak = 0, deepOld = 0, weekdayOld = 0, nameThisDeep = 0, nameThisWeekday = 0, living = 0, archiveSlots = 0, slotCardOk = 0, opens = 0;
const slotPos = [0, 0, 0];
let mornings = 0;
const etHour = iso => Number(new Date(iso).toLocaleString('en-US', { timeZone: 'America/New_York', hour: 'numeric', hourCycle: 'h23' }));
const start = Date.parse('2026-11-09T05:00:00Z'); // midnight Eastern
for (let d = 0; d < 35; d++) {
  for (const hourEt of [11, 20]) { // 11 a.m. and 8 p.m. Eastern (an hour after each post, roughly)
    const t = start + d * DAY + hourEt * H;
    const st = await state('A', iso(t));
    for (const e of st.envelopes.filter(e => !e.opened)) {
      const r = await open('A', iso(t), e.key);
      ok(r.status === 200, `A open ${e.key} at ${iso(t)}: ${r.status} ${JSON.stringify(r.data)}`);
      if (r.status !== 200) continue;
      opens++;
      const pulls = r.data.pulls;
      ok(pulls.length === 3, 'three cards');
      ok(pulls.every(p => p.signed), 'signed');
      const slotCard = etHour(e.at) < 12 ? cat.find(c => c.kind === 'dispatch' && c.postAt === e.at) : null;
      if (slotCard) mornings++;
      // The day's dispatch lands at a random spot (29 Oct 2026).
      const si = slotCard ? pulls.findIndex(p => p.card === slotCard.id && p.variant === 'still') : -1;
      if (si >= 0) { slotCardOk++; slotPos[si]++; }
      for (const p of pulls.filter((_, j) => j !== si)) {
        archiveSlots++;
        const c = byId.get(p.card);
        ok(c.postAt <= iso(t), 'archive card already posted');
        if (p.variant === 'living') { living++; ok(c.film && c.film.postAt <= iso(t), 'living has posted film'); }
        const old = Date.parse(c.postAt) < t - 90 * DAY;
        if (c.kind === 'namethis') { ok(c.answerAt && c.answerAt <= iso(t), 'name this answer public'); e.deep ? nameThisDeep++ : nameThisWeekday++; }
        if (old) e.deep ? deepOld++ : weekdayOld++;
      }
      if (r.data.earnedPriority) priorityEarned++;
      ok((await turn('A', iso(t))).data.waiting === 0, 'turned');
    }
  }
  const st = await state('A', iso(start + d * DAY + 21 * H));
  ok(st.player.streak === d + 1, `A streak day ${d + 1}: got ${st.player.streak}`);
  lastStreak = st.player.streak;
}
ok(priorityEarned === Math.floor(35 / 3), `priority earned ${priorityEarned}`);
ok(slotCardOk === mornings, `slot card still in every morning envelope (${slotCardOk}/${mornings})`);
ok(slotPos.every(n => n > 0), `slot card spot varies (${slotPos.join(" / ")})`);
ok(weekdayOld === 0, `weekday archive older than 90 days: ${weekdayOld}`);
ok(nameThisWeekday === 0, `Name This in weekday envelope: ${nameThisWeekday}`);
console.log(`A: ${opens} envelopes, streak ${lastStreak}, priority earned ${priorityEarned}, living ${living}/${archiveSlots} archive slots (${(100*living/archiveSlots).toFixed(1)}%), deep pulls older than 90 days ${deepOld}, Name This in deep ${nameThisDeep}`);
ok(deepOld > 0, 'Sunday deep archive reaches past 90 days');

// A: commemorative Pearl Harbor (10 a.m. EST = 15:00Z on 7 Dec, 72 hours) was inside the run.
let t = Date.parse('2026-12-07T14:59:00Z');
ok((await state('A', iso(t))).commemorative.length === 0, 'not open before 10 a.m. ET');
t = Date.parse('2026-12-10T14:59:00Z');
let st = await state('A', iso(t));
ok(st.commemorative.length === 1 && st.commemorative[0].key === 'c:2026-12-07', 'Pearl Harbor open on day 3');
ok((await state('A', '2026-12-10T15:00:00Z')).commemorative.length === 0, 'closed after 72 hours');
const streakBefore = st.player.streak;
let r = await open('A', iso(t), 'c:2026-12-07');
ok(r.status === 200 && r.data.pulls.length === 3, 'commemorative opens with 3 cards');
ok(r.data.player.streak === streakBefore, 'commemorative does not touch the streak');
await turn('A', iso(t));
ok((await open('A', iso(t), 'c:2026-12-07')).status === 409, 'commemorative opens once');
ok((await open('A', '2026-12-11T16:00:00Z', 'c:2026-12-07')).status === 409, 'closed commemorative refused');
// Midway and D Day overlap.
ok((await state('A', '2027-06-06T16:00:00Z')).commemorative.map(c => c.name).join() === 'Midway,D Day', 'Midway and D Day both open on 6 June');

// A: priority envelopes. Opening them doesn't change the streak; one too many is refused.
st = await state('A', iso(t));
const waitingP = st.priority;
ok(waitingP === priorityEarned, `priority waiting ${waitingP}`);
for (let i = 0; i < waitingP; i++) {
  r = await open('A', iso(t), 'priority');
  ok(r.status === 200 && r.data.pulls.length === 3, 'priority open');
  ok(r.data.player.streak === streakBefore, 'priority leaves streak alone');
  await turn('A', iso(t));
}
ok((await open('A', iso(t), 'priority')).status === 409, 'no priority left');

// B: reroll guard, waiting lock, future and expired envelopes.
t = Date.parse('2026-11-20T16:00:00Z');
st = await state('B', iso(t));
const [e1, e2] = st.envelopes;
ok((await open('B', iso(t), e2.key)).status === 200, 'B opens');
r = await open('B', iso(t), e1.key);
ok(r.status === 409 && r.data.error === 'cards waiting', 'locked while cards wait');
st = await state('B', iso(t));
ok(st.waiting.length === 3 && st.waiting.every(w => w.cardInfo), 'waiting cards listed with card details');
await turn('B', iso(t));
ok((await open('B', iso(t), e2.key)).data.error === 'already opened', 'reroll refused');
ok((await open('B', iso(t), e1.key)).status === 200, 'unlocked after turning'); await turn('B', iso(t));
ok((await open('B', iso(t), 'd:' + st.next)).status === 409, 'future envelope refused');
ok((await open('B', iso(t + DAY + H), e2.key)).status === 409, 'envelope refused after 24 hours');
ok((await open('B', iso(t), 'd:2026-11-20T16:00:01Z')).status === 409, 'made up slot refused');

// C: a missed day resets the streak.
const days = ['2026-11-10', '2026-11-11', '2026-11-13'];
for (const day of days) {
  t = Date.parse(day + 'T18:00:00Z');
  st = await state('C', iso(t));
  if (day === '2026-11-13') ok(st.player.streak === 0, 'streak shows 0 after a missed day');
  r = await open('C', iso(t), st.envelopes.find(e => !e.opened).key); await turn('C', iso(t));
}
ok(r.data.player.streak === 1 && r.data.player.priorityWaiting === 0, `streak restarts at 1 (got ${r.data.player.streak})`);
// Opening both envelopes in one day counts once.
t = Date.parse('2026-11-14T02:00:00Z'); // 9 p.m. Eastern on the 13th
st = await state('C', iso(t));
r = await open('C', iso(t), st.envelopes.find(e => !e.opened).key); await turn('C', iso(t));
ok(r.data.player.streak === 1, 'second envelope same day does not add');

// D: eight parallel opens of one envelope: exactly one wins.
t = Date.parse('2026-11-25T17:00:00Z');
st = await state('D', iso(t));
let rs = await Promise.all(Array.from({ length: 8 }, () => open('D', iso(t), st.envelopes[1].key)));
ok(rs.filter(x => x.status === 200).length === 1, `parallel reroll: ${rs.map(x => x.status)}`);
ok((await state('D', iso(t))).waiting.length === 3, 'only three cards saved');
await turn('D', iso(t));

// E: one priority envelope, four parallel opens: exactly one wins.
const { execSync } = await import('node:child_process');
execSync(`python3 -c "import sqlite3; c=sqlite3.connect('${process.env.DB}'); c.execute(\\"update players set priority_waiting=1 where id='${id('E')}'\\"); c.commit()"`);
rs = await Promise.all(Array.from({ length: 4 }, () => open('E', iso(t), 'priority')));
ok(rs.filter(x => x.status === 200).length === 1, `parallel priority: ${rs.map(x => x.status)}`);
st = await state('E', iso(t));
ok(st.priority === 0 && st.waiting.length === 3, `priority used once (${st.priority}, ${st.waiting.length})`);

// Serials: 30 players open the same envelope at once, all forced Top Secret.
t = Date.parse('2026-11-26T16:00:00Z');
st = await state('P0', iso(t));
const slot = st.envelopes[1].key;
rs = await Promise.all(Array.from({ length: 30 }, (_, i) => open('P' + i, iso(t), slot, { 'x-declass-force-finish': 'topsecret' })));
ok(rs.every(x => x.status === 200), 'all 30 opened');
const serials = {};
for (const x of rs) for (const p of x.data.pulls) (serials[p.card + '/' + p.variant] ||= []).push(p.serial);
const slotId = cat.find(c => c.kind === 'dispatch' && c.postAt === slot.slice(2)).id;
const s = serials[slotId + '/still'].sort((a, b) => a - b);
ok(s.length >= 30 && s.every((v, i) => v === i + 1), `slot card serials run 1 to n with no gaps (it can come up again as an archive pull): ${s.join(',')}`);
let allGood = true;
for (const [k, v] of Object.entries(serials)) { v.sort((a, b) => a - b); if (!v.every((x, i) => x === i + 1)) allGood = false; }
ok(allGood, 'every card numbered 1..n with no gaps or repeats');

// Signatures check out against the secret.
const rows = JSON.parse(execSync(`python3 -c "import sqlite3,json; c=sqlite3.connect('${process.env.DB}'); c.row_factory=sqlite3.Row; print(json.dumps([dict(r) for r in c.execute('select * from pulls')]))"`, { maxBuffer: 1 << 26 }));
const b64u = b => Buffer.from(b).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const bad = rows.filter(r => r.signature !== b64u(createHmac('sha256', 's').update(['pull', r.id, r.player_id, r.card_id, r.variant, r.finish, r.serial ?? '', r.slot_key, r.pulled_at].join('|')).digest()));
ok(bad.length === 0, `${rows.length} pulls, ${bad.length} bad signatures`);

// Gate and session checks.
ok((await req('state', { key: 'wrong' })).status === 403, 'no key, no game');
ok((await open(null, iso(t), slot)).status === 401, 'open needs sign in');
ok((await req('open', { player: 'A', body: { slot }, origin: 'https://evil.example' })).status === 403, 'other sites refused');
ok((await state(null, iso(t))).player === null, 'signed out state works');

console.log(`\n${pass} passed, ${failN} failed`);
