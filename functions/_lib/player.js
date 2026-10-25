// What the page is allowed to see about a player, and finding the signed in player.
import { readSession } from './session.js';
import { streakInfo } from './streak.js';

export function publicPlayer(p, t = new Date()) {
  return {
    fileNumber: p.id.slice(0, 8).toUpperCase(),
    since: p.created_at,
    ...streakInfo(p, t),
    priorityWaiting: p.priority_waiting,
    starterDone: Boolean(p.starter_done),
    tester: Boolean(p.tester),
  };
}

export async function signedInPlayer(env, request) {
  const playerId = await readSession(env, request);
  if (!playerId) return null;
  return env.DB.prepare('SELECT * FROM players WHERE id = ?').bind(playerId).first();
}
