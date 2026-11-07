// Campaigns on the server (build session 2, 6 Nov 2026). Campaigns Build doc.
// The page plays a chapter with the shared rules engine; the server checks the deck, hands out the run's
// seed in a signed ticket, and replays the finished run through the same engine before saving or ranking
// anything. No result from the page is ever trusted.
import * as E from '../../site/declass/campaigns/engine.js';
import battleOfBritain from '../_data/campaigns/1940-08-battle-of-britain.json';
import schedule from '../_data/campaigns/schedule.json';
import loanerData from '../_data/loaners.json';
import { findCard } from './catalog.js';
import { gameDay, zonedTime, isoSec, addDays } from './time.js';
import { hmac, hmacVerify } from './util.js';

// Launch switch. Until it is true, only a tester sending the preview header (or a local copy with the
// test clock) can reach Campaigns. Launching is a one line change here, no Cloudflare step.
export const CAMPAIGNS_LIVE = false;

// Settings (Campaigns Build doc, "Settings"): start values, tuned in the soft launch.
export const RUNS_PER_DAY = 3;          // per chapter, per Eastern game day
export const PREVIEW_RUNS_PER_DAY = 50; // on a preview deploy (*.pages.dev, its own database), so Brian can test freely
// Runs a day for this request: the real setting on ww2dispatches.com (and locally), a high limit on a
// branch preview, which uses the separate preview database and never reaches players.
export function runsPerDay(request) {
  try { return new URL(request.url).hostname.endsWith('.pages.dev') ? PREVIEW_RUNS_PER_DAY : RUNS_PER_DAY; } catch { return RUNS_PER_DAY; }
}
export const CHOICES_MAX = 4000;
// Intel paid when a chapter's month ends, by the player's band in that chapter's month rank (Campaigns
// doc, Ranking: top 5%, top 25%, top 50%, everyone who finished a run). Start values for Brian to approve.
export const BAND_INTEL = { top5: 50, top25: 30, top50: 20, finished: 10 };
export const bandOf = top => top <= 5 ? 'top5' : top <= 25 ? 'top25' : top <= 50 ? 'top50' : 'finished';
export const BAND_NAME = { top5: 'top 5%', top25: 'top 25%', top50: 'top 50%', finished: 'finished' };        // a finished run is a few hundred choices; anything far past that is refused

const CAMPAIGNS = new Map([battleOfBritain].map(c => [c.id, c]));
export const LOANERS = loanerData.loaners;
const LOANER_BY_ID = new Map(LOANERS.map(l => [l.id, l]));

export function campaignsOpen(env, request, player) {
  if (CAMPAIGNS_LIVE) return true;
  if (env.ALLOW_FAKE_NOW === '1') return true;
  return Boolean(player && player.tester && request.headers.get('x-campaigns-preview') === '1');
}

// Which campaign runs in the month of moment t (Eastern), and the year it runs in. schedule.json maps
// "YYYY-MM" to a campaign id. Before launch a tester previewing gets the reference campaign with every
// chapter open, so the page can be played on preview at any time of year.
export function campaignFor(t, preview = false) {
  const day = gameDay(t), ym = day.slice(0, 7);
  const id = schedule.months[ym];
  if (id && CAMPAIGNS.has(id)) return { campaign: CAMPAIGNS.get(id), year: ym.slice(0, 4), preview: false };
  if (preview && CAMPAIGNS.has(schedule.preview)) return { campaign: CAMPAIGNS.get(schedule.preview), year: ym.slice(0, 4), preview: true };
  return null;
}
// A chapter opens at midnight Eastern on its date. In preview every chapter is open.
export function chapterOpensAt(slot, ch) {
  if (slot.preview) return null;
  return isoSec(zonedTime(`${slot.year}-${ch.opens}`, '00:00'));
}
export function chapterReleased(slot, ch, t) {
  const at = chapterOpensAt(slot, ch);
  return at === null || at <= isoSec(t);
}

