// GET /api/stats: the Declass admin console (2 Nov 2026), for Brian only (file number on the admin list in functions/_lib/admins.js).
// Everyone else gets "not found". Built from what the game already stores; nothing extra is logged.
//   /api/stats            the whole picture: health, engagement, new players, economy, collecting, card rates,
//                         Intercept, catalog checks, and every player as a row (by file number)
//   /api/stats?player=X   one player in detail, by file number
import { json, fail } from '../_lib/util.js';
import { now, findCard, filmReleased } from '../_lib/catalog.js';
import { signedInPlayer } from '../_lib/player.js';
import { playerFileNumber } from '../_lib/fileno.js';
import { isAdmin } from '../_lib/admins.js';
import { FINISHES, LIVING_ONE_IN, FLASH_ONE_IN } from '../_lib/odds.js';
import { isMorning, gameDay, addDays } from '../_lib/time.js';
import { filledSlots, rankInfo } from '../_lib/rank.js';
import { ensureTally } from '../_lib/tally.js';
import data from '../_data/catalog.json';

// The admin list (Brian, plus the ADMIN_FILES variable) lives in functions/_lib/admins.js.

const DAY = 86400000;
const expected = v => { const t = FINISHES[v]; return { topsecret: t.topsecret / 1e4, gold: (t.gold - t.topsecret) / 1e4, silver: (t.silver - t.gold) / 1e4, copper: 1 - t.silver / 1e4 }; };
const kindOf = k => k.startsWith('d:') ? 'daily' : k.startsWith('p:') ? 'priority' : k.startsWith('c:') ? 'commemorative' : k === 's:starter' ? 'starter' : k.startsWith('q:') ? 'request' : k.startsWith('i:') ? 'intercept' : 'other';
const ENV_KINDS = new Set(['daily', 'priority', 'commemorative', 'request', 'intercept']);
const etHour = iso => Number(new Date(iso).toLocaleString('en-US', { timeZone: 'America/New_York', hour: 'numeric', hourCycle: 'h23' }));
const etMonth = iso => new Date(iso).toLocaleDateString('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit' }).slice(0, 7);
const median = a => { if (!a.length) return 0; const s = a.slice().sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };
const tally = () => ({ n: 0, copper: 0, silver: 0, gold: 0, topsecret: 0 });

