// Time helpers. The game day (for streaks) and Sunday mornings follow Eastern time, the same
// zone the fixed game text uses; the page shows every time in the player's own zone.
export const GAME_TZ = 'America/New_York';
const DAY_MS = 86400000;

const fmt = new Map();
function parts(date, tz) {
  if (!fmt.has(tz)) {
    fmt.set(tz, new Intl.DateTimeFormat('en-US', {
      timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit', weekday: 'short', hourCycle: 'h23',
    }));
  }
  const out = {};
  for (const p of fmt.get(tz).formatToParts(date)) out[p.type] = p.value;
  return out;
}

// "YYYY-MM-DD" in Eastern time.
export function gameDay(date) {
  const p = parts(date, GAME_TZ);
  return `${p.year}-${p.month}-${p.day}`;
}

export function addDays(day, n) {
  return new Date(Date.parse(day + 'T12:00:00Z') + n * DAY_MS).toISOString().slice(0, 10);
}

// Is this moment a Sunday morning (before noon) in Eastern time?
export function isSundayMorning(date) {
  const p = parts(date, GAME_TZ);
  return p.weekday === 'Sun' && Number(p.hour) < 12;
}

// Is this envelope time a morning one (before noon Eastern)? Only the morning envelope carries the day's dispatch.
export const isMorning = iso => Number(parts(new Date(iso), GAME_TZ).hour) < 12;

// A wall clock time in a zone ("2026-12-07", "10:00") as a UTC Date, daylight saving handled.
export function zonedTime(day, hhmm, tz = GAME_TZ) {
  const want = Date.parse(`${day}T${hhmm}:00Z`);
  let guess = want;
  for (let i = 0; i < 2; i++) {
    const p = parts(new Date(guess), tz);
    const shown = Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute, +p.second);
    guess += want - shown;
  }
  return new Date(guess);
}

export const isoSec = t => t.toISOString().replace(/\.\d{3}Z$/, 'Z');