// ---------- the deck ----------
// A card from the catalog as the engine sees it, or null if it can never be played in this chapter.
export function playable(card) {
  const g = card.game || {};
  if (card.kind !== 'dispatch' || card.flash && !g.role) return null;
  const series = card.flash ? ({ operation: 'battle', machine: 'blue', rally: 'home', statecraft: 'state' })[g.role] : card.series;
  if (!['blue', 'battle', 'home', 'state'].includes(series)) return null;
  return { series, value: g.value, branches: g.branches || [], keyword: g.keyword || null, noPlay: Boolean(g.noPlay), title: card.title, date: card.date, lens: card.lens || null };
}
// Why one card can't go in this chapter's deck ('' if it can). The era rule: the card's date is no later
// than the campaign's year and never after the formal surrender (2 September 1945). The side rule: Allied
// campaigns take Allied and civilian lens cards (cards with no lens yet count as Allied until the backfill).
export function cardProblem(campaign, ch, c) {
  if (!c) return 'This card is not played in Campaigns.';
  if (c.noPlay) return 'This card can never be played.';
  if (c.date) {
    if (c.date > '1945-09-02') return 'Postwar cards are for collecting only.';
    if (Number(c.date.slice(0, 4)) > campaign.year) return `Only cards from ${campaign.year} or earlier fit this campaign.`;
  }
  if (!(c.value >= 1 && c.value <= 7)) return 'This card has no number yet.';
  const axis = campaign.side === 'axis';
  if (c.lens && c.lens !== 'civilian_neutral' && axis !== c.lens.startsWith('axis_')) return 'This card is from the other side.';
  if (!E.fitsChapter(ch, c)) {
    const need = { air: 'the plane', sea: 'the anchor', land: 'the tank' };
    return `This chapter is ${ch.branches.join(' and ')} only: machines and operations need ${ch.branches.map(b => need[b] || b).join(' or ')}.`;
  }
  return '';
}
// picks: [{ card: catalog id } | { loaner: loaner id }], 20 of them. Returns { deck, problems }.
export function buildDeck(campaign, chN, picks, owned, t) {
  const ch = E.chapterOf(campaign, chN), problems = [], deck = [];
  if (!Array.isArray(picks) || picks.length !== E.RULES.deckSize) return { deck: null, problems: [`A deck has ${E.RULES.deckSize} cards.`] };
  const used = new Map();
  for (const p of picks) {
    if (p && typeof p.loaner === 'string') {
      const l = LOANER_BY_ID.get(p.loaner);
      if (!l || l.side !== campaign.side) { problems.push('Unknown loaner.'); continue; }
      const c = { series: l.series, value: l.value, branches: l.branches, keyword: l.keyword || null, title: l.title, loaner: l.id };
      const why = cardProblem(campaign, ch, c); if (why) { problems.push(`${l.title}: ${why}`); continue; }
      deck.push(c); continue;
    }
    const id = p && p.card;
    const card = typeof id === 'string' ? findCard(id, t) : null;
    if (!card || !owned.has(id)) { problems.push('A card that is not in your dossier.'); continue; }
    used.set(id, (used.get(id) || 0) + 1);
    if (used.get(id) > 1) { problems.push(`${card.title}: one copy of each card in a deck.`); continue; }
    const c = playable(card), why = cardProblem(campaign, ch, c);
    if (why) { problems.push(`${card.title}: ${why}`); continue; }
    deck.push({ ...c, card: id });
  }
  return problems.length ? { deck: null, problems } : { deck, problems };
}

// ---------- seeds and tickets ----------
// Everyone's first run of a chapter on a given day uses the same seed, everyone's second run the second,
// and so on (Campaigns doc, Ranking). The seed comes from the signing key, so it can't be worked out
// before the day.
export async function runSeed(env, campaignId, chN, day, runNo) {
  return (await hmac(env.SIGNING_KEY, `campaign-seed:${campaignId}:${chN}:${day}:${runNo}`)).slice(0, 16);
}
export const ticketFor = (env, runId, playerId) => hmac(env.SIGNING_KEY, `campaign-run:${runId}:${playerId}`).then(sig => `${runId}.${sig}`);
export async function readTicket(env, ticket, playerId) {
  const [runId, sig] = String(ticket || '').split('.');
  if (!runId || !sig || !(await hmacVerify(env.SIGNING_KEY, `campaign-run:${runId}:${playerId}`, sig))) return null;
  return runId;
}
export function newRunId() { const b = new Uint8Array(9); crypto.getRandomValues(b); return [...b].map(x => x.toString(16).padStart(2, '0')).join(''); }