export async function onRequestGet({ request, env }) {
  const player = await signedInPlayer(env, request);
  if (!isAdmin(env, player)) return fail(404, 'not found');
  const t = now(env, request), db = env.DB, today = gameDay(t);
  const [P, PL, O, S, L] = await db.batch([
    db.prepare('SELECT id, player_id, card_id, variant, finish, serial, slot_key, pulled_at, signature, turned, intel FROM pulls'),
    db.prepare('SELECT * FROM players'),
    db.prepare('SELECT player_id, slot_key, opened_at FROM opened'),
    db.prepare('SELECT card_id, variant, last FROM serials'),
    db.prepare('SELECT player_id, at, delta, reason, slot_key, card_id, variant, finish FROM intel_log'),
  ]);
  let IC = [];
  try { IC = (await db.prepare('SELECT player_id, day, status, score, mistakes, intel, fin, claimed FROM intercept').all()).results; } catch (e) {}
  const pulls = P.results, players = PL.results, openedAll = O.results, ilog = L.results;
  const honors = openedAll.filter(o => o.slot_key.startsWith('h:'));
  const opened = openedAll.filter(o => !o.slot_key.startsWith('h:'));
  const byId = new Map(data.cards.map(c => [c.id, c]));
  const posted = data.cards.filter(c => findCard(c.id, t));
  const postedDispatch = posted.filter(c => c.kind === 'dispatch');
  const fileOf = new Map(players.map(p => [p.id, playerFileNumber(p.id)]));

  // per player indexes
  const pullsBy = new Map(), openedBy = new Map(), logBy = new Map(), icBy = new Map();
  const push = (m, k, v) => { if (!m.has(k)) m.set(k, []); m.get(k).push(v); };
  pulls.forEach(p => push(pullsBy, p.player_id, p));
  opened.forEach(o => push(openedBy, o.player_id, o));
  ilog.forEach(r => push(logBy, r.player_id, r));
  IC.forEach(r => push(icBy, r.player_id, r));

  // days each player played (Eastern game days with an envelope opened)
  const playDays = new Map();
  for (const o of opened) if (ENV_KINDS.has(kindOf(o.slot_key))) { if (!playDays.has(o.player_id)) playDays.set(o.player_id, new Set()); playDays.get(o.player_id).add(gameDay(new Date(o.opened_at))); }

  // collections for pins: series, years, theaters, nations
  const colls = [];
  [...new Set(posted.map(c => c.series))].forEach(v => colls.push(c => c.series === v));
  [...new Set(postedDispatch.map(c => c.era))].forEach(v => colls.push(c => c.kind === 'dispatch' && c.era === v));
  [...new Set(posted.flatMap(c => c.theater || []))].forEach(v => colls.push(c => (c.theater || []).includes(v)));
  ['US', 'Britain', 'Soviet Union', 'Germany', 'Japan'].forEach(v => colls.push(c => (c.nations || []).includes(v)));
  const months = new Map();
  postedDispatch.forEach(c => push(months, etMonth(c.postAt), c.id));
  const nowYm = etMonth(t.toISOString());

  function summarize(pl) {
    const mine = pullsBy.get(pl.id) || [], held = new Set(mine.map(p => p.card_id)), days = playDays.get(pl.id) || new Set();
    const envs = (openedBy.get(pl.id) || []).filter(o => ENV_KINDS.has(kindOf(o.slot_key)));
    const last = envs.reduce((m, o) => o.opened_at > m ? o.opened_at : m, '');
    let stamps = 0; months.forEach((ids, ym) => { if (ym < nowYm && ids.every(id => held.has(id))) stamps++; });
    let pins = 0; colls.forEach(fn => { const n = posted.filter(fn).filter(c => held.has(c.id)).length; pins += [25, 50, 100].filter(k => n >= k).length; });
    const logSum = (logBy.get(pl.id) || []).reduce((s, r) => s + r.delta, 0);
    return {
      file: fileOf.get(pl.id), joined: pl.created_at, lastActive: last || null, daysPlayed: days.size, envelopes: envs.length, pulls: mine.length,
      streak: pl.streak, intel: pl.intel || 0, intelLogOk: (pl.intel || 0) === logSum, rank: rankInfo(filledSlots(mine), pl.rank_seen || 0).title,
      held: held.size, completion: posted.length ? held.size / posted.length : 0, goldPlus: mine.filter(p => p.finish === 'gold' || p.finish === 'topsecret').length,
      stamps, pins, starter: Boolean(pl.starter_done), waiting: mine.filter(p => !p.turned).length, priority: pl.priority_waiting,
      requests: new Set(mine.filter(p => kindOf(p.slot_key) === 'request').map(p => p.slot_key)).size, intercepts: (icBy.get(pl.id) || []).length,
    };
  }

  // ---------- one player ----------
  const want = new URL(request.url).searchParams.get('player');
  if (want) {
    const pl = players.find(p => fileOf.get(p.id) === want.toUpperCase());
    if (!pl) return fail(404, 'no such player');
    const mine = (pullsBy.get(pl.id) || []).slice().sort((a, b) => b.pulled_at.localeCompare(a.pulled_at));
    const envMap = new Map(); mine.forEach(p => push(envMap, p.slot_key, p));
    const envList = [...envMap].map(([slot, list]) => ({ slot, kind: kindOf(slot), at: list[0].pulled_at, cards: list.map(p => ({ short: (byId.get(p.card_id) || {}).short || p.card_id, finish: p.finish, living: p.variant === 'living', serial: p.serial, intel: p.intel, turned: Boolean(p.turned) })) })).sort((a, b) => b.at.localeCompare(a.at)).slice(0, 40);
    const missing = posted.filter(c => !mine.some(p => p.card_id === c.id)).map(c => c.short || c.id);
    return json({
      at: t.toISOString(), summary: summarize(pl), envelopes: envList, missing,
      intelLog: (logBy.get(pl.id) || []).slice().sort((a, b) => b.at.localeCompare(a.at)).slice(0, 30).map(r => ({ at: r.at, delta: r.delta, reason: r.reason, card: r.card_id ? (byId.get(r.card_id) || {}).short || r.card_id : null, finish: r.finish })),
      intercept: (icBy.get(pl.id) || []).slice().sort((a, b) => b.day.localeCompare(a.day)).slice(0, 14),
      honorsSeen: honors.filter(h => h.player_id === pl.id).map(h => h.slot_key.slice(2)),
      playDays: [...(playDays.get(pl.id) || [])].sort(),
    });
  }

  // ---------- card rates: day card, archive draws, packs ----------
  const groups = new Map();
  pulls.forEach(p => push(groups, p.player_id + '|' + p.slot_key, p));
  const rates = { dayCard: tally(), archiveStill: tally(), archiveLiving: tally(), starter: tally(), request: tally(), intercept: tally() };
  let archiveDraws = 0, archiveLiving = 0, archiveFlash = 0;
  const envShape = { daily: { envelopes: 0, wrongCount: 0, morningMissingDayCard: 0, withRepeat: 0 }, priority: { envelopes: 0, wrongCount: 0 }, commemorative: { envelopes: 0, wrongCount: 0 } };
  for (const [k, list] of groups) {
    const slot = k.slice(k.indexOf('|') + 1), kind = kindOf(slot);
    if (kind === 'starter' || kind === 'request' || kind === 'intercept') { list.forEach(p => { rates[kind].n++; rates[kind][p.finish]++; }); continue; }
    if (kind === 'other') continue;
    const e = envShape[kind]; e.envelopes++;
    let rest = list.slice();
    if (kind === 'daily') {
      const at = slot.slice(2), day = data.cards.find(c => c.kind === 'dispatch' && c.postAt === at);
      if (list.length !== 3) e.wrongCount++;
      if (new Set(list.map(p => p.card_id)).size < list.length) e.withRepeat++;
      if (isMorning(at) && day) {
        const i = rest.findIndex(p => p.card_id === day.id && p.variant === 'still');
        if (i < 0) e.morningMissingDayCard++;
        else { const d = rest.splice(i, 1)[0]; if (!day.flash) { rates.dayCard.n++; rates.dayCard[d.finish]++; } }
      }
    } else if (kind === 'priority') { if (list.length !== 3) e.wrongCount++; }
    else { rest = rest.filter(p => !(byId.get(p.card_id) || {}).flash); if (rest.length !== 3) e.wrongCount++; }
    for (const p of rest) {
      archiveDraws++;
      if ((byId.get(p.card_id) || {}).flash) { archiveFlash++; continue; }
      if (p.variant === 'living') { archiveLiving++; rates.archiveLiving.n++; rates.archiveLiving[p.finish]++; }
      else { rates.archiveStill.n++; rates.archiveStill[p.finish]++; }
    }
  }

  // ---------- health ----------
  const tsBy = new Map();
  pulls.forEach(p => { if (p.finish === 'topsecret' && p.serial) push(tsBy, p.card_id + '|' + p.variant, p.serial); });
  const lastBy = new Map(S.results.map(r => [r.card_id + '|' + r.variant, r.last]));
  let serialGaps = 0, serialDupes = 0, serialPastCounter = 0;
  for (const [k, list] of tsBy) { const set = new Set(list), max = Math.max(...list); if (set.size < list.length) serialDupes++; if (set.size < max) serialGaps++; if (max > (lastBy.get(k) || 0)) serialPastCounter++; }
  const twoDaysAgo = new Date(t.getTime() - 2 * DAY).toISOString();
  const openedSet = new Set(opened.map(o => o.player_id + '|' + o.slot_key)), pulledSet = new Set(groups.keys());
  const summaries = players.map(summarize);
  const health = {
    unsignedPulls: pulls.filter(p => !p.signature).length,
    stuckWaiting: pulls.filter(p => !p.turned && p.pulled_at < twoDaysAgo).length,
    unknownCards: pulls.filter(p => !byId.has(p.card_id)).length,
    cardsBeforePost: pulls.filter(p => byId.has(p.card_id) && !findCard(p.card_id, new Date(p.pulled_at))).length,
    topSecretConverted: pulls.filter(p => p.finish === 'topsecret' && p.intel > 0).length,
    serialGaps, serialDupes, serialPastCounter,
    intelMismatch: summaries.filter(s => !s.intelLogOk).map(s => s.file),
    openedWithoutPulls: opened.filter(o => ENV_KINDS.has(kindOf(o.slot_key)) && !pulledSet.has(o.player_id + '|' + o.slot_key)).length,
    pullsWithoutOpened: [...pulledSet].filter(k => ENV_KINDS.has(kindOf(k.slice(k.indexOf('|') + 1))) && !openedSet.has(k)).length,
  };

  // ---------- engagement ----------
  const activeOn = d => [...playDays.values()].filter(s => s.has(d)).length;
  const days14 = []; for (let i = 13; i >= 0; i--) { const d = addDays(today, -i); days14.push({ day: d, players: activeOn(d), opens: opened.filter(o => ENV_KINDS.has(kindOf(o.slot_key)) && gameDay(new Date(o.opened_at)) === d).length, intelEarned: ilog.filter(r => r.delta > 0 && gameDay(new Date(r.at)) === d).reduce((s, r) => s + r.delta, 0), intelSpent: -ilog.filter(r => r.delta < 0 && gameDay(new Date(r.at)) === d).reduce((s, r) => s + r.delta, 0) }); }
  const inLast = n => [...playDays.values()].filter(s => [...s].some(d => d > addDays(today, -n))).length;
  // retention: of players whose first play day is far enough back, how many played the next day, and on day 7 (days 6 to 8)
  let r1 = [0, 0], r7 = [0, 0];
  for (const s of playDays.values()) {
    const first = [...s].sort()[0];
    if (first <= addDays(today, -1)) { r1[1]++; if (s.has(addDays(first, 1))) r1[0]++; }
    if (first <= addDays(today, -8)) { r7[1]++; if ([6, 7, 8].some(k => s.has(addDays(first, k)))) r7[0]++; }
  }
  // daily envelopes: how fast they get opened, and how many on Last Call (a later game day than the drop)
  const delays = [], hours = new Array(24).fill(0); let lastCall = 0, dailyOpens = 0;
  for (const o of opened) {
    if (!o.slot_key.startsWith('d:')) continue;
    dailyOpens++;
    const drop = o.slot_key.slice(2), mins = (Date.parse(o.opened_at) - Date.parse(drop)) / 60000;
    if (mins >= 0) delays.push(mins);
    if (gameDay(new Date(o.opened_at)) > gameDay(new Date(drop))) lastCall++;
    hours[etHour(o.opened_at)]++;
  }
  // envelopes missed: daily envelope times between a player's first play day and yesterday that they never opened
  const slots = [...new Set(data.cards.filter(c => c.kind === 'dispatch').map(c => c.postAt))].filter(s => s <= new Date(t.getTime() - DAY).toISOString());
  let offered = 0, taken = 0;
  for (const pl of players) {
    const s = playDays.get(pl.id); if (!s) continue;
    const first = [...s].sort()[0], mineSet = new Set((openedBy.get(pl.id) || []).map(o => o.slot_key));
    slots.filter(x => gameDay(new Date(x)) >= first).forEach(x => { offered++; if (mineSet.has('d:' + x)) taken++; });
  }
  const streaks = {}; players.forEach(p => { const b = p.streak === 0 ? '0' : p.streak < 3 ? '1 to 2' : p.streak < 7 ? '3 to 6' : p.streak < 14 ? '7 to 13' : p.streak < 30 ? '14 to 29' : '30+'; streaks[b] = (streaks[b] || 0) + 1; });

  // ---------- new players: account to habit ----------
  const funnel = { accounts: players.length, starterDone: players.filter(p => p.starter_done).length, firstDaily: players.filter(p => (openedBy.get(p.id) || []).some(o => o.slot_key.startsWith('d:'))).length, played3Days: [...playDays.values()].filter(s => s.size >= 3).length, played7Days: [...playDays.values()].filter(s => s.size >= 7).length };

  // ---------- economy ----------
  const by = {}; ilog.forEach(r => { by[r.reason] = by[r.reason] || { n: 0, total: 0 }; by[r.reason].n++; by[r.reason].total += r.delta; });
  const weekAgo = new Date(t.getTime() - 7 * DAY).toISOString(), active7 = new Set(opened.filter(o => o.opened_at >= weekAgo).map(o => o.player_id));
  const earned7 = ilog.filter(r => r.delta > 0 && r.at >= weekAgo).reduce((s, r) => s + r.delta, 0);
  const reqs = tally(); pulls.filter(p => kindOf(p.slot_key) === 'request').forEach(p => { reqs.n++; reqs[p.finish]++; });
  const balances = players.map(p => p.intel || 0);

  // ---------- collecting ----------
  const ranks = {}; summaries.forEach(s => { ranks[s.rank] = (ranks[s.rank] || 0) + 1; });
  const finishesOut = tally(); pulls.forEach(p => { finishesOut.n++; finishesOut[p.finish]++; });
  const tsPerCard = [...tsBy].map(([k, list]) => ({ card: (byId.get(k.split('|')[0]) || {}).short || k, living: k.endsWith('living'), issued: list.length })).sort((a, b) => b.issued - a.issued);
  const cardCounts = new Map(); pulls.forEach(p => cardCounts.set(p.card_id, (cardCounts.get(p.card_id) || 0) + 1));
  const owners = new Map(); pulls.forEach(p => { if (!owners.has(p.card_id)) owners.set(p.card_id, new Set()); owners.get(p.card_id).add(p.player_id); });
  const cardTable = posted.map(c => ({ short: c.short || c.id, kind: c.kind, flash: Boolean(c.flash), postAt: c.kind === 'namethis' ? c.answerAt : c.postAt, pulls: cardCounts.get(c.id) || 0, owners: (owners.get(c.id) || new Set()).size })).sort((a, b) => b.pulls - a.pulls);

  // ---------- Intercept ----------
  const icDays = {}; IC.forEach(r => { icDays[r.day] = icDays[r.day] || { plays: 0, solved: 0, failed: 0, perfect: 0, scores: [], mistakes: [] }; const d = icDays[r.day]; d.plays++; if (r.status === 'solved') d.solved++; if (r.status === 'failed') d.failed++; if (r.score === 100) d.perfect++; if (r.score != null) d.scores.push(r.score); d.mistakes.push(r.mistakes); });
  const intercept = { plays: IC.length, solved: IC.filter(r => r.status === 'solved').length, failed: IC.filter(r => r.status === 'failed').length, perfect: IC.filter(r => r.score === 100).length, avgScore: IC.filter(r => r.score != null).length ? Math.round(IC.filter(r => r.score != null).reduce((s, r) => s + r.score, 0) / IC.filter(r => r.score != null).length) : null, claimed: IC.filter(r => r.claimed).length,
    days: Object.entries(icDays).sort((a, b) => b[0].localeCompare(a[0])).slice(0, 14).map(([day, d]) => ({ day, plays: d.plays, solved: d.solved, failed: d.failed, perfect: d.perfect, avgScore: d.scores.length ? Math.round(d.scores.reduce((s, x) => s + x, 0) / d.scores.length) : null, avgMistakes: d.mistakes.length ? +(d.mistakes.reduce((s, x) => s + x, 0) / d.mistakes.length).toFixed(1) : null })) };

  // ---------- growth: new players, site visits, sources, game actions (tallies start 2 Nov 2026) ----------
  let T = [];
  try { await ensureTally(db); T = (await db.prepare('SELECT day, metric, k, n FROM tally WHERE day >= ?').bind(addDays(today, -60)).all()).results; } catch (e) {}
  const sumT = (m, from, to, k) => T.filter(r => r.metric === m && r.day >= from && r.day <= to && (k === undefined || r.k === k)).reduce((s, r) => s + r.n, 0);
  const byK = (m, from, to) => { const o = {}; T.filter(r => r.metric === m && r.day >= from && r.day <= to).forEach(r => { o[r.k] = (o[r.k] || 0) + r.n; }); return o; };
  const joinDay = new Map(players.map(p => [p.id, gameDay(new Date(p.created_at))]));
  const signupsIn = (a, b) => [...joinDay.values()].filter(d => d >= a && d <= b).length;
  const opensIn = (a, b) => opened.filter(o => ENV_KINDS.has(kindOf(o.slot_key))).filter(o => { const d = gameDay(new Date(o.opened_at)); return d >= a && d <= b; }).length;
  const activeIn = (a, b) => [...playDays.values()].filter(s => [...s].some(d => d >= a && d <= b)).length;
  const playDaySum = (a, b) => [...playDays.values()].reduce((n, s) => n + [...s].filter(d => d >= a && d <= b).length, 0);
  const icIn = (a, b) => IC.filter(r => r.day >= a && r.day <= b).length;
  const period = (a, b) => ({
    visitors: sumT('visitors', a, b), views: sumT('view', a, b), newVisitors: sumT('new', a, b), declassVisitors: sumT('visitor', a, b, 'declass'),
    signups: signupsIn(a, b), activePlayers: activeIn(a, b), playerDays: playDaySum(a, b),
    envelopes: opensIn(a, b), intercepts: icIn(a, b), actions: sumT('ev', a, b),
    engagements: opensIn(a, b) + icIn(a, b) + sumT('ev', a, b), guestStarters: sumT('ev', a, b, 'guest_starter'),
  });
  const firstTally = T.reduce((m, r) => !m || r.day < m ? r.day : m, null);
  const firstJoin = [...joinDay.values()].sort()[0] || today;
  const days30 = [];
  for (let i = 29; i >= 0; i--) { const d = addDays(today, -i); days30.push({ day: d, views: sumT('view', d, d), visitors: sumT('visitors', d, d), newVisitors: sumT('new', d, d), declass: sumT('visitor', d, d, 'declass'), signups: signupsIn(d, d), total: signupsIn('0000', d), active: activeOn(d), engagements: opensIn(d, d) + icIn(d, d) + sumT('ev', d, d) }); }
  const growth = {
    since: firstTally, firstJoin,
    week: period(addDays(today, -6), today), lastWeek: period(addDays(today, -13), addDays(today, -7)), month: period(addDays(today, -29), today),
    days30,
    pages: { views: byK('view', addDays(today, -29), today), visitors: byK('visitor', addDays(today, -29), today) },
    sources: byK('source', addDays(today, -29), today), sourcesWeek: byK('source', addDays(today, -6), today),
    devices: byK('device', addDays(today, -29), today),
    actions: byK('ev', addDays(today, -29), today), actionsWeek: byK('ev', addDays(today, -6), today),
    signupSources: byK('signup', '0000', today),
    newest: players.slice().sort((a, b) => b.created_at.localeCompare(a.created_at)).slice(0, 10).map(p => ({ file: fileOf.get(p.id), joined: p.created_at, daysPlayed: (playDays.get(p.id) || new Set()).size, starter: Boolean(p.starter_done) })),
  };

  // ---------- catalog checks ----------
  const iso = t.toISOString(), week = new Date(t.getTime() + 7 * DAY).toISOString();
  const catalog = {
    posted: posted.length, dispatchPosted: postedDispatch.length,
    comingWeek: data.cards.filter(c => c.kind === 'dispatch' && c.postAt > iso && c.postAt <= week).length,
    lastPost: postedDispatch.reduce((m, c) => c.postAt > m ? c.postAt : m, ''),
    nextPost: data.cards.filter(c => c.kind === 'dispatch' && c.postAt > iso).reduce((m, c) => !m || c.postAt < m ? c.postAt : m, null),
    livingPosted: postedDispatch.filter(c => filmReleased(c, t)).length,
    noFile: postedDispatch.filter(c => !c.dfile).map(c => c.short || c.id),
    fileNoPhoto: postedDispatch.filter(c => c.dfile && !c.dfile.photo).length,
    nameThisWaiting: data.cards.filter(c => c.kind === 'namethis' && !c.answerAt).map(c => c.short || c.id),
    flashPosted: posted.filter(c => c.flash).length,
  };

  return json({
    at: t.toISOString(), today,
    totals: { players: players.length, pulls: pulls.length, envelopes: envShape.daily.envelopes + envShape.priority.envelopes + envShape.commemorative.envelopes, posted: posted.length },
    health,
    engagement: { active1: activeOn(today), active7: inLast(7), active30: inLast(30), retentionDay1: r1, retentionDay7: r7, days14, dailyOpens, lastCall, medianOpenMinutes: Math.round(median(delays)), hoursET: hours, missedRate: offered ? 1 - taken / offered : null, offered, taken, streaks },
    funnel,
    economy: { byReason: by, earned7, active7: active7.size, perActiveWeek: active7.size ? Math.round(earned7 / active7.size) : 0, design: 117, balances: { median: median(balances), max: Math.max(0, ...balances), over500: balances.filter(b => b > 500).length }, requests: reqs },
    collecting: { ranks, finishesOut, tsPerCard: tsPerCard.slice(0, 12), stampsEarned: summaries.reduce((s, x) => s + x.stamps, 0), pinsEarned: summaries.reduce((s, x) => s + x.pins, 0), goldPlusHolders: summaries.filter(s => s.goldPlus > 0).length, avgCompletion: summaries.length ? summaries.reduce((s, x) => s + x.completion, 0) / summaries.length : 0 },
    rates, expected: { still: expected('still'), living: expected('living') },
    living: { draws: archiveDraws, living: archiveLiving, expected: 1 / LIVING_ONE_IN },
    flash: { draws: archiveDraws, flash: archiveFlash, expected: 1 / FLASH_ONE_IN },
    envelopes: envShape, cards: cardTable, intercept, catalog, growth,
    players: summaries.sort((a, b) => (b.lastActive || '').localeCompare(a.lastActive || '')),
  });
}
