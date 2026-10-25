// Streaks (Envelope doc): a game day (Eastern) counts if at least one daily envelope is opened.
// Every third day of a streak earns a priority envelope. Missing a day resets to zero.
import { gameDay, addDays } from './time.js';

export const PRIORITY_EVERY = 3;

// The streak as it stands now: still alive if the last day played was today or yesterday.
export function currentStreak(player, t) {
  const today = gameDay(t);
  const last = player.last_day_played;
  if (last === today || last === addDays(today, -1)) return player.streak;
  return 0;
}

// What opening a daily envelope now does to the streak, or null if today already counted.
export function streakAfterOpen(player, t) {
  const today = gameDay(t);
  const last = player.last_day_played;
  if (last === today) return null;
  const streak = last === addDays(today, -1) ? player.streak + 1 : 1;
  return { streak, day: today, earned: streak % PRIORITY_EVERY === 0 ? 1 : 0 };
}

export function streakInfo(player, t) {
  const streak = currentStreak(player, t);
  const playedToday = player.last_day_played === gameDay(t);
  // Days of opening still needed for the next priority envelope, counting today if not yet played.
  const toNext = PRIORITY_EVERY - (streak % PRIORITY_EVERY);
  return { streak, playedToday, nextPriorityIn: toNext };
}
