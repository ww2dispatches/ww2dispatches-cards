// GET /api/stats: the tester stats page (2 Nov 2026). Totals across every player, never anything about one
// player: pull rates against the designed odds, envelope shapes, and health checks that would show a bug
// (envelopes with the wrong card count, missing day cards, serial gaps, Intel that doesn't add up, unsigned
// or stuck pulls, cards the catalog doesn't know). Behind the tester gate like every game request.
import { json } from '../_lib/util.js';
import { now, findCard } from '../_lib/catalog.js';
import { FINISHES, LIVING_ONE_IN, FLASH_ONE_IN } from '../_lib/odds.js';
import { isMorning } from '../_lib/time.js';
import data from '../_data/catalog.json';

const FIN = ['copper', 'silver', 'gold', 'topsecret'];
const expected = v => { const t = FINISHES[v]; return { topsecret: t.topsecret / 1e4, gold: (t.gold - t.topsecret) / 1e4, silver: (t.silver - t.gold) / 1e4, copper: 1 - t.silver / 1e4 }; };
const kindOf = k => k.startsWith('d:') ? 'daily' : k.startsWith('p:') ? 'priority' : k.startsWith('c:') ? 'commemorative' : k === 's:starter' ? 'starter' : k.startsWith('q:') ? 'request' : k.startsWith('i:') ? 'intercept' : 'other';

