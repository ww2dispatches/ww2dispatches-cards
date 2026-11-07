// Test decks for the engine checks. These are made up test cards, not posted dispatches: real card
// numbers stay in the private score sheet until the seal reveal (Seal Reveal and Keywords doc), so no
// dispatch is named here. The values match the test bench's two ready made decks.
const M = (v, b = ['air']) => ({ series: 'blue', value: v, branches: b });
const O = (v, b = ['air']) => ({ series: 'battle', value: v, branches: b });
const H = v => ({ series: 'home', value: v, branches: [] });
const S = (v, keyword) => ({ series: 'state', value: v, branches: [], keyword });
export const FIGHTER_COMMAND = [
  M(1), M(2), M(4), M(2), M(3), M(4),
  O(1), O(2), O(2), O(3), O(3), O(4),
  H(2), H(3), H(2), H(4),
  S(1, 'backchannel'), S(2, 'backchannel'), S(3, 'evac'), S(4, 'ultimatum'),
];
export const STATECRAFT_HEAVY = [
  M(1), M(2), M(2), M(4),
  O(1), O(2), O(3), O(3), O(4),
  H(2), H(3), H(1), H(4),
  S(1, 'backchannel'), S(2, 'ultimatum'), S(2, 'backchannel'), S(3, 'lend'), S(3, 'evac'), S(4, 'lend'), S(4, 'ultimatum'),
];
