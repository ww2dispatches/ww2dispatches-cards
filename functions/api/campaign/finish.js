// POST /api/campaign/finish {ticket, choices}: the page's list of choices for a finished run. The server
// replays them through the shared engine with the run's own deck and seed; only that result is saved and
// ranked. The day's best run per player feeds the day histogram, and the best run of the month feeds the
// chapter histogram. Winning a chapter unlocks the next one.
import { json, fail } from '../../_lib/util.js';
import { now } from '../../_lib/catalog.js';
import { signedInPlayer } from '../../_lib/player.js';
import * as C from '../../_lib/campaigns.js';
import * as E from '../../../site/declass/campaigns/engine.js';

export async function onRequestPost({ request, env }) {
  const t = now(env, request);
  const player = await signedInPlayer(env, request);
  if (!player) return fail(401, 'sign in');
  if (!C.campaignsOpen(env, request, player)) return fail(403, 'coming soon');
  let body;
  try { body = await request.json(); } catch { return fail(400, 'bad request'); }
  const runId = await C.readTicket(env, body && body.ticket, player.id);
  if (!runId) return fail(400, 'bad ticket');
  const choices = body.choices;
  if (!Array.isArray(choices) || choices.length > C.CHOICES_MAX) return fail(400, 'bad choices');
  const db = env.DB;
  await C.ensureTables(db);
  const run = await db.prepare('SELECT * FROM campaign_runs WHERE id = ? AND player_id = ?').bind(runId, player.id).first();
  if (!run) return fail(404, 'no such run');
  if (run.status !== 'play') return json({ result: 'already', run: publicRun(run) });
  const slot = C.campaignFor(new Date(run.started_at), !C.CAMPAIGNS_LIVE);
  if (!slot || slot.campaign.id !== run.campaign_id) return fail(409, 'campaign over');
  const { campaign } = slot;

  const r = E.replay(campaign, run.chapter, JSON.parse(run.deck), run.seed, choices);
  if (!r.ok) {
    await db.prepare("UPDATE campaign_runs SET status = 'refused', finished_at = ? WHERE id = ? AND status = 'play'").bind(t.toISOString(), run.id).run();
    return json({ result: 'refused', error: r.error }, 400);
  }
  const o = r.result, score = r.score, at = t.toISOString();
  const pid = player.id, cid = campaign.id, chN = run.chapter, day = run.day, year = slot.year;
  // Is this the player's best run today, and best this month?
  const dayBest = await db.prepare('SELECT score FROM campaign_day_best WHERE player_id = ? AND campaign_id = ? AND chapter = ? AND day = ?').bind(pid, cid, chN, day).first();
  const prog = await db.prepare('SELECT * FROM campaign_progress WHERE player_id = ? AND campaign_id = ? AND year = ? AND chapter = ?').bind(pid, cid, year, chN).first();
  const stmts = [
    // Compare and set on the status, so the same run finished twice at once is saved once.
    db.prepare(`UPDATE campaign_runs SET status = 'done', choices = ?, won = ?, resolve = ?, rounds = ?, waves = ?, destroyed = ?, score = ?, finished_at = ? WHERE id = ? AND status = 'play'`)
      .bind(JSON.stringify(choices), o.won ? 1 : 0, o.resolve, o.rounds, o.wavesCleared, o.destroyed, score, at, run.id),
  ];
  const done = `EXISTS (SELECT 1 FROM campaign_runs WHERE id = '${run.id}' AND finished_at = '${at}')`;
  const bump = (kind, k, oldScore) => {
    if (oldScore != null) stmts.push(db.prepare(`UPDATE campaign_ranks SET n = n - 1 WHERE campaign_id = ? AND chapter = ? AND kind = ? AND k = ? AND score = ? AND ${done}`).bind(cid, chN, kind, k, oldScore));
    stmts.push(db.prepare(`INSERT INTO campaign_ranks (campaign_id, chapter, kind, k, score, n) SELECT ?, ?, ?, ?, ?, 1 WHERE ${done} ON CONFLICT (campaign_id, chapter, kind, k, score) DO UPDATE SET n = n + 1`).bind(cid, chN, kind, k, score));
  };
  if (!dayBest || score > dayBest.score) {
    stmts.push(db.prepare(`INSERT INTO campaign_day_best (player_id, campaign_id, chapter, day, score) SELECT ?, ?, ?, ?, ? WHERE ${done} ON CONFLICT (player_id, campaign_id, chapter, day) DO UPDATE SET score = excluded.score`).bind(pid, cid, chN, day, score));
    bump('day', day, dayBest ? dayBest.score : null);
  }
  const newBest = !prog || prog.best == null || score > prog.best;
  if (newBest) bump('chapter', year, prog ? prog.best : null);
  stmts.push(db.prepare(`INSERT INTO campaign_progress (player_id, campaign_id, year, chapter, won_at, best, best_day) SELECT ?1, ?2, ?3, ?4, ?5, ?6, ?7 WHERE ${done}
    ON CONFLICT (player_id, campaign_id, year, chapter) DO UPDATE SET won_at = COALESCE(won_at, excluded.won_at),
      best = CASE WHEN best IS NULL OR excluded.best > best THEN excluded.best ELSE best END,
      best_day = CASE WHEN best IS NULL OR excluded.best > best THEN excluded.best_day ELSE best_day END`)
    .bind(pid, cid, year, chN, o.won ? at : null, score, day));
  const res = await db.batch(stmts);
  if (!(res[0].meta && res[0].meta.changes)) return json({ result: 'already' });
  const dayRank = await C.percentile(db, cid, chN, 'day', day, Math.max(score, dayBest ? dayBest.score : -1));
  const chapterRank = await C.percentile(db, cid, chN, 'chapter', year, Math.max(score, prog && prog.best != null ? prog.best : -1));
  return json({ bands: C.BAND_INTEL, monthEnds: slot.preview ? null : C.monthEndsAt(campaign, year).toISOString(), result: o.won ? 'won' : 'lost', outcome: o, score, bestToday: !dayBest || score > dayBest.score, dayRank, chapterRank, unlocked: o.won && chN < campaign.chapters.length ? chN + 1 : null });
}
const publicRun = r => ({ chapter: r.chapter, day: r.day, runNo: r.run_no, status: r.status, won: Boolean(r.won), resolve: r.resolve, rounds: r.rounds, score: r.score });
