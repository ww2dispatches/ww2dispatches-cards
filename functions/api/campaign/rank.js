// GET /api/campaign/rank?chapter=N: the player's percentile today and for the month in that chapter.
// Provisional until the month ends; no names anywhere.
import { json, fail } from '../../_lib/util.js';
import { now } from '../../_lib/catalog.js';
import { signedInPlayer } from '../../_lib/player.js';
import * as C from '../../_lib/campaigns.js';

export async function onRequestGet({ request, env }) {
  const t = now(env, request);
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');
  if (!C.campaignsOpen(env, request, player)) return fail(403, 'coming soon');
  const slot = C.campaignFor(t, !C.CAMPAIGNS_LIVE);
  if (!slot) return fail(409, 'no campaign');
  const chN = Number(new URL(request.url).searchParams.get('chapter'));
  if (!slot.campaign.chapters.some(c => c.n === chN)) return fail(400, 'bad chapter');
  const db = env.DB, cid = slot.campaign.id, day = C.gameDay(t);
  await C.ensureTables(db);
  const d = await db.prepare('SELECT score FROM campaign_day_best WHERE player_id = ? AND campaign_id = ? AND chapter = ? AND day = ?').bind(player.id, cid, chN, day).first();
  const p = await db.prepare('SELECT best FROM campaign_progress WHERE player_id = ? AND campaign_id = ? AND year = ? AND chapter = ?').bind(player.id, cid, slot.year, chN).first();
  return json({
    day, provisional: true,
    today: d ? await C.percentile(db, cid, chN, 'day', day, d.score) : null,
    chapter: p && p.best != null ? await C.percentile(db, cid, chN, 'chapter', slot.year, p.best) : null,
  });
}
