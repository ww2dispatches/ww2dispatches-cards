// The free starter pack (Envelope doc, First visit): five cards, today's dispatch plus one from
// each series, at least one silver or better. Opened before sign in, it travels as a signed
// token the browser holds, and is saved into the dossier when the player signs in. Each
// account can only ever have one starter pack (the opened table's "s:starter" key).
//
// No Top Secret in starter packs: a pack can be reopened in a fresh browser before sign in, so a
// numbered serial there could be farmed. A Top Secret roll becomes a gold.
import { b64url, unb64url, hmac, hmacVerify } from './util.js';
import { postedCards, findCard } from './catalog.js';
import { rollFinish, secureInt } from './odds.js';

export const STARTER_KEY = 's:starter';
const SERIES = ['battle', 'home', 'blue', 'state'];
const TOKEN_DAYS = 30;

export function drawStarter(t, rnd = secureInt) {
  const dispatches = postedCards(t).filter(c => c.kind === 'dispatch' && !c.flash); // Flash cards come only from their file or the 1 in 200 roll
  if (!dispatches.length) return [];
  const today = dispatches[dispatches.length - 1]; // the newest posted dispatch
  const cards = [today];
  for (const s of SERIES) {
    let pool = dispatches.filter(c => c.series === s && c.id !== today.id && !cards.includes(c));
    if (!pool.length) pool = dispatches.filter(c => !cards.includes(c));
    if (pool.length) cards.push(pool[rnd(pool.length)]);
  }
  const picks = cards.map(card => {
    const f = rollFinish('still', rnd);
    return { card, variant: 'still', finish: f === 'topsecret' ? 'gold' : f };
  });
  if (picks.every(p => p.finish === 'copper')) picks[rnd(picks.length)].finish = 'silver';
  return picks;
}

export async function makeToken(env, picks, t) {
  const payload = b64url(new TextEncoder().encode(JSON.stringify({
    e: Math.floor(t.getTime() / 1000) + TOKEN_DAYS * 86400,
    c: picks.map(p => [p.card.id, p.finish]),
  })));
  return `${payload}.${await hmac(env.SIGNING_KEY, 'starter:' + payload)}`;
}

// The picks inside a valid token, or null.
export async function readToken(env, token, t) {
  const [payload, sig] = String(token || '').split('.');
  if (!payload || !sig || !(await hmacVerify(env.SIGNING_KEY, 'starter:' + payload, sig))) return null;
  try {
    const data = JSON.parse(new TextDecoder().decode(unb64url(payload)));
    if (!data.e || data.e < t.getTime() / 1000 || !Array.isArray(data.c) || data.c.length !== 5) return null;
    const ok = new Set(['copper', 'silver', 'gold']);
    const picks = data.c.map(([id, finish]) => ({ card: findCard(id, t), variant: 'still', finish }));
    if (picks.some(p => !p.card || !ok.has(p.finish))) return null;
    return picks;
  } catch { return null; }
}

// Save a starter pack into a player's dossier. turned: whether the player has already seen
// the cards (a pack opened before sign in) or will turn them now. False if they already have one.
export async function saveStarter(env, playerId, picks, t, turned) {
  const db = env.DB, at = t.toISOString();
  const stmts = [
    db.prepare('INSERT INTO opened (player_id, slot_key, opened_at) VALUES (?, ?, ?)').bind(playerId, STARTER_KEY, at),
    db.prepare('UPDATE players SET starter_done = 1 WHERE id = ?').bind(playerId),
    ...picks.map(p => db.prepare(
      `INSERT INTO pulls (player_id, card_id, variant, finish, serial, slot_key, pulled_at, signature, turned)
       VALUES (?, ?, ?, ?, NULL, ?, ?, '', ?)`
    ).bind(playerId, p.card.id, p.variant, p.finish, STARTER_KEY, at, turned ? 1 : 0)),
  ];
  try {
    await db.batch(stmts);
    return true;
  } catch (err) {
    if (String(err && err.message).includes('UNIQUE')) return false;
    throw err;
  }
}
