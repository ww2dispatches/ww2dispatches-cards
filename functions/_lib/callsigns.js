// Display Case call signs (word lists approved by Brian, 11 Nov 2026; Display Case doc).
// A call sign is one FIRST word and one SECOND word. No typing, so nothing to moderate.
// Rules for any word added later: WWII era, military, weather, landscape, and nature words. Never rank
// words, finish names, nations, ethnicities, religions, colors tied to race, political words, real units,
// slang, or words with a common crude second meaning. Check every new word against every word in the
// other list. A word removed here falls back to CALL SIGN for anyone who had it, with no page change.
export const FIRST = [
  'AMBER', 'ARCTIC', 'ASH', 'AUTUMN', 'BOLD', 'BRAVE', 'BRIGHT', 'BRONZE', 'CEDAR', 'CLEAR', 'COBALT', 'COLD',
  'CRIMSON', 'DAWN', 'DISTANT', 'DUSK', 'EAST', 'FAR', 'FROST', 'GRANITE', 'GREY', 'HARDY', 'HIDDEN',
  'IRON', 'KEEN', 'LOYAL', 'LUCKY', 'MIDNIGHT', 'MOONLIT', 'NIGHT', 'NORTH', 'OAK', 'PATIENT', 'PINE', 'QUIET',
  'RAPID', 'RISING', 'ROAMING', 'SHADOW', 'SILENT', 'SLATE', 'SOARING', 'SOUTH', 'STALWART', 'STARLIT', 'STEADY',
  'STEEL', 'STONE', 'STORM', 'SWIFT', 'THUNDER', 'TRUE', 'VALIANT', 'WATCHFUL', 'WEST', 'WINTER',
];
export const SECOND = [
  'ALBATROSS', 'ANCHOR', 'ANVIL', 'ARROW', 'BADGER', 'BEACON', 'BEAR', 'BISON', 'BRIDGE', 'BULWARK', 'CANTEEN',
  'CANYON', 'CIPHER', 'CITADEL', 'COMET', 'COMPASS', 'CONDOR', 'CONVOY', 'COURIER', 'EAGLE', 'EMBER', 'FALCON',
  'FLARE', 'FLINT', 'FORGE', 'FOX', 'GALE', 'GLACIER', 'HANGAR', 'HARBOR', 'HAWK', 'HERON', 'KEEL', 'KESTREL',
  'LANCE', 'LANTERN', 'MARINER', 'MESA', 'METEOR', 'NAVIGATOR', 'OSPREY', 'OWL', 'PATHFINDER', 'PILOT', 'RAMPART',
  'RAVEN', 'RIDGE', 'RIVER', 'RUDDER', 'SCOUT', 'SENTINEL', 'SENTRY', 'SHIELD', 'SIGNAL', 'SPARK', 'SPARROW',
  'STAG', 'STAR', 'TIDE', 'TORCH',
];
// Single pairs stopped without removing either word. Empty for now: HIGH PILOT was blocked, then Brian removed
// HIGH from the first words altogether (11 Nov 2026), since HIGH COURIER, HIGH SCOUT and similar read the same way.
export const BLOCKED = [];

const A = new Set(FIRST), B = new Set(SECOND), X = new Set(BLOCKED.map(([a, b]) => a + ' ' + b));
export const callSignOk = (a, b) => A.has(a) && B.has(b) && !X.has(a + ' ' + b);

// What the page gets in state, so Random and the builder always use the current lists.
export const callSignLists = () => ({ first: FIRST, second: SECOND, blocked: BLOCKED.map(p => p.join(' ')) });
