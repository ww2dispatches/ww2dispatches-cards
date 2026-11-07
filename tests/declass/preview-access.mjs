// Tester preview access after launch (7 Nov 2026). Launch night wipes the players table and then sets
// LAUNCHED to 1, so every account signs in again with tester = 0. The Code Room preview must still open
// for Brian and for named testers, by file number, without touching the database. Runs in plain node:
//   node --import ./tests/declass/json-loader.mjs tests/declass/preview-access.mjs
// The local server suite (intercept.mjs) runs with the test clock on, which opens the puzzle to
// everyone, so this checks interceptOpen and the admin list directly with a production style env.
import { interceptOpen, INTERCEPT_LIVE } from '../../functions/_lib/intercept.js';
import { isAdmin, isTester } from '../../functions/_lib/admins.js';
import { playerFileNumber } from '../../functions/_lib/fileno.js';
import { b64url } from '../../functions/_lib/util.js';

let pass = 0, failN = 0;
const ok = (cond, msg) => { if (cond) pass++; else { failN++; console.log('FAIL:', msg); } };

// A player id whose file number is the one asked for (ids are 32 characters of base64url).
const ALPHA = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
function idFor(file) {
  let bits = 0n;
  for (const ch of file) bits = (bits << 5n) | BigInt(ALPHA.indexOf(ch));
  const bytes = new Uint8Array(24);
  for (let i = 4; i >= 0; i--) { bytes[i] = Number(bits & 255n); bits >>= 8n; }
  for (let i = 5; i < 24; i++) bytes[i] = (i * 37) & 255;
  return b64url(bytes);
}
const randomId = () => b64url(crypto.getRandomValues(new Uint8Array(24)));

const brian = { id: idFor('WKB9MK5Y'), tester: 0 };
ok(playerFileNumber(brian.id) === 'WKB9MK5Y', 'the crafted id has Brian\'s file number');
const stranger = { id: randomId(), tester: 0 };
const named = { id: randomId(), tester: 0 };
const helper = { id: randomId(), tester: 0 };
const oldTester = { id: randomId(), tester: 1 };
const fileOf = p => playerFileNumber(p.id);

// Production after launch: no test clock, LAUNCHED on, the two lists as Brian would set them.
const env = { LAUNCHED: '1', TESTER_FILES: ' ' + fileOf(named).toLowerCase() + ' ,', ADMIN_FILES: fileOf(helper) };
const preview = new Request('https://ww2dispatches.com/api/intercept', { headers: { 'x-intercept-preview': '1' } });
const plain = new Request('https://ww2dispatches.com/api/intercept');

ok(INTERCEPT_LIVE === false, 'Code Room is still behind its launch switch');
ok(interceptOpen(env, preview, brian), 'Brian keeps the preview after the wipe (tester 0)');
ok(!interceptOpen(env, plain, brian), 'Brian without the preview flag sees what players see');
ok(interceptOpen(env, preview, named), 'a file number in TESTER_FILES opens the preview (case and spaces forgiven)');
ok(interceptOpen(env, preview, helper), 'a file number in ADMIN_FILES opens the preview');
ok(interceptOpen(env, preview, oldTester), 'a player flagged tester in the database still opens it');
ok(!interceptOpen(env, preview, stranger), 'anyone else with the preview flag is refused');
ok(!interceptOpen(env, preview, null), 'signed out is refused');
ok(!interceptOpen({ LAUNCHED: '1' }, preview, named), 'with TESTER_FILES empty, the named tester is refused');

ok(isAdmin(env, brian) && isAdmin(env, helper), 'the console admits Brian and ADMIN_FILES');
ok(!isAdmin(env, named), 'TESTER_FILES never opens the admin console');
ok(!isAdmin(env, stranger) && !isAdmin(env, null), 'the console refuses everyone else');
ok(isTester(env, named) && !isTester(env, stranger), 'isTester matches the lists');

console.log(`${pass} passed, ${failN} failed`);
process.exit(failN ? 1 : 0);
