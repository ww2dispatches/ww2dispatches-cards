// Who is an admin, and who keeps tester access after launch (7 Nov 2026). Both go by file number,
// which comes from the scrambled Google id, so it stays the same when the players table is wiped
// on launch night. Nothing here touches the database.
//   ADMINS (below) and the ADMIN_FILES variable: the admin console, plus every tester preview.
//   The TESTER_FILES variable: tester previews only (Code Room's ?intercept=preview), not the console.
// Both variables are comma separated file numbers, set in Cloudflare (Pages, Settings, Variables).
import { playerFileNumber } from './fileno.js';

export const ADMINS = new Set(['WKB9MK5Y']); // Brian

const listOf = v => String(v || '').split(',').map(x => x.trim().toUpperCase()).filter(Boolean);

export const adminFiles = env => new Set([...ADMINS, ...listOf(env.ADMIN_FILES)]);
export const testerFiles = env => new Set([...adminFiles(env), ...listOf(env.TESTER_FILES)]);

export const isAdmin = (env, player) => Boolean(player && player.id && adminFiles(env).has(playerFileNumber(player.id)));

// A tester for previews: flagged in the database (signed in before launch) or named by file number.
export const isTester = (env, player) => Boolean(player && (player.tester || (player.id && testerFiles(env).has(playerFileNumber(player.id)))));
