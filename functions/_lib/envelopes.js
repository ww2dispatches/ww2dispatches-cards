// Which envelopes exist at a moment, and what goes inside one.
//
// Slot keys (stored in opened and pulls):
//   d:<UTC post time>   a daily envelope, one per dispatch post time, open for 24 hours
//   c:<YYYY-MM-DD>      a commemorative file, opening 10 a.m. Eastern on the anniversary for 3 days
//   p:<random>          a priority envelope (streak reward), drawn when opened
import { SLOT_TIMES, slotCards, archivePool, deepPool, filmReleased } from './catalog.js';
import { rollFinish, rollLiving, secureInt } from './odds.js';
import { isSundayMorning, zonedTime, gameDay, isoSec } from './time.js';

const HOUR = 3600000;
export const DAILY_HOURS = 24;
export const COMMEMORATIVE_HOURS = 72;
const CARDS_PER_ENVELOPE = 3;

// Nine a year (Envelope doc, Commemorative files). 1 and 2 September share one file.
export const COMMEMORATIVE = [
  { md: '02-19', title: '19 February 1945 · Iwo Jima', name: 'Iwo Jima', stamp: 'IWO JIMA · 19 FEBRUARY 1945' },
  { md: '05-08', title: '8 May 1945 · VE Day', name: 'VE Day', stamp: 'VE DAY · 8 MAY 1945' },
  { md: '06-04', title: '4 June 1942 · Midway', name: 'Midway', stamp: 'MIDWAY · 4 JUNE 1942' },
  { md: '06-06', title: '6 June 1944 · D Day', name: 'D Day', stamp: 'D DAY · 6 JUNE 1944' },
  { md: '08-15', title: '15 August 1945 · VJ Day', name: 'VJ Day', stamp: 'VJ DAY · 15 AUGUST 1945' },
  { md: '09-01', title: '1 September 1939 · 2 September 1945', name: 'First and last days', stamp: '1 SEPTEMBER 1939 · 2 SEPTEMBER 1945' },
  { md: '09-15', title: '15 September 1940 · Battle of Britain Day', name: 'Battle of Britain Day', stamp: 'BATTLE OF BRITAIN · 15 SEPTEMBER 1940' },
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

function commemorativeFor(year, c) {
  const day = `${year}-${c.md}`;
  const opens = zonedTime(day, '10:00');
  return { key: 'c:' + day, kind: 'commemorative', name: c.name, title: c.title, stamp: c.stamp,
    at: isoSec(opens), closes: isoSec(new Date(opens.getTime() + COMMEMORATIVE_HOURS * HOUR)), deep: true };
}

// Commemorative files open right now (two can overlap, Midway and D Day).
export function commemorativeOpen(t) {
  const year = Number(gameDay(t).slice(0, 4));
  const now = t.getTime();
  return [year - 1, year].flatMap(y => COMMEMORATIVE.map(c => commemorativeFor(y, c)))
    .filter(e => Date.parse(e.at) <= now && now < Date.parse(e.closes));
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

// One archive slot: roll living first, then pick a card, then roll the finish.
function archivePick(pool, t, rnd) {
  if (!pool.length) return null;
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

// The three cards in an envelope. Daily: that slot's dispatch (always the still card), then
// archive pulls from the last 90 days, or the whole history on Sunday mornings. Priority and
// commemorative: three cards from the whole history.
export function drawCards(env, t, rnd = secureInt) {
  const picks = [];
  if (env.kind === 'daily') {
    for (const card of slotCards(env.at).slice(0, CARDS_PER_ENVELOPE)) {
      picks.push({ card, variant: 'still', finish: rollFinish('still', rnd) });
    }
  }
  let pool = env.deep ? deepPool(t) : archivePool(t);
  if (!pool.length) pool = deepPool(t);
  while (picks.length < CARDS_PER_ENVELOPE) {
    const p = archivePick(pool, t, rnd);
    if (!p) break;
    picks.push(p);
  }
  return picks;
}