export async function onRequestGet({ request, env }) {
  const t = now(env, request), db = env.DB;
  const [P, PL, O, S, L] = await db.batch([
    db.prepare('SELECT player_id, card_id, variant, finish, serial, slot_key, pulled_at, signature, turned, intel FROM pulls'),
    db.prepare('SELECT id, created_at, intel, streak, last_day_played FROM players'),
    db.prepare("SELECT player_id, slot_key, opened_at FROM opened WHERE slot_key NOT LIKE 'h:%'"),
    db.prepare('SELECT card_id, variant, last FROM serials'),
    db.prepare('SELECT player_id, SUM(delta) AS total FROM intel_log GROUP BY player_id'),
  ]);
  const pulls = P.results, players = PL.results, opened = O.results;
  const byId = new Map(data.cards.map(c => [c.id, c]));

  // ---- each pull's source: the guaranteed day card, an archive draw, or a pack/request/pick ----
  const groups = new Map(); // player|slot -> pulls
  for (const p of pulls) { const k = p.player_id + '|' + p.slot_key; if (!groups.has(k)) groups.set(k, []); groups.get(k).push(p); }
  const tally = () => ({ n: 0, copper: 0, silver: 0, gold: 0, topsecret: 0 });
  const rates = { dayCard: tally(), archiveStill: tally(), archiveLiving: tally(), starter: tally(), request: tally(), intercept: tally() };
  let archiveDraws = 0, archiveLiving = 0, archiveFlash = 0;
  const envShape = { daily: { envelopes: 0, wrongCount: 0, morningMissingDayCard: 0, withRepeat: 0 }, priority: { envelopes: 0, wrongCount: 0 }, commemorative: { envelopes: 0, wrongCount: 0 } };
  for (const [k, list] of groups) {
    const slot = k.slice(k.indexOf('|') + 1), kind = kindOf(slot);
    if (kind === 'starter') { list.forEach(p => { rates.starter.n++; rates.starter[p.finish]++; }); continue; }
    if (kind === 'request') { list.forEach(p => { rates.request.n++; rates.request[p.finish]++; }); continue; }
    if (kind === 'intercept') { list.forEach(p => { rates.intercept.n++; rates.intercept[p.finish]++; }); continue; }
    if (kind === 'other') continue;
    const e = envShape[kind]; e.envelopes++;
    let rest = list.slice();
    if (kind === 'daily') {
      const at = slot.slice(2), morning = isMorning(at);
      const day = data.cards.find(c => c.kind === 'dispatch' && c.postAt === at);
      if (list.length !== 3) e.wrongCount++;
      if (new Set(list.map(p => p.card_id)).size < list.length) e.withRepeat++;
      if (morning && day) {
        const i = rest.findIndex(p => p.card_id === day.id && p.variant === 'still');
        if (i < 0) e.morningMissingDayCard++;
        else { const d = rest.splice(i, 1)[0]; if (!day.flash) { rates.dayCard.n++; rates.dayCard[d.finish]++; } }
      }
    } else if (kind === 'priority') { if (list.length !== 3) e.wrongCount++; }
    else if (kind === 'commemorative') { const fl = rest.filter(p => (byId.get(p.card_id) || {}).flash); rest = rest.filter(p => !(byId.get(p.card_id) || {}).flash); if (rest.length !== 3) e.wrongCount++; }
    for (const p of rest) {
      archiveDraws++;
      const c = byId.get(p.card_id) || {};
      if (c.flash) { archiveFlash++; continue; }
      if (p.variant === 'living') { archiveLiving++; rates.archiveLiving.n++; rates.archiveLiving[p.finish]++; }
      else { rates.archiveStill.n++; rates.archiveStill[p.finish]++; }
    }
  }

  // ---- health checks ----
  const tsBy = new Map();
  for (const p of pulls) if (p.finish === 'topsecret' && p.serial) { const k = p.card_id + '|' + p.variant; if (!tsBy.has(k)) tsBy.set(k, []); tsBy.get(k).push(p.serial); }
  let serialGaps = 0, serialDupes = 0, serialPastCounter = 0;
  const lastBy = new Map(S.results.map(r => [r.card_id + '|' + r.variant, r.last]));
  for (const [k, list] of tsBy) {
    const set = new Set(list); if (set.size < list.length) serialDupes++;
    const max = Math.max(...list); if (set.size < max) serialGaps++;
    if (max > (lastBy.get(k) || 0)) serialPastCounter++;
  }
  const dayAgo = new Date(t.getTime() - 2 * 86400000).toISOString();
  const logBy = new Map(L.results.map(r => [r.player_id, r.total || 0]));
  const openedSet = new Set(opened.map(o => o.player_id + '|' + o.slot_key));
  const pulledSet = new Set(groups.keys());
  const envKinds = new Set(['daily', 'priority', 'commemorative', 'request', 'intercept']);
  const health = {
    unsignedPulls: pulls.filter(p => !p.signature).length,
    stuckWaiting: pulls.filter(p => !p.turned && p.pulled_at < dayAgo).length,
    unknownCards: pulls.filter(p => !byId.has(p.card_id)).length,
    cardsBeforePost: pulls.filter(p => byId.has(p.card_id) && !findCard(p.card_id, new Date(p.pulled_at))).length,
    topSecretConverted: pulls.filter(p => p.finish === 'topsecret' && p.intel > 0).length,
    serialGaps, serialDupes, serialPastCounter,
    intelMismatch: players.filter(pl => (pl.intel || 0) !== (logBy.get(pl.id) || 0)).length,
    openedWithoutPulls: opened.filter(o => envKinds.has(kindOf(o.slot_key)) && !pulledSet.has(o.player_id + '|' + o.slot_key)).length,
    pullsWithoutOpened: [...pulledSet].filter(k => envKinds.has(kindOf(k.slice(k.indexOf('|') + 1))) && !openedSet.has(k)).length,
  };

  // ---- activity ----
  const days = [];
  for (let i = 13; i >= 0; i--) {
    const d = new Date(t.getTime() - i * 86400000).toISOString().slice(0, 10);
    days.push({ day: d, opens: opened.filter(o => o.opened_at.slice(0, 10) === d && envKinds.has(kindOf(o.slot_key))).length, players: new Set(opened.filter(o => o.opened_at.slice(0, 10) === d).map(o => o.player_id)).size });
  }
  const perPlayer = players.map(pl => pulls.filter(p => p.player_id === pl.id).length).sort((a, b) => a - b);
  const since = h => new Set(opened.filter(o => o.opened_at >= new Date(t.getTime() - h * 3600000).toISOString()).map(o => o.player_id)).size;
  const cardCounts = new Map();
  for (const p of pulls) cardCounts.set(p.card_id, (cardCounts.get(p.card_id) || 0) + 1);
  const posted = data.cards.filter(c => findCard(c.id, t));
  const most = [...cardCounts].sort((a, b) => b[1] - a[1]).slice(0, 8).map(([id, n]) => ({ id, short: (byId.get(id) || {}).short || id, n }));
  const never = posted.filter(c => !cardCounts.has(c.id)).map(c => c.short || c.id);

  return json({
    at: t.toISOString(),
    players: { total: players.length, active24h: since(24), active7d: since(168), pullsMin: perPlayer[0] || 0, pullsMedian: perPlayer[Math.floor(perPlayer.length / 2)] || 0, pullsMax: perPlayer[perPlayer.length - 1] || 0 },
    totals: { pulls: pulls.length, envelopes: envShape.daily.envelopes + envShape.priority.envelopes + envShape.commemorative.envelopes, archiveDraws, postedCards: posted.length },
    rates, expected: { still: expected('still'), living: expected('living') },
    living: { draws: archiveDraws, living: archiveLiving, expected: 1 / LIVING_ONE_IN },
    flash: { draws: archiveDraws, flash: archiveFlash, expected: 1 / FLASH_ONE_IN },
    envelopes: envShape, health, days, most, never,
  });
}
