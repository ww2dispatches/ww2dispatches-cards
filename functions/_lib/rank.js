// Ranks (decided 25 Oct 2026, Envelope doc "Ranks"). Based on filled slots: each finish of each card
// variant counts once, requested slots included. Ranks are never lost. The ladder stays on the server:
// players only ever see their current rank and the next one, and each new title is a surprise.
export const LADDER = [
  [0, 'Private'], [50, 'Corporal'], [150, 'Sergeant'], [300, 'Staff Sergeant'], [500, 'Lieutenant'],
  [750, 'Captain'], [1000, 'Major'], [1500, 'Lieutenant Colonel'], [2000, 'Colonel'],
  [3000, 'Brigadier General'], [4000, 'Major General'], [5000, 'Lieutenant General'],
  [6500, 'General'], [8000, 'General of the Army'],
];
// US Army ranks (25 Oct 2026): the top rank is General of the Army, the five star rank of December 1944.
const SHORT = { 'Lieutenant Colonel': 'Lt. Colonel', 'General of the Army': 'Gen. of the Army' }; // header only

// Filled slots from a player's pull rows.
export function filledSlots(rows) {
  return new Set(rows.map(r => `${r.card_id}|${r.variant}|${r.finish}`)).size;
}

export function rankIndex(filled) {
  let i = 0;
  while (i + 1 < LADDER.length && filled >= LADDER[i + 1][0]) i++;
  return i;
}

// What the page may know: the current rank, progress to the next, and whether a promotion is still to
// be shown (seen = the highest rank already announced to this player).
export function rankInfo(filled, seen = 0) {
  const i = rankIndex(filled), next = LADDER[i + 1] || null;
  return {
    index: i, title: LADDER[i][1], short: SHORT[LADDER[i][1]] || LADDER[i][1], filled,
    from: LADDER[i][0], nextAt: next ? next[0] : null, nextTitle: next ? next[1] : null,
    seen: Math.min(seen, i), promoted: i > seen,
  };
}
