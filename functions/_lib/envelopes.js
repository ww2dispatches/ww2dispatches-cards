// Which envelopes exist at a moment, and what goes inside one.
//
// Slot keys (stored in opened and pulls):
//   d:<UTC post time>   a daily envelope, one per dispatch post time, open for 24 hours
//   c:<YYYY-MM-DD>      a commemorative file, opening 10 a.m. Eastern on the anniversary for 3 days
//   p:<random>          a priority envelope (streak reward), drawn when opened
import { SLOT_TIMES, slotCards, archivePool, deepPool, flashPool, flashForFile, filmReleased } from './catalog.js';
import { rollFinish, rollLiving, rollFlash, secureInt } from './odds.js';
import { isSundayMorning, isMorning, zonedTime, gameDay, isoSec } from './time.js';

const HOUR = 3600000;
export const DAILY_HOURS = 24;
export const COMMEMORATIVE_HOURS = 72;
const CARDS_PER_ENVELOPE = 3;

// The Flash days (Roadmap, Flash cards plan; Envelope doc, Commemorative files). One commemorative file
// per date, each carrying that year's Flash card. Fifteen files a year since 30 Oct 2026, at least one
// every month; 1 and 2 September share one file. `from` is the first year a date runs: the six monthly
// dates added 30 Oct 2026 start in 2027 so Pearl Harbor (7 Dec 2026) is the first Flash card.
export const COMMEMORATIVE = [
  { md: '01-31', from: 2027, title: '31 January 1943 · Stalingrad', name: 'Stalingrad', stamp: 'STALINGRAD · 31 JANUARY 1943' },
  { md: '02-19', title: '19 February 1945 · Iwo Jima', name: 'Iwo Jima', stamp: 'IWO JIMA · 19 FEBRUARY 1945' },
  { md: '03-07', from: 2027, title: '7 March 1945 · Remagen', name: 'Remagen', stamp: 'REMAGEN · 7 MARCH 1945' },
  { md: '04-18', from: 2027, title: '18 April 1942 · The Doolittle Raid', name: 'The Doolittle Raid', stamp: 'DOOLITTLE RAID · 18 APRIL 1942' },
  { md: '05-08', title: '8 May 1945 · VE Day', name: 'VE Day', stamp: 'VE DAY · 8 MAY 1945' },
  { md: '06-04', title: '4 June 1942 · Midway', name: 'Midway', stamp: 'MIDWAY · 4 JUNE 1942' },
  { md: '06-06', title: '6 June 1944 · D Day', name: 'D Day', stamp: 'D DAY · 6 JUNE 1944' },
  { md: '07-16', from: 2027, title: '16 July 1945 · Trinity', name: 'Trinity', stamp: 'TRINITY · 16 JULY 1945' },
  { md: '08-15', title: '15 August 1945 · VJ Day', name: 'VJ Day', stamp: 'VJ DAY · 15 AUGUST 1945' },
  { md: '09-01', title: '1 September 1939 · 2 September 1945', name: 'First and last days', stamp: '1 SEPTEMBER 1939 · 2 SEPTEMBER 1945' },
  { md: '09-15', title: '15 September 1940 · Battle of Britain Day', name: 'Battle of Britain Day', stamp: 'BATTLE OF BRITAIN · 15 SEPTEMBER 1940' },
  { md: '10-25', from: 2027, title: '25 October 1944 · Leyte Gulf', name: 'Leyte Gulf', stamp: 'LEYTE GULF · 25 OCTOBER 1944' },
  { md: '11-20', from: 2027, title: '20 November 1943 · Tarawa', name: 'Tarawa', stamp: 'TARAWA · 20 NOVEMBER 1943' },
  { md: '12-07', title: '7 December 1941 · Pearl Harbor', name: 'Pearl Harbor', stamp: 'PEARL HARBOR · 7 DECEMBER 1941' },
  { md: '12-16', title: '16 December 1944 · The Bulge', name: 'The Bulge', stamp: 'THE BULGE · 16 DECEMBER 1944' },
];

// Daily envelopes out right now (posted within the last 24 hours), oldest first.
export function dailyOpen(t) {
  const now = t.getTime();
  return SLOT_TIMES
    .filter(s => { const at = Date.parse(s); return at <= now && now < at + DAILY_HOURS * HOUR; })
    .map(s => ({
      key: 'd:' + s, kind: 'daily', at: s,
      closes: isoSec(new Date(Date.parse(s) + DAILY_HOURS * HOUR)),
      deep: isSundayMorning(new Date(s)),
    }));
}

// The next envelope time after now (just the time; nothing about the card).
export const nextSlot = t => SLOT_TIMES.find(s => Date.parse(s) > t.getTime()) || null;

// Envelope times still to come in the next 24 hours (times only, nothing about the cards), so the
// page can show tonight's envelope as "Arrives 5:00 PM".
export function upcomingSlots(t) {
  const now = t.getTime();
  return SLOT_TIMES.filter(s => { const at = Date.parse(s); return at > now && at <= now + DAILY_HOURS * HOUR; })
    .map(s => ({ at: s, deep: isSundayMorning(new Date(s)) }));
}

