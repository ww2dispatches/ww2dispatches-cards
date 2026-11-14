// Email sign in server tests (13 Nov 2026). Run against a local server with the test clock on and a
// throwaway database (README, steps 3 and 4), with the real catalog:
//   DB=<the local D1 sqlite file> node tests/declass/email-signin.mjs
// On a test copy (ALLOW_FAKE_NOW=1) no mail is sent: the server hands the code back in the answer.
import { DatabaseSync } from 'node:sqlite';
const BASE = 'http://localhost:8799';
const db = new DatabaseSync(process.env.DB);
let pass = 0, failN = 0;
const ok = (cond, msg) => { if (cond) pass++; else { failN++; console.log('FAIL:', msg); } };
async function req(path, { body, now, cookie, fakeGoogle, fakeEmail } = {}) {
  const h = { 'x-declass-key': 't' };
  if (cookie) h.cookie = cookie;
  if (now) h['x-declass-now'] = now;
  if (fakeGoogle) h['x-declass-fake-google'] = fakeGoogle;
  if (fakeEmail) h['x-declass-fake-email'] = fakeEmail;
  if (body) { h['content-type'] = 'application/json'; h.origin = BASE; }
  const r = await fetch(BASE + '/api/' + path, { method: body ? 'POST' : 'GET', headers: h, body: body ? JSON.stringify(body) : undefined });
  const set = r.headers.get('set-cookie');
  return { status: r.status, data: await r.json().catch(() => ({})), cookie: set ? set.split(';')[0] : null };
}
const T0 = Date.parse('2026-11-20T18:00:00Z');
const at = min => new Date(T0 + min * 60000).toISOString();
const ask = (email, min = 0) => req('auth/email', { body: { email }, now: at(min) });
const enter = (email, code, min = 0, extra = {}) => req('auth/email', { body: Object.assign({ email, code }, extra), now: at(min) });
const count = sql => db.prepare(sql).get().n;
const run = Date.now().toString(36);
const addr = n => `${n}.${run}@example.com`;

// config says the form is on
let r = await req('config');
ok(r.data.emailSignIn === true, 'config: emailSignIn is on for a test copy');

// bad addresses are refused before anything is stored
for (const bad of ['', 'nope', 'a@b', 'two@@example.com', 'spa ce@example.com', 'x@.com', 'a@b..com'])
  ok((await ask(bad)).status === 400, 'bad address refused: ' + JSON.stringify(bad));

// ask, then sign in: a new player
const A = addr('alice');
r = await ask(A); const codeA = r.data.test;
ok(r.status === 200 && r.data.sent === true && /^\d{6}$/.test(codeA || ''), 'a code is made for a good address');
ok(count(`SELECT COUNT(*) n FROM email_codes WHERE id LIKE '%${'@'}%' OR code_hash LIKE '%${codeA}%'`) === 0, 'neither the address nor the code is stored in the clear');
r = await enter(A, '000000' === codeA ? '111111' : '000000');
ok(r.status === 401 && r.data.error === 'wrong code' && !r.cookie, 'a wrong code is refused, no session');
r = await enter(A, codeA.slice(0, 3) + ' ' + codeA.slice(3), 1);
ok(r.status === 200 && r.cookie && r.data.player, 'the right code signs in (typed with a space)');
const cookieA = r.cookie, fileA = r.data.player.file || r.data.player.fileNumber;
let st = await req('state', { cookie: cookieA, now: at(1) });
ok(st.status === 200 && st.data.player, 'the session cookie works');
const whoA = JSON.stringify(st.data.player.file || st.data.player.fileNumber || st.data.player);
r = await enter(A, codeA, 2);
ok(r.status === 410, 'the same code cannot be used twice');

// same address, any capitals or spaces: the same dossier
r = await ask('  ' + A.toUpperCase() + ' ', 5); 
ok(r.status === 200, 'asking again after a minute works');
r = await enter(A.toUpperCase(), r.data.test, 5);
st = await req('state', { cookie: r.cookie, now: at(5) });
ok(JSON.stringify(st.data.player.file || st.data.player.fileNumber || st.data.player) === whoA, 'capitals and spaces in the address reach the same dossier');

// asking twice inside a minute is slowed, and the first code still works
const B = addr('bob');
r = await ask(B, 10); const codeB = r.data.test;
let r2 = await ask(B, 10.5);
ok(r2.status === 429 && r2.data.error === 'wait' && r2.data.wait > 0, 'a second ask inside a minute is told to wait');
r = await enter(B, codeB, 11);
ok(r.status === 200, 'the first code still works after the refused second ask');

// expiry: ten minutes
const C = addr('carol');
r = await ask(C, 20); 
ok((await enter(C, r.data.test, 31)).status === 410, 'a code older than ten minutes has run out');

// five wrong tries lock the code, even for the right one after
const D = addr('dave');
r = await ask(D, 40); const codeD = r.data.test; const wrong = codeD === '123456' ? '654321' : '123456';
let last;
for (let i = 0; i < 5; i++) last = await enter(D, wrong, 41);
ok(last.status === 410 && last.data.error === 'code locked', 'the fifth wrong try locks the code');
ok((await enter(D, codeD, 41)).status === 410, 'the right code is refused once locked');
r = await ask(D, 43);
ok(r.status === 200 && (await enter(D, r.data.test, 43)).status === 200, 'a new code after a lock works');

