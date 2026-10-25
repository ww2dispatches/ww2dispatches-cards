// POST /api/starter: open the free starter pack.
// Signed out: the five cards come back with a signed token the browser keeps until sign in.
// Signed in (and no starter yet): the cards go straight into the dossier, waiting to be turned.
import { json, fail } from '../_lib/util.js';
import { now, summary } from '../_lib/catalog.js';
import { signedInPlayer, publicPlayer } from '../_lib/player.js';
import { drawStarter, makeToken, saveStarter, STARTER_KEY } from '../_lib/starter.js';
import { signPending, withCard } from '../_lib/pulls.js';

export async function onRequestPost({ request, env }) {
  const t = now(env, request);
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
