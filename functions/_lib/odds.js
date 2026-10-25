// The odds (Envelope doc, starting values 23 Oct 2026). Rolled independently: whether an archive
// slot is living, then the finish from the matching table. Out of 10,000 so 0.25% is exact.
export const LIVING_ONE_IN = 6;
export const FINISHES = {
  //            Top Secret, Gold, Silver (cumulative edges); the rest is Copper
  still:  { topsecret: 25,  gold: 525,  silver: 2500 },  // 0.25, 5, 19.75, 75
  living: { topsecret: 150, gold: 1400, silver: 4000 },  // 1.5, 12.5, 26, 60
};

// A fair whole number from 0 to n - 1 from the secure random generator (never Math.random).
export function secureInt(n) {
  if (!(n > 0)) return 0;
  const limit = Math.floor(0x100000000 / n) * n;
  const buf = new Uint32Array(1);
  do { crypto.getRandomValues(buf); } while (buf[0] >= limit);
  return buf[0] % n;
}

export function rollFinish(variant, rnd = secureInt) {
  const t = FINISHES[variant] || FINISHES.still;
  const x = rnd(10000);
  if (x < t.topsecret) return 'topsecret';
  if (x < t.gold) return 'gold';
  if (x < t.silver) return 'silver';
  return 'copper';
}

export const rollLiving = (rnd = secureInt) => rnd(LIVING_ONE_IN) === 0;
