// Carrying a starter pack from a social app's browser to a real one (13 Nov 2026).
// Run: node --import ./tests/declass/json-loader.mjs tests/declass/carry-pack.mjs
// Plain node, no server and no database: POST /api/starter with {token} only reads the signed token back.
import { onRequestPost } from '../../functions/api/starter.js';
import { drawStarter, makeToken } from '../../functions/_lib/starter.js';

let pass = 0, fail = 0;
const ok = (name, cond) => { cond ? pass++ : fail++; console.log((cond ? 'ok   ' : 'FAIL ') + name); };
const env = { SIGNING_KEY: 'test-signing-key', ID_SALT: 'salt', DB: null };
const post = body => onRequestPost({ env, request: new Request('https://ww2dispatches.com/api/starter', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) }) });

const t = new Date();
const picks = drawStarter(t);
ok('the catalog can deal a starter pack', picks.length === 5);
const token = await makeToken(env, picks, t);

let r = await post({ token }), d = await r.json();
ok('a good token reads back', r.status === 200);
ok('five cards come back', Array.isArray(d.pulls) && d.pulls.length === 5);
ok('the same cards and finishes, in order', d.pulls.every((p, i) => p.card === picks[i].card.id && p.finish === picks[i].finish && p.variant === 'still'));
ok('each card carries its picture', d.pulls.every(p => p.cardInfo && p.cardInfo.img));
ok('the token is handed back unchanged', d.token === token);
ok('no serials on a carried pack', d.pulls.every(p => p.serial === null));

r = await post({ token: token.slice(0, -3) + 'abc' });
ok('a tampered signature is refused', r.status === 410);
const [payload, sig] = token.split('.');
const forged = Buffer.from(JSON.stringify({ e: Math.floor(Date.now() / 1000) + 86400, c: picks.map(p => [p.card.id, 'gold']) })).toString('base64url');
r = await post({ token: forged + '.' + sig });
ok('a pack edited to all gold is refused', r.status === 410);
const old = await makeToken(env, picks, new Date(Date.now() - 31 * 86400000));
r = await post({ token: old });
ok('a pack older than 30 days is refused', r.status === 410);
r = await post({ token: 'nonsense' });
ok('nonsense is refused', r.status === 410);
r = await post({ token: await makeToken({ SIGNING_KEY: 'another-key' }, picks, t) });
ok('a token signed with another key is refused', r.status === 410);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
