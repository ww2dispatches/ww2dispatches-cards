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
export const CHOICES_MAX = 4000;        // a finished run is a few hundred choices; anything far past that is refused

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
function playable(card) {
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
  if (!(c.value >= 1 && c.value <= 7)) return 'This card has no number yet.';
  if (c.date) {
    if (c.date > '1945-09-02') return 'Postwar cards are for collecting only.';
    if (Number(c.date.slice(0, 4)) > campaign.year) return `Only cards from ${campaign.year} or earlier fit this campaign.`;
  }
  const axis = campaign.side === 'axis';
  if (c.lens && c.lens !== 'civilian_neutral' && axis !== c.lens.startsWith('axis_')) return 'This card is from the other side.';
  if (!E.fitsChapter(ch, c)) return `This is ${ch.branches.join(' and ')} only: no branch of this card fights here.`;
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
export { gameDay, addDays };
