// POST /api/campaign/start {chapter, deck: [{card} | {loaner}] x 20}: start a run. The server checks the
// chapter is released and unlocked, a run is left today, and the deck follows every rule, then saves the
// run and hands back its seed in a signed ticket. A started run counts against today's runs even if it
// is never finished, so starting over can't buy a better draw.
import { json, fail } from '../../_lib/util.js';
import { now } from '../../_lib/catalog.js';
import { signedInPlayer } from '../../_lib/player.js';
import * as C from '../../_lib/campaigns.js';

export async function onRequestPost({ request, env }) {
  const t = now(env, request);
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');
  if (!C.campaignsOpen(env, request, player)) return fail(403, 'coming soon');
  let body;
  try { body = await request.json(); } catch { return fail(400, 'bad request'); }
  const slot = C.campaignFor(t, !C.CAMPAIGNS_LIVE);
  if (!slot) return fail(409, 'no campaign');
  const { campaign } = slot, chN = Number(body && body.chapter);
  const ch = campaign.chapters.find(c => c.n === chN);
  if (!ch) return fail(400, 'bad chapter');
  const db = env.DB;
  await C.ensureTables(db);
  const progress = await C.progressOf(db, player.id, slot);
  const pc = C.publicChapter(slot, ch, t, progress);
  if (!pc.released) return fail(409, 'not released');
  if (!pc.unlocked) return fail(409, 'locked');
  const day = C.gameDay(t);
  const used = await C.runsToday(db, player.id, campaign.id, chN, day);
  if (used >= C.RUNS_PER_DAY) return fail(409, 'no runs left');
  const owned = new Set(((await db.prepare('SELECT DISTINCT card_id FROM pulls WHERE player_id = ?').bind(player.id).all()).results || []).map(r => r.card_id));
  const { deck, problems } = C.buildDeck(campaign, chN, body.deck, owned, t);
  if (!deck) return json({ error: 'deck', problems }, 400);
  const runNo = used + 1, id = C.newRunId(), seed = await C.runSeed(env, campaign.id, chN, day, runNo);
  try {
    await db.prepare('INSERT INTO campaign_runs (id, player_id, campaign_id, chapter, day, run_no, deck, seed, started_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)')
      .bind(id, player.id, campaign.id, chN, day, runNo, JSON.stringify(deck), seed, t.toISOString()).run();
  } catch (err) {
    if (String(err && err.message).includes('UNIQUE')) return fail(409, 'try again'); // two starts at once took the same run number
    throw err;
  }
  return json({ ticket: await C.ticketFor(env, id, player.id), seed, runNo, runsLeft: C.RUNS_PER_DAY - runNo, deck, engine: 1 });
}
