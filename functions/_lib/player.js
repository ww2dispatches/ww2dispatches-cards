// What the page is allowed to see about a player.
export function publicPlayer(p) {
  return {
    fileNumber: p.id.slice(0, 8).toUpperCase(),
    since: p.created_at,
    streak: p.streak,
    priorityWaiting: p.priority_waiting,
    starterDone: Boolean(p.starter_done),
    tester: Boolean(p.tester),
  };
}