// five sends an hour to one address
const E = addr('erin');
let sent = 0, slowed = null;
for (let i = 0; i < 7; i++) { r = await ask(E, 60 + i * 2); if (r.status === 200) sent++; else slowed = r; }
ok(sent === 5 && slowed && slowed.data.error === 'slow', 'the sixth send in an hour is refused (' + sent + ' sent)');
ok((await ask(E, 60 + 61)).status === 200, 'an hour later sends work again');

// eight tries of one right code at once: exactly one signs in
const F = addr('frank');
r = await ask(F, 200); const codeF = r.data.test;
const many = await Promise.all(Array.from({ length: 8 }, () => enter(F, codeF, 200)));
ok(many.filter(x => x.status === 200).length === 1, 'eight uses of one code at once: exactly one signs in (' + many.filter(x => x.status === 200).length + ')');

// a starter pack opened before sign in is saved by email sign in
const G = addr('gina');
const pack = await req('starter', { body: {}, now: at(210) });
ok(pack.status === 200 && pack.data.token && pack.data.pulls.length === 5, 'a guest starter pack is dealt');
r = await ask(G, 210);
r = await enter(G, r.data.test, 210, { starter: pack.data.token, starterTurned: true, src: 'threads' });
ok(r.status === 200 && r.data.starterSaved === true, 'email sign in saves the starter pack');
st = await req('state', { cookie: r.cookie, now: at(210) });
const key = p => p.card + ':' + p.finish;
ok(st.data.pulls.length === 5 && st.data.pulls.map(key).sort().join() === pack.data.pulls.map(key).sort().join(), 'the five cards are in the dossier');
r = await ask(G, 212); r = await enter(G, r.data.test, 212, { starter: pack.data.token });
ok(r.status === 200 && r.data.starterSaved === false, 'the same pack is not saved twice');

// Google first, then email with the same address: one dossier
const H = addr('hank');
r = await req('auth/google', { body: { credential: 'x' }, fakeGoogle: 'hank-' + run, fakeEmail: H, now: at(220) });
ok(r.status === 200 && r.cookie, 'fake Google sign in works');
st = await req('state', { cookie: r.cookie, now: at(220) }); const whoH = JSON.stringify(st.data.player);
r = await ask(H, 221); r = await enter(H, r.data.test, 221);
st = await req('state', { cookie: r.cookie, now: at(221) });
ok(JSON.stringify(st.data.player) === whoH, 'Google first, then email: the same dossier');

// email first, then Google with the same address: one dossier
const I = addr('iris');
r = await ask(I, 230); r = await enter(I, r.data.test, 230);
st = await req('state', { cookie: r.cookie, now: at(230) }); const whoI = JSON.stringify(st.data.player);
r = await req('auth/google', { body: { credential: 'x' }, fakeGoogle: 'iris-' + run, fakeEmail: I.toUpperCase(), now: at(231) });
st = await req('state', { cookie: r.cookie, now: at(231) });
ok(JSON.stringify(st.data.player) === whoI, 'email first, then Google: the same dossier');
r = await req('auth/google', { body: { credential: 'x' }, fakeGoogle: 'iris-' + run, now: at(232) });
st = await req('state', { cookie: r.cookie, now: at(232) });
ok(JSON.stringify(st.data.player) === whoI, 'that Google account keeps opening the same dossier, even with no address');

// Google with no address at all still works as before
r = await req('auth/google', { body: { credential: 'x' }, fakeGoogle: 'solo-' + run, now: at(240) });
ok(r.status === 200 && r.cookie, 'Google sign in with no address works as before');

// Delete my dossier clears the second ids, and the address starts fresh
r = await ask(H, 250); r = await enter(H, r.data.test, 250);
const before = count('SELECT COUNT(*) n FROM aliases');
const del = await req('delete', { body: {}, cookie: r.cookie, now: at(250) });
ok(del.status === 200 && count('SELECT COUNT(*) n FROM aliases') === before - 1, 'Delete my dossier removes the second id');
r = await ask(H, 252); r = await enter(H, r.data.test, 252);
st = await req('state', { cookie: r.cookie, now: at(252) });
ok(r.status === 200 && JSON.stringify(st.data.player) !== whoH && st.data.pulls.length === 0, 'after deleting, the address starts a fresh dossier');

// nothing readable is kept
const rows = db.prepare('SELECT id, code_hash FROM email_codes').all().concat(db.prepare('SELECT alias AS id, player_id AS code_hash FROM aliases').all()).concat(db.prepare("SELECT id, '' AS code_hash FROM players").all());
ok(rows.every(x => !/@|example|alice|bob|hank|iris/i.test(x.id + x.code_hash)), 'no address appears anywhere in the database');

console.log(`\n${pass} passed, ${failN} failed`);
process.exit(failN ? 1 : 0);
