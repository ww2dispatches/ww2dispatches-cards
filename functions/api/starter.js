// POST /api/starter: open the free starter pack.
// With {token}: read back a pack this visitor already opened in another browser (13 Nov 2026). Social apps
// open links in their own built in browser, where Google will not sign anyone in, so the save screen hands
// the visitor a link that carries the pack's token to their real browser. Nothing is drawn or saved here;
// the token is the same signed one the first browser holds, and an account can still only keep one pack.
// Signed out: the five cards come back with a signed token the browser keeps until sign in.
// Signed in (and no starter yet): the cards go straight into the dossier, waiting to be turned.
import { json, fail } from '../_lib/util.js';
import { now, summary } from '../_lib/catalog.js';
import { signedInPlayer, publicPlayer } from '../_lib/player.js';
import { drawStarter, makeToken, readToken, saveStarter, STARTER_KEY } from '../_lib/starter.js';
import { signPending, withCard } from '../_lib/pulls.js';

export async function onRequestPost({ request, env }) {
  const t = now(env, request);
  let body = {};
  try { body = (await request.json()) || {}; } catch { body = {}; }
  if (body.token) {
    const carried = await readToken(env, body.token, t);
    if (!carried) return fail(410, 'pack expired');
    return json({
      token: String(body.token),
      pulls: carried.map(p => ({ card: p.card.id, variant: p.variant, finish: p.finish, serial: null, cardInfo: summary(p.card, t) })),
    });
  }
  const player = await signedInPlayer(env, request);
  if (player && player.starter_done) return fail(409, 'already opened');

  const picks = drawStarter(t);
  if (picks.length < 5) return fail(409, 'not available');

  if (!player) {
    return json({
      token: await makeToken(env, picks, t),
      pulls: picks.map(p => ({ card: p.card.id, variant: p.variant, finish: p.finish, serial: null, cardInfo: summary(p.card, t) })),
    });
  }

  if (!(await saveStarter(env, player.id, picks, t, false))) return fail(409, 'already opened');
  await signPending(env, player.id);
  const rows = await env.DB.prepare('SELECT * FROM pulls WHERE player_id = ? AND slot_key = ? ORDER BY id').bind(player.id, STARTER_KEY).all();
  const fresh = await env.DB.prepare('SELECT * FROM players WHERE id = ?').bind(player.id).first();
  return json({ pulls: rows.results.map(r => withCard(r, t)), player: publicPlayer(fresh, t) });
}
