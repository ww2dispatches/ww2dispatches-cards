// GET /api/campaign: this month's campaign for the page. Its chapters (the enemy and debriefs only once
// a chapter is released), the player's progress and runs left today, the loaners, and the player's own
// cards that can be played, with their game numbers.
import { json, fail } from '../../_lib/util.js';
import { now, findCard } from '../../_lib/catalog.js';
import { signedInPlayer } from '../../_lib/player.js';
import * as C from '../../_lib/campaigns.js';

export async function onRequestGet({ request, env }) {
  const t = now(env, request);
  const player = await signedInPlayer(env, request);
  if (!C.campaignsOpen(env, request, player)) return json({ status: 'soon' });
  const slot = C.campaignFor(t, !C.CAMPAIGNS_LIVE);
  if (!slot) return json({ status: 'none' });
  const { campaign } = slot, day = C.gameDay(t);
  const base = { status: 'open', day, runsPerDay: C.RUNS_PER_DAY, campaign: { id: campaign.id, title: campaign.title, council: campaign.council, side: campaign.side, year: campaign.year, startResolve: campaign.startResolve, table: campaign.table } };
  if (!player) return json({ ...base, status: 'signin', chapters: campaign.chapters.map(ch => C.publicChapter(slot, ch, t, new Map())) });
  const db = env.DB;
  await C.ensureTables(db);
  const progress = await C.progressOf(db, player.id, slot);
  const chapters = [];
  for (const ch of campaign.chapters) {
    const pc = C.publicChapter(slot, ch, t, progress);
    if (pc.released) pc.runsLeft = Math.max(0, C.RUNS_PER_DAY - await C.runsToday(db, player.id, campaign.id, ch.n, day));
    chapters.push(pc);
  }
  const owned = (await db.prepare('SELECT DISTINCT card_id FROM pulls WHERE player_id = ?').bind(player.id).all()).results || [];
  const cards = [];
  for (const { card_id } of owned) {
    const card = findCard(card_id, t);
    if (!card || card.kind !== 'dispatch') continue;
    const g = card.game || {};
    // why: for each released chapter, the reason this card can't go in its deck ('' when it can), the
    // same check the server makes at the start of a run, so the deck builder can grey it out and say why.
    const p = C.playable(card), why = {};
    for (const ch of campaign.chapters) if (C.chapterReleased(slot, ch, t)) why[ch.n] = C.cardProblem(campaign, ch, p);
    cards.push({ id: card.id, title: card.title, short: card.short, series: p ? p.series : card.series, flash: Boolean(card.flash), date: card.date, img: card.img, value: g.value, branches: g.branches || [], keyword: g.keyword || null, role: g.role || null, noPlay: Boolean(g.noPlay), why });
  }
  const loaners = C.LOANERS.filter(l => l.side === campaign.side).map(l => {
    const why = {};
    for (const ch of campaign.chapters) if (C.chapterReleased(slot, ch, t)) why[ch.n] = C.cardProblem(campaign, ch, { series: l.series, value: l.value, branches: l.branches, keyword: l.keyword || null });
    return { ...l, why };
  });
  return json({ ...base, chapters, loaners, cards });
}