// ---------- the tables (created on first use; migrations/0005_campaigns.sql holds the same for the record) ----------
const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS campaign_runs (id TEXT PRIMARY KEY, player_id TEXT NOT NULL, campaign_id TEXT NOT NULL, chapter INTEGER NOT NULL, day TEXT NOT NULL, run_no INTEGER NOT NULL, deck TEXT NOT NULL, seed TEXT NOT NULL, started_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'play', choices TEXT, won INTEGER, resolve INTEGER, rounds INTEGER, waves INTEGER, destroyed REAL, score INTEGER, finished_at TEXT, UNIQUE (player_id, campaign_id, chapter, day, run_no))`,
  `CREATE INDEX IF NOT EXISTS campaign_runs_player ON campaign_runs(player_id, campaign_id)`,
  `CREATE TABLE IF NOT EXISTS campaign_progress (player_id TEXT NOT NULL, campaign_id TEXT NOT NULL, year TEXT NOT NULL, chapter INTEGER NOT NULL, won_at TEXT, best INTEGER, best_day TEXT, PRIMARY KEY (player_id, campaign_id, year, chapter))`,
  `CREATE TABLE IF NOT EXISTS campaign_day_best (player_id TEXT NOT NULL, campaign_id TEXT NOT NULL, chapter INTEGER NOT NULL, day TEXT NOT NULL, score INTEGER NOT NULL, PRIMARY KEY (player_id, campaign_id, chapter, day))`,
  // Histograms, no names: one row per score with how many players have it. kind 'day' (k = the day) or 'chapter' (k = the year).
  // Month end payouts (build session 5): one row per player and chapter, written once with the settled rank.
  `CREATE TABLE IF NOT EXISTS campaign_payouts (player_id TEXT NOT NULL, campaign_id TEXT NOT NULL, year TEXT NOT NULL, chapter INTEGER NOT NULL, top INTEGER NOT NULL, players INTEGER NOT NULL, band TEXT NOT NULL, intel INTEGER NOT NULL, paid_at TEXT NOT NULL, tok TEXT NOT NULL, seen INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (player_id, campaign_id, year, chapter))`,
  `CREATE TABLE IF NOT EXISTS campaign_ranks (campaign_id TEXT NOT NULL, chapter INTEGER NOT NULL, kind TEXT NOT NULL, k TEXT NOT NULL, score INTEGER NOT NULL, n INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (campaign_id, chapter, kind, k, score))`,
];
let ready = null;
export function ensureTables(db) {
  if (!ready) ready = db.batch(SCHEMA.map(s => db.prepare(s))).catch(err => { ready = null; throw err; });
  return ready;
}

// What the page sees about a chapter. Waves (the enemy and the debriefs) only once it is released.
export function publicChapter(slot, ch, t, progress) {
  const released = chapterReleased(slot, ch, t);
  const prev = ch.n === 1 ? null : progress.get(ch.n - 1);
  const unlocked = released && (ch.n === 1 || Boolean(prev && prev.won_at));
  const mine = progress.get(ch.n);
  const out = { n: ch.n, name: ch.name, opensAt: chapterOpensAt(slot, ch), released, unlocked, won: Boolean(mine && mine.won_at), best: mine ? mine.best : null };
  if (released) Object.assign(out, { branches: ch.branches, twist: ch.twist, intro: ch.intro, calm: ch.calm, benchmark: ch.benchmark, sweep: ch.sweep, waves: ch.waves });
  return out;
}
export async function progressOf(db, playerId, slot) {
  const rows = (await db.prepare('SELECT * FROM campaign_progress WHERE player_id = ? AND campaign_id = ? AND year = ?').bind(playerId, slot.campaign.id, slot.year).all()).results || [];
  return new Map(rows.map(r => [r.chapter, r]));
}
export async function runsToday(db, playerId, campaignId, chN, day) {
  const r = await db.prepare('SELECT COUNT(*) AS n FROM campaign_runs WHERE player_id = ? AND campaign_id = ? AND chapter = ? AND day = ?').bind(playerId, campaignId, chN, day).first();
  return r ? r.n : 0;
}
// Percentile: the share of players whose score is below this one, plus half of those tied.
export async function percentile(db, campaignId, chN, kind, k, score) {
  const r = await db.prepare('SELECT SUM(CASE WHEN score < ?5 THEN n ELSE 0 END) AS below, SUM(CASE WHEN score = ?5 THEN n ELSE 0 END) AS tied, SUM(n) AS total FROM campaign_ranks WHERE campaign_id = ?1 AND chapter = ?2 AND kind = ?3 AND k = ?4')
    .bind(campaignId, chN, kind, k, score).first();
  if (!r || !r.total) return null;
  // "Top 12%": the share of players at or above this score, ties counted halfway.
  return { top: Math.max(1, Math.round(100 - (100 * (r.below + r.tied / 2)) / r.total)), players: r.total };
}
// When a campaign's month ends (midnight Eastern on the 1st of the next month), its chapter ranks settle.
export function monthEndsAt(campaign, year) {
  const m = campaign.month, y = Number(year);
  const next = m === 12 ? `${y + 1}-01-01` : `${y}-${String(m + 1).padStart(2, '0')}-01`;
  return zonedTime(next, '00:00');
}
// Settled for real only when the month was a scheduled month for that campaign. Preview runs (any month,
// before launch) never pay out, except on a local copy with the test clock, so the settle can be tested.
function settles(env, campaignId, year, campaign) {
  if (env.ALLOW_FAKE_NOW === '1') return true;
  return schedule.months[`${year}-${String(campaign.month).padStart(2, '0')}`] === campaignId;
}
// Pay this player for every chapter whose month has ended and that isn't paid yet. Called when the home
// screen or Campaigns loads, so nothing has to run on a timer. Each payout is written once (the primary
// key), and the Intel moves only in the batch whose payout row went in. Returns the new payouts.
export async function settleFor(env, playerId, t) {
  const db = env.DB;
  const rows = (await db.prepare(`SELECT p.campaign_id, p.year, p.chapter, p.best FROM campaign_progress p WHERE p.player_id = ? AND p.best IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM campaign_payouts x WHERE x.player_id = p.player_id AND x.campaign_id = p.campaign_id AND x.year = p.year AND x.chapter = p.chapter)`).bind(playerId).all()).results || [];
  const paid = [];
  for (const r of rows) {
    const campaign = CAMPAIGNS.get(r.campaign_id);
    if (!campaign || !settles(env, r.campaign_id, r.year, campaign) || t < monthEndsAt(campaign, r.year)) continue;
    const pc = await percentile(db, r.campaign_id, r.chapter, 'chapter', r.year, r.best);
    if (!pc) continue;
    const band = bandOf(pc.top), intel = BAND_INTEL[band], at = t.toISOString();
    const tok = newRunId();
    const mine = `EXISTS (SELECT 1 FROM campaign_payouts WHERE player_id = ?1 AND campaign_id = ?2 AND year = ?3 AND chapter = ?4 AND tok = ?5)`;
    const res = await db.batch([
      db.prepare('INSERT INTO campaign_payouts (player_id, campaign_id, year, chapter, top, players, band, intel, paid_at, tok) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT DO NOTHING')
        .bind(playerId, r.campaign_id, r.year, r.chapter, pc.top, pc.players, band, intel, at, tok),
      db.prepare(`UPDATE players SET intel = intel + ?6 WHERE id = ?1 AND ${mine}`).bind(playerId, r.campaign_id, r.year, r.chapter, tok, intel),
      db.prepare(`INSERT INTO intel_log (player_id, at, delta, reason, slot_key) SELECT ?1, ?7, ?6, 'campaign', ?8 WHERE ${mine}`)
        .bind(playerId, r.campaign_id, r.year, r.chapter, tok, intel, at, `cmp:${r.campaign_id}:${r.year}:${r.chapter}`),
    ]);
    if (res[0].meta && res[0].meta.changes) paid.push({ campaign: r.campaign_id, title: campaign.title, year: r.year, chapter: r.chapter, name: (campaign.chapters.find(c => c.n === r.chapter) || {}).name, top: pc.top, players: pc.players, band, intel });
  }
  return paid;
}
// Settled results the player hasn't been shown yet; marks them shown.
export async function unseenPayouts(db, playerId) {
  const rows = (await db.prepare('SELECT * FROM campaign_payouts WHERE player_id = ? AND seen = 0').bind(playerId).all()).results || [];
  if (rows.length) await db.prepare('UPDATE campaign_payouts SET seen = 1 WHERE player_id = ? AND seen = 0').bind(playerId).run();
  return rows.map(r => { const c = CAMPAIGNS.get(r.campaign_id); return { campaign: r.campaign_id, title: c ? c.title : '', year: r.year, chapter: r.chapter, name: c ? (c.chapters.find(x => x.n === r.chapter) || {}).name : '', top: r.top, players: r.players, band: r.band, intel: r.intel }; });
}
export { gameDay, addDays };