function commemorativeFor(year, c) {
  const day = `${year}-${c.md}`;
  const opens = zonedTime(day, '10:00');
  return { key: 'c:' + day, day, kind: 'commemorative', name: c.name, title: c.title, stamp: c.stamp,
    at: isoSec(opens), closes: isoSec(new Date(opens.getTime() + COMMEMORATIVE_HOURS * HOUR)), deep: true };
}

// A Flash card is always Top Secret, with no worldwide serial (Roadmap, Flash cards plan).
const flashPick = card => ({ card, variant: 'still', finish: 'topsecret' });

// Commemorative files open right now (two can overlap, Midway and D Day).
export function commemorativeOpen(t) {
  const year = Number(gameDay(t).slice(0, 4));
  const now = t.getTime();
  return [year - 1, year].flatMap(y => COMMEMORATIVE.filter(c => !c.from || y >= c.from).map(c => commemorativeFor(y, c)))
    .filter(e => Date.parse(e.at) <= now && now < Date.parse(e.closes));
}

// The next Flash days still to come (names and dates only, never the card), for the Incoming Flash
// traffic strip. Public knowledge, so it shows signed out too.
export function flashUpcoming(t, n = 3) {
  const year = Number(gameDay(t).slice(0, 4)), now = t.getTime();
  return [year, year + 1].flatMap(y => COMMEMORATIVE.filter(c => !c.from || y >= c.from).map(c => commemorativeFor(y, c)))
    .filter(e => Date.parse(e.at) > now)
    .sort((a, b) => a.at.localeCompare(b.at)).slice(0, n)
    .map(e => ({ name: e.name, title: e.title, day: e.day, at: e.at }));
}

// Turn a requested slot key into an envelope the player may open now, or null.
export function resolveEnvelope(slot, t, player) {
  if (slot === 'priority') {
    if (!(player.priority_waiting > 0)) return null;
    const rand = new Uint8Array(9); crypto.getRandomValues(rand);
    return { key: 'p:' + [...rand].map(b => b.toString(16).padStart(2, '0')).join(''), kind: 'priority', deep: true };
  }
  if (typeof slot !== 'string') return null;
  if (slot.startsWith('d:')) return dailyOpen(t).find(e => e.key === slot) || null;
  if (slot.startsWith('c:')) return commemorativeOpen(t).find(e => e.key === slot) || null;
  return null;
}

// One archive slot: roll Flash first (1 in 200, from the Flash cards already posted), then living,
// then pick a card and roll the finish.
function archivePick(pool, t, rnd) {
  if (!pool.length) return null;
  if (rollFlash(rnd)) {
    const flashes = flashPool(t);
    if (flashes.length) return flashPick(flashes[rnd(flashes.length)]);
  }
  if (rollLiving(rnd)) {
    const films = pool.filter(c => filmReleased(c, t));
    if (films.length) {
      const card = films[rnd(films.length)];
      return { card, variant: 'living', finish: rollFinish('living', rnd) };
    }
  }
  const card = pool[rnd(pool.length)];
  return { card, variant: 'still', finish: rollFinish('still', rnd) };
}

// The cards in an envelope. Daily morning: that slot's dispatch (evening: archive cards only) (always the still card; a Flash dispatch
// comes Top Secret), then archive pulls from the last 90 days, or the whole history on Sunday
// mornings. Priority: three cards from the whole history. Commemorative: the day's Flash card
// (or cards, on 1 and 2 September) plus three cards from the whole history.
export function drawCards(env, t, rnd = secureInt) {
  const picks = [];
  let want = CARDS_PER_ENVELOPE;
  // Only the morning envelope carries the day's dispatch (29 Oct 2026); the evening envelope is
  // three archive cards, so a full month takes some luck or Intel, not just showing up.
  const morning = env.kind === 'daily' && isMorning(env.at);
  if (morning) {
    for (const card of slotCards(env.at).slice(0, CARDS_PER_ENVELOPE)) {
      picks.push(card.flash ? flashPick(card) : { card, variant: 'still', finish: rollFinish('still', rnd) });
    }
  }
  if (env.kind === 'commemorative') {
    const flashes = flashForFile(env.day, t);
    flashes.forEach(card => picks.push(flashPick(card)));
    want = flashes.length + CARDS_PER_ENVELOPE;
  }
  let pool = env.deep ? deepPool(t) : archivePool(t);
  if (!pool.length) pool = deepPool(t);
  while (picks.length < want) {
    const p = archivePick(pool, t, rnd);
    if (!p) break;
    picks.push(p);
  }
  // The day's dispatch is guaranteed but lands at a random spot in the envelope (29 Oct 2026), so
  // the newest card isn't always card 1.
  if (morning) {
    const k = Math.min(slotCards(env.at).length, CARDS_PER_ENVELOPE);
    const mixed = picks.slice(k);
    picks.slice(0, k).forEach(d => mixed.splice(rnd(mixed.length + 1), 0, d));
    return mixed;
  }
  return picks;
}
