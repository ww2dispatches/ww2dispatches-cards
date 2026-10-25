// GET /api/state: everything the home screen needs in one request. Replaces /api/me.
// Signed out: the envelope times only. Signed in: which are opened, waiting cards, priority
// envelopes, streak, and the whole pull history for the dossier (card details from /api/catalog).
import { json } from '../_lib/util.js';
import { now } from '../_lib/catalog.js';
import { signedInPlayer, publicPlayer } from '../_lib/player.js';
import { dailyOpen, commemorativeOpen, nextSlot, upcomingSlots } from '../_lib/envelopes.js';
import { signPending, publicPull, withCard } from '../_lib/pulls.js';

export async function onRequestGet({ request, env }) {
  const t = now(env, request);
  const daily = dailyOpen(t);
  const commemorative = commemorativeOpen(t);
  const base = { now: t.toISOString(), next: nextSlot(t), upcoming: upcomingSlots(t) };

  const player = await signedInPlayer(env, request);
  if (!player) return json({ ...base, player: null, envelopes: daily, commemorative, priority: 0, waiting: [], pulls: [] });

  await signPending(env, player.id);
  const [opened, pulls] = await env.DB.batch([
    env.DB.prepare('SELECT slot_key FROM opened WHERE player_id = ?').bind(player.id),
    env.DB.prepare('SELECT * FROM pulls WHERE player_id = ? ORDER BY id DESC').bind(player.id),
  ]);
  const done = new Set(opened.results.map(r => r.slot_key));
  const mark = e => ({ ...e, opened: done.has(e.key) });

  return json({
    ...base,
    player: publicPlayer(player, t),
    envelopes: daily.map(mark),
    commemorative: commemorative.map(mark),
    priority: player.priority_waiting,
    waiting: pulls.results.filter(r => !r.turned).reverse().map(r => withCard(r, t)),
    pulls: pulls.results.map(publicPull),
  });
}
