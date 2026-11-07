// Campaigns · a Declass card battle (build session 3, 6 Nov 2026): the door on the home screen, the month
// and chapter screens with release dates, the deck builder (suggested deck, the plain words deck check,
// greyed out cards with a reason), the opening hand and mulligan, and the calm opening on the plotting
// table. The raid and your attacks on the battlefield are build session 4.
//
// The rules are not here: every rule lives in engine.js, the same file the server uses to replay each
// finished run before it is saved or ranked. This page only shows the state and records the choices.
import * as E from './engine.js';

const D = () => window.Declass;
const $ = id => document.getElementById(id);
const esc = t => String(t == null ? '' : t).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const LIVE = false; // the same switch as CAMPAIGNS_LIVE on the server; until launch only a preview tester gets in
const RUN_STORE = 'declass_cmp_run';
const deckStore = (cid, n) => `declass_cmp_deck:${cid}:${n}`;

let DATA = null;        // GET /api/campaign
let loading = null;
let CH = null;          // the chapter on screen
let PICKS = [];         // the deck being built: [{card} | {loaner}]
let RUN = null;         // the run in progress: {campaignId, chapter, ticket, seed, deck, choices, runNo, day}
let ST = null;          // the engine state, rebuilt from RUN's choices
let LIFT = null;        // the hand card lifted for a closer look (its place in the deck)
let busy = false;

// ---------- the look: series, icons, the value seal ----------
const SER = {
  blue: { name: 'Blueprint', role: 'Machine', col: '#3D5884' },
  battle: { name: 'Battle Lines', role: 'Operation', col: '#B04A3E' },
  home: { name: 'Home Front', role: 'Rally', col: '#5E6B3A' },
  state: { name: 'Statecraft', role: 'Statecraft', col: '#B8862B' },
};
const KW = {
  lend: { name: 'Lend Lease', rule: `Put a machine of ${E.REACH.lend} or less from your deck onto your line. It sets up like any new machine.` },
  backchannel: { name: 'Back Channel', rule: `Draw ${E.BACK_CHANNEL_DRAW} cards.` },
  ultimatum: { name: 'Ultimatum', rule: `Played during the raid: put off one attack of ${E.REACH.ultimatum} or less. It comes back next round, 1 bigger.` },
  evac: { name: 'Evacuation', rule: `Bring a knocked out machine of ${E.REACH.evac} or less back to your hand.` },
};
const BRANCH = { air: 'air', sea: 'sea', land: 'land' };
// Icons on a 24 unit grid, drawn as single bold shapes so they hold at hand size (Card Design doc).
const ICON = {
  shield: '<path d="M12 2.2l8 3v6.2c0 5-3.4 8.9-8 10.6-4.6-1.7-8-5.6-8-10.6V5.2z"/>',
  swords: '<g fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M5 4.5l12.5 12.5M19 4.5L6.5 17"/><path d="M14.5 19.5l5-5M9.5 19.5l-5-5"/></g>',
  heart: '<path d="M12 21.2s-8.6-5.3-8.6-11.4A4.7 4.7 0 0 1 12 7a4.7 4.7 0 0 1 8.6 2.8c0 6.1-8.6 11.4-8.6 11.4z"/>',
  rings: '<g fill="none" stroke="currentColor" stroke-width="2.6"><circle cx="8.6" cy="12" r="5.4"/><circle cx="15.4" cy="12" r="5.4"/></g>',
  air: '<path d="M12 1.8c.9 0 1.4 1 1.4 2.2v5.2l8 4.6v2.3l-8-2.3v4.4l2.4 1.8V22L12 21l-3.8 1v-1.9l2.4-1.8v-4.4l-8 2.3v-2.3l8-4.6V4c0-1.2.5-2.2 1.4-2.2z"/>',
  land: '<path d="M3 14.5h18l-1.6 4.5H4.6zM6 10.5h9l1.5 4H4.5zM13.5 11.6l8-2.2.5 1.6-8 2.2z"/>',
  sea: '<g fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="12" cy="5" r="2.2"/><path d="M12 7.2V21M7.5 10.5h9M4.5 14c0 4 3.4 7 7.5 7s7.5-3 7.5-7"/></g>',
  lend: '<path d="M12 2.5c-5.3 0-9.5 3.1-9.5 6.6h19c0-3.5-4.2-6.6-9.5-6.6z"/><path d="M3 9.6l6.6 6.8M21 9.6l-6.6 6.8M12 9.6v6.8" fill="none" stroke="currentColor" stroke-width="1.5"/><rect x="8" y="15.6" width="8" height="6.4" rx=".6"/>',
  backchannel: '<path d="M6.2 3.2l3.2-.6 1.7 4.6-2.3 1.7a12 12 0 0 0 6.3 6.3l1.7-2.3 4.6 1.7-.6 3.2c-.3 1.4-1.6 2.3-3 2.1C10.4 19 5 13.6 4.1 6.2c-.2-1.4.7-2.7 2.1-3z"/>',
  ultimatum: '<rect x="10" y="1.6" width="4" height="2.6" rx=".6"/><circle cx="12" cy="13.6" r="8" fill="none" stroke="currentColor" stroke-width="2.6"/><path d="M12 13.6V8.4" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/>',
  evac: '<path d="M12 2.4l6 6.2h-4v6.2h-4V8.6H6z"/><path d="M2.5 18.2c1.6 0 2.4-1.6 4.75-1.6S10.4 18.2 12 18.2s2.4-1.6 4.75-1.6 3.15 1.6 4.75 1.6" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"/>',
};
const ROLE_ICON = { blue: 'shield', battle: 'swords', home: 'heart', state: 'rings' };
const svgI = (k, cls) => `<svg class="${cls || 'ci'}" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">${ICON[k] || ''}</svg>`;

// The value seal (Card Design doc: A1 position, W1 ribbon seal): the number and role icon in the top half,
// a ribbon in the series color with the branches, or the keyword on Statecraft (which shows no number).
function sealHTML(c) {
  const col = SER[c.series] ? SER[c.series].col : '#555';
  const state = c.series === 'state', home = c.series === 'home';
  const top = state
    ? `<svg x="34" y="12" width="32" height="32" viewBox="0 0 24 24" fill="#EDE4CF" style="color:#EDE4CF">${ICON.rings}</svg>`
    : home
      ? `<text x="50" y="44" text-anchor="middle" class="sn">${c.value}</text><svg x="38" y="47" width="24" height="24" viewBox="0 0 24 24" fill="#EDE4CF">${ICON.heart}</svg>`
      : `<text x="40" y="46" text-anchor="middle" class="sn">${c.value}</text><svg x="52" y="20" width="27" height="27" viewBox="0 0 24 24" fill="#EDE4CF" style="color:#EDE4CF">${ICON[ROLE_ICON[c.series]]}</svg>`;
  let rib = '';
  const marks = state ? (c.keyword ? [c.keyword] : []) : home ? [] : (c.branches || []).filter(b => BRANCH[b]);
  if (!home) {
    const w = 15, gap = 3, tot = marks.length * w + (marks.length - 1) * gap, x0 = 50 - tot / 2;
    rib = `<path d="M-2 56h104l-5 10 5 10H-2l5-10z" fill="${col}" stroke="rgba(0,0,0,.18)" stroke-width="1"/>` +
      marks.map((m, k) => `<svg x="${x0 + k * (w + gap)}" y="58.5" width="${w}" height="${w}" viewBox="0 0 24 24" fill="#EDE4CF" style="color:#EDE4CF">${ICON[m] || ''}</svg>`).join('');
  }
  // No SVG filters here: a filter defined inside a hidden screen blanks every seal that points at it.
  return `<svg class="cseal" viewBox="-4 -2 108 92" aria-hidden="true">
    <circle cx="50" cy="44" r="40" fill="${col}"/><circle cx="50" cy="44" r="35.5" fill="none" stroke="#EDE4CF" stroke-width="1.6" opacity=".75"/>${top}${rib}</svg>`;
}

// A card as the page shows it: a dossier card ({card}) or a loaner ({loaner}).
function cardOf(pick) {
  if (pick.loaner) { const l = (DATA.loaners || []).find(x => x.id === pick.loaner); return l ? { ...l, loaner: true, key: 'l:' + l.id } : null; }
  const c = (DATA.cards || []).find(x => x.id === pick.card); return c ? { ...c, own: true, key: 'c:' + c.id } : null;
}
const imgOf = c => { const inf = c && c.card ? D().card(c.card) : c && c.id && !c.loaner ? D().card(c.id) : null; return (inf && inf.img) || (c && c.img) || ''; };
function cardFaceHTML(c, cls) {
  // A dossier card is its posted picture with the seal drawn over it; a loaner is a typed requisition slip
  // in a dark steel edge (not from your collection, never a rarity).
  if (c.loaner) {
    const s = SER[c.series] || {};
    return `<div class="cface loan ${cls || ''}" style="--sc:${s.col}"><div class="lband"></div>${sealHTML(c)}<div class="lbody"><span class="lkind">LOANER · <em>${esc((s.name || '').toUpperCase())}</em></span><b>${esc(c.title)}</b></div></div>`;
  }
  return `<div class="cface own ${cls || ''}"><img src="${esc(imgOf(c))}" alt="" draggable="false" loading="lazy">${c.value >= 1 ? sealHTML(c) : ''}</div>`;
}

// What a card does, in words, with the number it changes (Campaigns doc: say what it costs).
function roleLine(c) {
  if (c.series !== 'state' && !(c.value >= 1)) return `${SER[c.series] ? SER[c.series].role : 'Card'} · no number yet`;
  if (c.series === 'blue') return `Machine · armor ${c.value} · costs ${c.value} Supply`;
  if (c.series === 'battle') return `Operation · attack ${c.value} for a machine that shares its branch · costs ${c.value} Supply`;
  if (c.series === 'home') return `Rally · repair a machine or raise Resolve by ${c.value} · costs ${c.value} Supply`;
  if (c.series === 'state') return `Statecraft · ${KW[c.keyword] ? KW[c.keyword].name + ': ' + KW[c.keyword].rule : 'no keyword yet'} · free, one a round`;
  return '';
}
const branchWords = bs => { const n = { air: 'air', sea: 'sea', land: 'land' }; const w = bs.map(b => n[b] || b); return w.length > 1 ? w.slice(0, -1).join(', ') + ' and ' + w[w.length - 1] : w[0] || ''; };
const branchNeed = bs => bs.length === 1 ? ({ air: 'the plane', sea: 'the anchor', land: 'the tank' })[bs[0]] : bs.map(b => ({ air: 'the plane', sea: 'the anchor', land: 'the tank' })[b]).join(' or the ');
function stampFor(why) {
  if (!why) return '';
  if (/only: machines|branch/.test(why)) return 'NOT IN THIS CAMPAIGN';
  if (/no number/.test(why)) return 'AWAITING ITS NUMBER';
  if (/other side/.test(why)) return 'THE OTHER SIDE';
  if (/Postwar/.test(why)) return 'COLLECT ONLY';
  if (/or earlier/.test(why)) return 'AFTER ' + ((why.match(/from (\d{4})/) || [])[1] || 'THIS YEAR');
  if (/never be played/.test(why)) return 'NEVER PLAYED';
  return 'NOT PLAYABLE';
}

// ---------- dates ----------
const ET = { timeZone: 'America/New_York' };
const dayMonth = iso => new Date(iso).toLocaleDateString('en-GB', { ...ET, day: 'numeric', month: 'long' });
const waveDate = d => new Date(d + 'T12:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
const shortDate = d => new Date(d + 'T12:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'long', timeZone: 'UTC' });
const sideName = () => DATA.campaign.side === 'axis' ? 'the defenders' : 'Britain';

// ---------- data ----------
const wanted = () => LIVE || (D() && D().cmpPreview());
function load(force) {
  if (!wanted()) return Promise.resolve(null);
  if (loading && !force) return loading;
  loading = D().api('campaign').then(d => { DATA = d; return d; }).catch(e => { loading = null; throw e; });
  return loading;
}
function engineCampaign() {
  // The engine needs only the released chapters; the server holds back the rest until their date.
  const c = DATA.campaign;
  return { id: c.id, side: c.side, year: c.year, startResolve: c.startResolve, chapters: DATA.chapters.filter(ch => ch.released) };
}
const chapterN = n => DATA.chapters.find(c => c.n === n);
function bestText(ch) {
  if (ch.best == null) return '';
  if (ch.best >= 1e6) return `Best: won with a Resolve of ${Math.floor((ch.best - 1e6) / 1000)}`;
  const waves = Math.floor(ch.best / 1000);
  return `Best: ${waves} of ${ch.waves ? ch.waves.length : 3} waves cleared`;
}
function loadRun() { try { RUN = JSON.parse(localStorage.getItem(RUN_STORE) || 'null'); } catch (e) { RUN = null; } return RUN; }
function saveRun() { try { RUN ? localStorage.setItem(RUN_STORE, JSON.stringify(RUN)) : localStorage.removeItem(RUN_STORE); } catch (e) {} }
const runHere = () => RUN && DATA && DATA.campaign && RUN.campaignId === DATA.campaign.id && chapterN(RUN.chapter) && chapterN(RUN.chapter).released;

// ---------- the home door ----------
function tileHTML() {
  const d = DATA;
  if (!d || d.status === 'soon' || d.status === 'none') return '';
  const t = d.campaign ? d.campaign.title : 'Campaigns';
  const go = (sub, cls) => `<button class="cmptile ${cls || 'live'}" id="cmpTile" type="button"><b>Campaigns</b><span>${esc(t)}</span><span>${sub}</span></button>`;
  if (d.status === 'signin') return go('Sign in to fight this month\'s campaign', 'wait');
  if (runHere()) return go(`A run in progress · Chapter ${RUN.chapter}`);
  const open = d.chapters.filter(c => c.released && c.unlocked && !c.won);
  const ch = open[0] || d.chapters.filter(c => c.released && c.unlocked).slice(-1)[0];
  if (!ch) return go('Chapter 1 opens ' + dayMonth(d.chapters[0].opensAt), 'done');
  const left = ch.runsLeft;
  return go(`Chapter ${ch.n}: ${esc(ch.name)} · ${left ? left + ' run' + (left > 1 ? 's' : '') + ' left today' : 'New runs tomorrow'}`, left ? 'live' : 'done');
}
function tile(el) {
  if (!el) return;
  if (!wanted()) { el.innerHTML = ''; return; }
  loadRun();
  if (!DATA) { el.innerHTML = ''; load().then(() => tile(el)).catch(() => {}); return; }
  el.innerHTML = tileHTML();
  const b = $('cmpTile');
  if (b) b.onclick = () => { if (DATA.status === 'signin') { D().toast('Sign in to play Campaigns.'); return; } openCampaign(); };
}

// ---------- the month: three chapters ----------
function openCampaign() {
  $('cmpBody').innerHTML = '<p class="cmpline">Opening the campaign…</p>';
  D().show('sCampaigns'); window.scrollTo(0, 0);
  loadRun();
  load(true).then(drawCampaign).catch(() => { $('cmpBody').innerHTML = '<p class="cmpline">The campaign could not be opened. Try again in a moment.</p>'; });
}
function drawCampaign() {
  const d = DATA;
  if (!d || d.status !== 'open') { $('cmpBody').innerHTML = `<p class="cmpline">${d && d.status === 'signin' ? 'Sign in on the Declass home page to play.' : 'Coming soon.'}</p>`; return; }
  $('cmpBack').hidden = false;
  const c = d.campaign;
  const month = new Date(Date.UTC(c.year, (d.chapters[0].opensAt ? new Date(d.chapters[0].opensAt).getUTCMonth() : 7), 15)).toLocaleDateString('en-GB', { month: 'long', timeZone: 'UTC' });
  let html = `<p class="cmpkicker">${esc(month)} ${c.year} · This month's campaign</p><h2 class="cmptitle">${esc(c.title)}</h2>`;
  if (runHere()) html += `<button class="cmpresume" id="cmpResume" type="button"><b>Back to your run</b><span>Chapter ${RUN.chapter}: ${esc(chapterN(RUN.chapter).name)} · run ${RUN.runNo} of ${d.runsPerDay} today</span></button>`;
  html += `<div class="chaps">${d.chapters.map(chapterTileHTML).join('')}</div>`;
  html += `<p class="cmpsmall">A new chapter opens on the 1st, 11th, and 21st. Win a chapter to open the next one. ${d.runsPerDay} runs a day for each chapter; every run counts, and your best of the day is the one ranked.</p>`;
  $('cmpBody').innerHTML = html;
  const r = $('cmpResume'); if (r) r.onclick = () => resumeRun();
  $('cmpBody').querySelectorAll('[data-ch]').forEach(b => { b.onclick = () => {
    const ch = chapterN(Number(b.dataset.ch));
    if (!ch.released) { D().toast(`Chapter ${ch.n} opens ${dayMonth(ch.opensAt)}.`); return; }
    if (!ch.unlocked) { D().toast(`Win chapter ${ch.n - 1} to open chapter ${ch.n}.`); return; }
    openChapter(ch.n);
  }; });
}
function chapterTileHTML(ch) {
  let state, cls;
  if (!ch.released) { state = `Opens ${esc(dayMonth(ch.opensAt))}`; cls = 'wait'; }
  else if (!ch.unlocked) { state = `Win chapter ${ch.n - 1} to open it`; cls = 'locked'; }
  else if (ch.won) { state = 'Won' + (ch.runsLeft ? ` · ${ch.runsLeft} run${ch.runsLeft > 1 ? 's' : ''} left today` : ''); cls = 'won'; }
  else { state = ch.runsLeft ? `${ch.runsLeft} run${ch.runsLeft > 1 ? 's' : ''} left today` : 'New runs tomorrow'; cls = ch.runsLeft ? 'open' : 'spent'; }
  const files = ch.released ? `<span class="cdates">${ch.waves.map(w => esc(shortDate(w.date))).join(' · ')}</span>` : '';
  return `<button class="chap ${cls}" type="button" data-ch="${ch.n}"><span class="cno">CHAPTER ${ch.n}</span><b>${esc(ch.name)}</b>${files}<span class="cstate">${state}</span>${ch.released ? `<span class="cbest">${esc(bestText(ch))}</span>` : ''}${ch.won ? '<span class="cwon">WON</span>' : ''}</button>`;
}

// ---------- one chapter: the briefing ----------
function openChapter(n) {
  CH = chapterN(n);
  $('cmpBack').hidden = true;
  const ch = CH, c = DATA.campaign;
  const br = ch.branches;
  let html = `<button class="back" id="chBack" type="button">◀︎ ${esc(c.title.split(':')[0])}</button>
    <p class="cmpkicker">Chapter ${ch.n} of ${DATA.chapters.length}</p><h2 class="cmptitle">${esc(ch.name)}</h2>
    <p class="cmplead">${esc(ch.intro)}</p>
    <h3 class="cmph">Three files, three waves</h3>
    <ol class="cfiles">${ch.waves.map((w, i) => `<li><span class="fdate">${esc(waveDate(w.date))}</span><b>${esc(w.name)}</b><span class="fwho">${w.units.map(u => esc(u.name)).join(' · ')}</span></li>`).join('')}</ol>
    <p class="cmpsmall">Each file is one enemy wave. Clear it and the file ends; the next wave attacks in the very next raid. Clear all three to win.</p>
    <div class="cmark"><span>THE MARK TO BEAT · A RESOLVE OF ${ch.benchmark}</span><p>You start at a Resolve of ${c.startResolve}. Attacks you don't block take it down; Home Front cards raise it, up to ${E.RULES.resolveCap}. What is left when the last wave breaks is your score.</p></div>`;
  if (ch.twist) html += `<div class="ctwist"><span>THIS CHAPTER'S TWIST · ${esc(ch.twist.name.toUpperCase())}</span><p>${esc(ch.twist.text)}</p></div>`;
  html += `<p class="cbranch">${br.map(b => svgI(b, 'bi')).join('')}This is ${br.length === 1 ? 'an ' + branchWords(br) : 'a ' + branchWords(br)} campaign. Machines and operations need ${branchNeed(br)}.</p>`;
  html += `<p class="cmpsmall">${ch.calm ? `Rounds 1 and 2 are calm: ${esc(ch.calm.text)} The first raid comes in round 3.` : ''}</p>`;
  const left = ch.runsLeft;
  html += runHere() && RUN.chapter === ch.n
    ? `<button class="btn big cmpgo" id="chGo" type="button">Back to your run</button>`
    : `<button class="btn big cmpgo" id="chGo" type="button"${left ? '' : ' disabled'}>${left ? 'Choose your deck' : 'No runs left today'}</button><p class="cmpsmall c">${left ? `${left} of ${DATA.runsPerDay} runs left today for this chapter` : 'New runs at midnight Eastern.'}</p>`;
  $('cmpBody').innerHTML = html;
  window.scrollTo(0, 0);
  $('chBack').onclick = drawCampaign;
  $('chGo').onclick = () => { if (runHere() && RUN.chapter === ch.n) resumeRun(); else if (left) openDeck(); };
}

// ---------- the deck builder ----------
function pool() {
  // Every card that could be shown: the player's own dispatch cards, then the loaners for this side.
  const n = CH.n;
  const own = (DATA.cards || []).map(c => ({ ...c, own: true, key: 'c:' + c.id, why: (c.why || {})[n] || '' }));
  const lo = (DATA.loaners || []).map(l => ({ ...l, loaner: true, key: 'l:' + l.id, why: (l.why || {})[n] || '' }));
  return { own, lo };
}
const pickKey = p => p.loaner ? 'l:' + p.loaner : 'c:' + p.card;
const countIn = key => PICKS.filter(p => pickKey(p) === key).length;
function loadPicks() {
  let saved = null;
  try { saved = JSON.parse(localStorage.getItem(deckStore(DATA.campaign.id, CH.n)) || 'null'); } catch (e) {}
  const { own, lo } = pool(), ok = new Set(own.concat(lo).filter(c => !c.why).map(c => c.key));
  PICKS = Array.isArray(saved) ? saved.filter(p => p && ok.has(pickKey(p))) : [];
  const seen = new Set(); PICKS = PICKS.filter(p => { if (p.loaner) return true; if (seen.has(p.card)) return false; seen.add(p.card); return true; });
  PICKS = PICKS.slice(0, E.RULES.deckSize);
  return Array.isArray(saved);
}
function savePicks() { try { localStorage.setItem(deckStore(DATA.campaign.id, CH.n), JSON.stringify(PICKS)); } catch (e) {} }

// The suggested deck: the shape of the test bench's Fighter Command deck (6 machines, 6 operations,
// 4 Home Front, 4 Statecraft, on a low to high curve), filled from the player's own cards first, each
// card within one of the wanted number, then loaners.
const SHAPE = { blue: [1, 2, 2, 3, 4, 4], battle: [1, 2, 2, 3, 3, 4], home: [2, 2, 3, 4], state: ['backchannel', 'backchannel', 'evac', 'ultimatum'] };
function suggested() {
  const { own, lo } = pool();
  const mine = own.filter(c => !c.why), loan = lo.filter(c => !c.why), used = new Set(), loanUse = new Map(), out = [];
  for (const s of ['blue', 'battle', 'home', 'state']) {
    for (const want of SHAPE[s]) {
      const fit = c => c.series === s && (s === 'state' ? c.keyword === want : Math.abs(c.value - want) <= 1);
      const dist = c => s === 'state' ? 0 : Math.abs(c.value - want);
      const o = mine.filter(c => fit(c) && !used.has(c.id)).sort((a, b) => dist(a) - dist(b) || b.value - a.value)[0];
      if (o) { used.add(o.id); out.push({ card: o.id }); continue; }
      const l = loan.filter(c => c.series === s && (s === 'state' ? c.keyword === want : true))
        .sort((a, b) => dist(a) - dist(b) || (loanUse.get(a.id) || 0) - (loanUse.get(b.id) || 0))[0]
        || loan.filter(c => c.series === s)[0];
      if (l) { loanUse.set(l.id, (loanUse.get(l.id) || 0) + 1); out.push({ loaner: l.id }); }
    }
  }
  return out.slice(0, E.RULES.deckSize);
}

// The plain words deck check (Testing in the Campaigns doc): what the deck is short of, said as advice.
function deckNotes(cards) {
  const by = s => cards.filter(c => c.series === s);
  const m = by('blue'), o = by('battle'), h = by('home'), s = by('state');
  const notes = [];
  const size = E.RULES.deckSize;
  if (cards.length < size) notes.push(['need', `${size - cards.length} more card${size - cards.length > 1 ? 's' : ''} to go. A deck has ${size}.`]);
  if (!cards.length) return notes;
  if (m.length < 6) notes.push(['warn', `You have ${m.length} machine${m.length === 1 ? '' : 's'}. Most winning decks carry at least 6, since only machines block and attack.`]);
  if (m.length && !m.some(c => c.value <= 2)) notes.push(['warn', 'No machine of 2 or less. Round 1 gives 2 Supply, so the game will swap a bigger one out of your opening hand.']);
  if (o.length < 4) notes.push(['warn', `You have ${o.length} operation${o.length === 1 ? '' : 's'}. A machine with no operation can block but can't attack.`]);
  if (o.length > m.length + 1 && m.length) notes.push(['warn', `${o.length} operations for ${m.length} machines. Some operations may never find a machine to arm.`]);
  if (!h.length) notes.push(['warn', 'No Home Front cards. Nothing to repair a machine or raise your Resolve, and Resolve is your score.']);
  if (s.length > 5) notes.push(['warn', `${s.length} Statecraft cards. Only one can be played a round.`]);
  const heavy = m.concat(o, h).filter(c => c.value >= 5).length;
  if (heavy > 6) notes.push(['warn', `${heavy} cards cost 5 or more. Supply starts at 2 and only reaches 5 in round 4.`]);
  if (cards.length === size && notes.length === 0) notes.push(['ok', `A balanced deck: ${m.length} machines, ${o.length} operations, ${h.length} Home Front, ${s.length} Statecraft.`]);
  return notes;
}

function openDeck() {
  const had = loadPicks();
  drawDeck(!had);
}
function drawDeck(fresh) {
  const ch = CH, br = ch.branches;
  const cards = PICKS.map(cardOf).filter(Boolean);
  const full = cards.length === E.RULES.deckSize;
  const counts = s => cards.filter(c => c.series === s).length;
  const { own, lo } = pool();
  let html = `<button class="back" id="dkBack" type="button">◀︎ Chapter ${ch.n}</button>
    <p class="cmpkicker">Chapter ${ch.n}: ${esc(ch.name)}</p><h2 class="cmptitle">Your deck</h2>
    <p class="cbranch">${br.map(b => svgI(b, 'bi')).join('')}This is ${br.length === 1 ? 'an ' + branchWords(br) : 'a ' + branchWords(br)} campaign. Machines and operations need ${branchNeed(br)}.</p>`;
  if (fresh && !cards.length) html += `<div class="dkfirst"><p>New to Campaigns? Start with the suggested deck. It mixes your own cards with loaners, and you can change any card after.</p><button class="btn big" id="dkSug1" type="button">Use the suggested deck</button><p class="cmpsmall c">or pick your cards below</p></div>`;
  html += `<div class="dkbar"><span class="dkn${full ? ' full' : ''}" aria-label="${cards.length} of ${E.RULES.deckSize} cards"><b>${cards.length}</b>/${E.RULES.deckSize}</span>
    <span class="dkmix">${['blue', 'battle', 'home', 'state'].map(s => `<span class="mx" style="--sc:${SER[s].col}">${svgI(ROLE_ICON[s])}${counts(s)}</span>`).join('')}</span>
    <span class="dkbtns"><button class="tbtn" id="dkSug" type="button">Suggested</button><button class="tbtn" id="dkClr" type="button"${cards.length ? '' : ' disabled'}>Clear</button></span></div>`;
  html += `<div class="dknotes">${deckNotes(cards).map(([k, t]) => `<p class="dn ${k}">${esc(t)}</p>`).join('')}</div>`;
  if (cards.length) {
    // the deck in series order, a loaner taken more than once shown once with its count; tap to take one out
    const groups = [];
    PICKS.forEach((p, i) => { const k = pickKey(p), g = groups.find(x => x.k === k); if (g) g.n++; else groups.push({ k, i, n: 1, c: cardOf(p) }); });
    groups.sort((a, b) => ['blue', 'battle', 'home', 'state'].indexOf(a.c.series) - ['blue', 'battle', 'home', 'state'].indexOf(b.c.series) || a.c.value - b.c.value);
    html += `<div class="dkdeck">${groups.map(g => `<button class="dchip" type="button" data-rm="${g.i}" style="--sc:${SER[g.c.series].col}" aria-label="Take ${esc(g.c.title)} out of the deck">${svgI(ROLE_ICON[g.c.series])}<span class="dv">${g.c.series === 'state' ? '' : g.c.value}</span><span class="dt">${esc(g.c.short || g.c.title)}</span>${g.n > 1 ? `<span class="dnn">×${g.n}</span>` : ''}<span class="dx">✕</span></button>`).join('')}</div>`;
  }
  const sect = (title, sub, list) => `<h3 class="cmph">${title}</h3><p class="cmpsmall">${sub}</p><div class="dkpool">${list.map(poolTileHTML).join('')}</div>`;
  const ownSorted = own.slice().sort((a, b) => (a.why ? 1 : 0) - (b.why ? 1 : 0) || ['blue', 'battle', 'home', 'state'].indexOf(a.series) - ['blue', 'battle', 'home', 'state'].indexOf(b.series));
  html += own.length
    ? sect('Your cards', 'One copy of each card you hold. Greyed out cards can\'t go in this chapter\'s deck; tap one to see why.', ownSorted)
    : `<h3 class="cmph">Your cards</h3><p class="cmpsmall">No cards in your dossier yet. Loaners fill the whole deck.</p>`;
  html += sect('Loaners', 'Real but undated kinds of strength, lent to fill your deck. They carry a steel edge and are never collected. Tap to add a copy.', lo.slice().sort((a, b) => (a.why ? 1 : 0) - (b.why ? 1 : 0) || ['blue', 'battle', 'home', 'state'].indexOf(a.series) - ['blue', 'battle', 'home', 'state'].indexOf(b.series) || a.value - b.value));
  const left = ch.runsLeft;
  html += `<div class="dkgo"><button class="btn big" id="dkStart" type="button"${full && left ? '' : ' disabled'}>${!left ? 'No runs left today' : full ? 'Start the run' : `Add ${E.RULES.deckSize - cards.length} more card${E.RULES.deckSize - cards.length > 1 ? 's' : ''}`}</button></div>`;
  $('cmpBody').innerHTML = html;
  const keep = window.scrollY; window.scrollTo(0, fresh === 'keep' ? keep : 0);
  $('dkBack').onclick = () => openChapter(ch.n);
  const sug = () => { PICKS = suggested(); savePicks(); D().sfx && D().sfx('slide'); drawDeck('keep'); };
  $('dkSug').onclick = sug; if ($('dkSug1')) $('dkSug1').onclick = sug;
  $('dkClr').onclick = () => { PICKS = []; savePicks(); drawDeck('keep'); };
  $('cmpBody').querySelectorAll('[data-rm]').forEach(b => { b.onclick = () => { PICKS.splice(Number(b.dataset.rm), 1); savePicks(); drawDeck('keep'); }; });
  $('cmpBody').querySelectorAll('[data-pk]').forEach(b => { b.onclick = () => tapPool(b.dataset.pk); });
  $('dkStart').onclick = confirmStart;
}
function poolTileHTML(c) {
  const n = countIn(c.key), stamp = stampFor(c.why);
  return `<button class="ptile${c.why ? ' no' : ''}${n ? ' in' : ''}" type="button" data-pk="${esc(c.key)}" aria-label="${esc(c.title)}${c.why ? ': ' + esc(c.why) : ''}">
    ${cardFaceHTML(c, 'sm')}${stamp ? `<span class="pstamp">${stamp}</span>` : ''}${n ? `<span class="pin">${c.loaner ? '×' + n : 'IN DECK'}</span>` : ''}<span class="pname">${esc(c.short || c.title)}</span></button>`;
}
function tapPool(key) {
  const { own, lo } = pool(), c = own.concat(lo).find(x => x.key === key);
  if (!c) return;
  if (c.why) { slip(c, c.why); return; }
  if (c.own && countIn(key)) { PICKS = PICKS.filter(p => pickKey(p) !== key); savePicks(); drawDeck('keep'); return; }
  if (PICKS.length >= E.RULES.deckSize) { D().toast(`The deck is full at ${E.RULES.deckSize}. Tap a card in the deck to take it out.`); return; }
  PICKS.push(c.loaner ? { loaner: c.id } : { card: c.id }); savePicks(); drawDeck('keep');
}
function slip(c, why) {
  D().sheet(`<div class="sheettop"><span class="howstamp">${esc(SER[c.series] ? SER[c.series].name : 'Card')}</span><button class="howx" data-close aria-label="Close">✕</button></div>
    <div class="cmpslip">${cardFaceHTML(c, 'md')}<div><h2>${esc(c.title)}</h2><p class="sheetline">${esc(roleLine(c))}</p>${why ? `<p class="tslip">${esc(why)}</p>` : ''}</div></div>`);
}

// ---------- starting a run ----------
function confirmStart() {
  if (busy) return;
  const left = CH.runsLeft;
  D().sheet(`<div class="sheettop"><span class="howstamp">Start the run</span><button class="howx" data-close aria-label="Close">✕</button></div>
    <h2>Chapter ${CH.n}: ${esc(CH.name)}</h2>
    <p class="sheetline">This uses 1 of your ${left} run${left > 1 ? 's' : ''} left today. A run counts once it starts, even if you leave it.</p>
    <button class="btn" id="cmpStartGo" type="button">Start the run</button><button class="btn alt" data-close type="button">Not yet</button>`);
  $('cmpStartGo').onclick = startRun;
}
function startRun() {
  if (busy) return; busy = true;
  $('cmpStartGo').disabled = true;
  D().api('campaign/start', { chapter: CH.n, deck: PICKS }).then(d => {
    busy = false; D().closeSheet();
    CH.runsLeft = d.runsLeft;
    RUN = { campaignId: DATA.campaign.id, chapter: CH.n, ticket: d.ticket, seed: d.seed, deck: d.deck, choices: [], runNo: d.runNo, day: DATA.day, started: Date.now() };
    saveRun();
    playRun(true);
  }).catch(e => {
    busy = false;
    const m = e.message;
    const msg = m === 'no runs left' ? 'No runs left today for this chapter. New runs at midnight Eastern.' : m === 'locked' ? 'Win the chapter before this one first.' : m === 'not released' ? 'This chapter has not opened yet.' : m === 'deck' ? 'The server found a problem with the deck. Rebuild it and try again.' : 'The run could not be started. Try again in a moment.';
    const b = $('cmpStartGo'); if (b) { b.disabled = false; b.insertAdjacentHTML('beforebegin', `<p class="tslip">${esc(msg)}</p>`); }
  });
}
function resumeRun() { loadRun(); if (!runHere()) { drawCampaign(); return; } CH = chapterN(RUN.chapter); playRun(false); }

// Rebuild the run from its choices: the same seed and the same choices always give the same state.
function rebuild() {
  const camp = engineCampaign();
  ST = E.newRun(camp, RUN.chapter, RUN.deck, RUN.seed);
  for (const c of RUN.choices) { const r = E.act(camp, ST, c); if (!r.ok) { RUN.choices = RUN.choices.slice(0, RUN.choices.indexOf(c)); break; } }
  return ST;
}
function choose(c) {
  const camp = engineCampaign();
  const r = E.act(camp, ST, c);
  if (!r.ok) { D().toast(r.error); return false; }
  RUN.choices.push(c); saveRun();
  return true;
}

// ---------- the run: the plotting table ----------
const UNDOABLE = new Set(['place', 'attach', 'rally', 'lend', 'backchannel', 'evac', 'block', 'attack', 'hold', 'ultimatum']);
function playRun(isNew) {
  rebuild(); LIFT = null;
  D().show('sCmpRun');
  drawRun();
  if (ST.phase === 'opening') openingHand();
  else if (isNew === false && E.calm(ST)) tele('ALL QUIET', allQuietLines());
}
const deckCard = i => { const d = RUN.deck[i]; return { ...ST.cards[i], title: d.title || (d.card && D().card(d.card) ? D().card(d.card).short : 'Card'), card: d.card, loaner: d.loaner ? true : false, short: d.card && D().card(d.card) ? D().card(d.card).short : d.title }; };
function waveLabel() {
  const ch = CH, w = ch.waves[ST.wave];
  return `Wave ${ST.wave + 1} of ${ch.waves.length} · Round ${ST.round} · ${waveDate(w.date)}`;
}
function topBarHTML() {
  const raid = ST.phase === 'enemy', opening = ST.phase === 'opening';
  const lamp = opening ? 'OPENING HAND' : raid ? 'THE RAID' : 'YOUR TURN';
  const sub = E.calm(ST) || opening ? `Calm · first raid in round ${ST.calmRounds + 1}` : waveLabel();
  const sup = raid ? '–' : `${ST.supply}/${E.supplyFor(ST, ST.round)}`;
  return `<div class="tote"><div class="ttile res">${svgI('heart')}<b>${ST.resolve}</b><small>Resolve</small></div>
    <div class="tlamp ${raid ? 'red' : 'amber'}"><span class="lamp"></span><b>${lamp}</b><small>${esc(sub)}</small></div>
    <div class="ttile sup"><b>${sup}</b><small>Supply</small></div></div>`;
}
// "Ju 87 Stukas over the convoy" -> ["Ju 87", "Stukas over the convoy"]: the type in Oswald, the role in type.
const unitWords = u => { const m = String(u.name).match(/^(\S+ \d+\S*)\s*(.*)$/); return m ? [m[1], m[2]] : [u.name, '']; };
function enemyPieceHTML(u, where) {
  const firstRaid = ST.calmRounds + 1;
  const inN = where === 'far' ? Math.max(1, firstRaid - ST.round) : 0;
  const nx = E.nextAttack(u);
  const tab = where === 'far' ? `<span class="etab wait">IN ${inN}</span>` : nx > 0 ? `<span class="etab atk">▼ ${nx}</span>` : '<span class="etab climb">CLIMB</span>';
  const [type, role] = unitWords(u);
  return `<div class="epiece ${where}${u.escort ? ' esc' : ''}" title="${esc(u.name)}">${tab}<span class="eplaque">${u.st}</span><span class="ephoto" data-piece="${esc(u.piece)}"><i>${esc(type)}</i></span><span class="ename">${esc(u.escort ? 'Escort' : role || type)}</span></div>`;
}
function linePieceHTML(m) {
  const c = deckCard(m.card), max = ST.cards[m.card].value, atk = E.opValue(ST, m);
  const face = c.loaner ? `<span class="lpslip">${esc(c.title)}</span>` : `<img src="${esc(imgOf(c))}" alt="" draggable="false">`;
  return `<div class="lpiece${c.loaner ? ' loan' : ''}${m.fresh ? ' fresh' : ''}${m.state === 'out' || m.state === 'blocked' ? ' rearm' : ''}" data-m="${m.uid}" title="${esc(c.title)}">${face}
    <span class="btag">${(ST.cards[m.card].branches || []).map(b => svgI(b)).join('')}</span>
    <span class="bshield${m.arm < max ? ' hurt' : ''}">${svgI('shield')}<b>${m.arm < max ? m.arm + '/' + max : m.arm}</b></span>${atk ? `<span class="batk">${atk}</span>` : ''}
    ${m.fresh ? '<span class="pslip set">SETTING UP</span>' : m.state === 'out' || m.state === 'blocked' ? '<span class="pslip rearm">REARMING</span>' : ''}</div>`;
}
function handHTML() {
  const raid = ST.phase === 'enemy';
  const camp = engineCampaign();
  const n = ST.hand.length;
  return ST.hand.map((i, k) => {
    const c = deckCard(i), why = E.whyNot(camp, ST, i);
    const rot = n > 1 ? (k - (n - 1) / 2) * Math.min(6, 26 / n) : 0;
    return `<button class="hcard${why ? ' dark' : ' lit'}${LIFT === i ? ' up' : ''}${raid && c.keyword === 'ultimatum' && !why ? ' ult' : ''}" type="button" data-h="${i}" style="--r:${rot}deg;--k:${k}" aria-label="${esc(c.title)}">${cardFaceHTML(c, 'hand')}</button>`;
  }).join('');
}
function drawRun() {
  const ch = CH, al = E.alive(ST), calm = E.calm(ST) || ST.phase === 'opening';
  const far = calm ? al : [];
  const channel = calm ? [] : al;
  const slots = [];
  for (let k = 0; k < ST.rules.line; k++) slots.push(ST.line[k] ? linePieceHTML(ST.line[k]) : '<div class="lslot"></div>');
  const btn = ST.phase === 'enemy' ? 'Lock in blocks' : calm ? 'End turn' : 'End turn: attack';
  $('cmpRun').innerHTML = `${topBarHTML()}
    <div class="plot">
      <div class="band far"><span class="pname l">BOULOGNE</span><span class="pname r">CALAIS</span><div class="erow">${far.map(u => enemyPieceHTML(u, 'far')).join('')}</div></div>
      <div class="band chan"><span class="compass" aria-hidden="true"><i>S</i></span><span class="chname">THE CHANNEL</span><div class="erow">${channel.map(u => enemyPieceHTML(u, 'chan')).join('')}</div><div class="tele" id="cmpTele" hidden></div>
        <div class="actbar"><button class="rmenu" id="cmpMenu" type="button" aria-label="Round menu">☰</button><button class="actbtn${ST.phase === 'enemy' ? ' raid' : ''}" id="cmpAct" type="button"${ST.phase === 'opening' ? ' disabled' : ''}>${btn}</button></div></div>
      <div class="band coast"><span class="pname l">FOLKESTONE</span><span class="pname r">DOVER</span><div class="lrow">${slots.join('')}</div></div>
    </div>
    <div class="hand${ST.phase === 'enemy' ? ' down' : ''}" id="cmpHand">${handHTML()}</div>
    <div class="liftbox" id="cmpLift" hidden></div>
    <div class="cmpover" id="cmpOver" hidden></div>`;
  $('cmpAct').onclick = act;
  $('cmpMenu').onclick = menu;
  $('cmpRun').querySelectorAll('[data-h]').forEach(b => { b.onclick = () => lift(Number(b.dataset.h)); });
  $('cmpRun').querySelectorAll('[data-m]').forEach(b => { b.onclick = () => pieceInfo(b.dataset.m); });
  if (LIFT != null && ST.hand.includes(LIFT)) showLift(LIFT); else LIFT = null;
  if (ST.phase === 'enemy') raidHold();
}

// The opening hand: five cards, keep them or take the one mulligan.
function openingHand() {
  const o = $('cmpOver');
  const cards = ST.hand.map(deckCard);
  o.innerHTML = `<div class="ohand"><p class="okick">YOUR OPENING HAND</p>
    <div class="orow">${cards.map(c => cardFaceHTML(c, 'open')).join('')}</div>
    <p class="oline">Five cards from your shuffled deck. There is always a machine you can afford in round 1.</p>
    <button class="btn big" id="ohKeep" type="button">Keep this hand</button>
    <button class="btn alt big" id="ohMull" type="button"${ST.mulliganed ? ' disabled' : ''}>${ST.mulliganed ? 'Mulligan used' : 'Mulligan · draw 5 new'}</button>
    <p class="oline small">One mulligan a run: your hand goes back into the deck and you draw 5 new cards. Everyone's run ${RUN.runNo} today uses the same shuffle.</p></div>`;
  o.hidden = false;
  $('ohKeep').onclick = () => { if (choose({ a: 'keep' })) { o.hidden = true; drawRun(); tele('ALL QUIET', allQuietLines()); } };
  $('ohMull').onclick = () => { if (!ST.mulliganed && choose({ a: 'mulligan' })) { D().sfx && D().sfx('slide'); openingHand(); } };
}
function hostileNames(list) {
  const n = [...new Set(list.map(u => unitWords(u)[0]))];
  return n.join(', ');
}
function allQuietLines() {
  return [`Hostiles massing over France: ${hostileNames(E.alive(ST))}.`, 'Build your line before they come.'];
}
let teleT = 0;
function tele(head, lines) {
  const t = $('cmpTele'); if (!t) return;
  t.innerHTML = `<b>${esc(head)}</b>${lines.map(l => `<span>${esc(l)}</span>`).join('')}`;
  t.hidden = false; t.classList.remove('go'); void t.offsetWidth; t.classList.add('go');
  clearTimeout(teleT); teleT = setTimeout(() => { t.hidden = true; }, 3200);
  t.onclick = () => { clearTimeout(teleT); t.hidden = true; };
}

// A hand card lifted: what it does, what it costs, and the plays it can make right now.
function lift(i) {
  if (ST.phase === 'opening') return;
  LIFT = LIFT === i ? null : i;
  $('cmpRun').querySelectorAll('[data-h]').forEach(b => b.classList.toggle('up', Number(b.dataset.h) === LIFT));
  if (LIFT == null) { $('cmpLift').hidden = true; return; }
  showLift(i);
}
function playsFor(i) {
  // Every play the engine would accept for this card, found by trying it on a copy of the run.
  const camp = engineCampaign(), c = ST.cards[i], out = [];
  const tryIt = (choice, label) => { const s = E.copy(ST); if (E.act(camp, s, choice).ok) out.push({ choice, label }); };
  const nm = m => deckCard(m.card).short || deckCard(m.card).title;
  if (c.series === 'blue') tryIt({ a: 'place', card: i }, `Put on your line · ${c.value} Supply`);
  if (c.series === 'battle') ST.line.forEach(m => tryIt({ a: 'attach', card: i, machine: m.uid }, `Arm ${nm(m)} · attack ${c.value} · ${c.value} Supply`));
  if (c.series === 'home') {
    tryIt({ a: 'rally', card: i, to: 'resolve' }, `Raise Resolve from ${ST.resolve} to ${Math.min(ST.rules.resolveCap, ST.resolve + c.value)} · ${c.value} Supply`);
    ST.line.forEach(m => { const max = ST.cards[m.card].value; tryIt({ a: 'rally', card: i, to: m.uid }, `Repair ${nm(m)} from ${m.arm} to ${Math.min(max, m.arm + c.value)} · ${c.value} Supply`); });
  }
  if (c.series === 'state') {
    if (c.keyword === 'backchannel') tryIt({ a: 'backchannel', card: i }, `Back Channel: draw ${E.BACK_CHANNEL_DRAW} cards · free`);
    if (c.keyword === 'lend') E.lendable(camp, ST).forEach(p => tryIt({ a: 'lend', card: i, pick: p }, `Lend Lease: bring in ${deckCard(p).short || deckCard(p).title} (armor ${ST.cards[p].value}) · free`));
    if (c.keyword === 'evac') E.evacuable(ST).forEach(p => tryIt({ a: 'evac', card: i, pick: p }, `Evacuation: bring ${deckCard(p).short || deckCard(p).title} back to your hand · free`));
  }
  return out;
}
function showLift(i) {
  const c = deckCard(i), why = E.whyNot(engineCampaign(), ST, i), plays = why ? [] : playsFor(i);
  const box = $('cmpLift');
  box.innerHTML = `<div class="lbtop"><b>${esc(c.title)}</b><button class="howx" id="lbX" aria-label="Close">✕</button></div><p class="lbrole">${esc(roleLine(c))}</p>
    ${why ? `<p class="tslip">${esc(why)}</p>` : plays.length ? plays.map((p, k) => `<button class="lbplay" type="button" data-p="${k}">${esc(p.label)}</button>`).join('') : '<p class="tslip">Nothing to play it on right now.</p>'}`;
  box.hidden = false;
  $('lbX').onclick = () => lift(i);
  box.querySelectorAll('[data-p]').forEach(b => { b.onclick = () => { if (choose(plays[Number(b.dataset.p)].choice)) { LIFT = null; D().sfx && D().sfx('slide'); drawRun(); } }; });
}
function pieceInfo(uid) {
  const m = ST.line.find(x => x.uid === uid); if (!m) return;
  const c = deckCard(m.card), max = ST.cards[m.card].value, op = m.op != null ? deckCard(m.op) : null;
  const state = m.fresh ? 'Setting up: it can block in the next raid, but it can\'t be armed until your next turn.' : m.state === 'out' ? 'Rearming: it attacked, so it sits out the next raid.' : m.state === 'blocked' ? 'Rearming: it blocked, so it can\'t attack this turn.' : 'Ready.';
  D().sheet(`<div class="sheettop"><span class="howstamp">On your line</span><button class="howx" data-close aria-label="Close">✕</button></div>
    <div class="cmpslip">${cardFaceHTML(c, 'md')}<div><h2>${esc(c.title)}</h2><p class="sheetline">Armor ${m.arm} of ${max}. ${op ? `Armed with ${esc(op.title)}: attack ${op.value}.` : 'No operation: it can block but not attack.'}</p><p class="sheetnote">${state}</p></div></div>`);
}

// The action button: End turn in the calm rounds. The raid itself is the next build session.
function act() {
  if (ST.phase === 'yours') {
    LIFT = null;
    if (!choose({ a: 'end' })) return;
    drawRun();
    if (E.calm(ST)) tele('ALL QUIET', allQuietLines());
    else if (ST.phase === 'enemy') tele('RAID INBOUND', [`Hostiles plotted over the Channel: ${hostileNames(E.alive(ST).filter(u => E.incoming(ST, u) > 0))}.`, 'Scramble your fighters to block them.']);
  }
}
function raidHold() {
  // Build session 3 stops here: the raid, blocking, attacks, and debriefs come with the battlefield.
  const o = $('cmpOver');
  setTimeout(() => {
    if (!$('cmpOver') || ST.phase !== 'enemy') return;
    o.innerHTML = `<div class="ohand hold"><p class="okick">PREVIEW · BUILD SESSION 3</p><p class="oline">The first raid comes in here. Blocking, attacking, and the debriefs arrive with the battlefield in the next build session, so this preview run stops at round ${ST.round}.</p>
      <button class="btn big" id="holdLeave" type="button">Leave the run</button><button class="btn alt big" id="holdLook" type="button">Look at the table</button></div>`;
    o.hidden = false;
    $('holdLeave').onclick = leaveRun;
    $('holdLook').onclick = () => { o.hidden = true; };
  }, 1400);
}
function menu() {
  const last = RUN.choices[RUN.choices.length - 1];
  const canUndo = last && UNDOABLE.has(last.a);
  D().sheet(`<div class="sheettop"><span class="howstamp">Round menu</span><button class="howx" data-close aria-label="Close">✕</button></div>
    <button class="btn alt" id="mUndo" type="button"${canUndo ? '' : ' disabled'}>Undo last move</button>
    <button class="btn alt" id="mDeck" type="button">Cards left in your deck</button>
    <button class="btn danger" id="mLeave" type="button">Leave the run</button>
    <p class="sheetnote">${canUndo ? 'Any move can be undone until you press the action button.' : 'Nothing to undo since the action button was last pressed.'}</p>`);
  $('mUndo').onclick = () => { if (!canUndo) return; RUN.choices.pop(); saveRun(); rebuild(); D().closeSheet(); LIFT = null; drawRun(); };
  $('mDeck').onclick = () => {
    const left = ST.draw.map(deckCard).sort((a, b) => ['blue', 'battle', 'home', 'state'].indexOf(a.series) - ['blue', 'battle', 'home', 'state'].indexOf(b.series) || a.value - b.value);
    D().sheet(`<div class="sheettop"><span class="howstamp">Your deck</span><button class="howx" data-close aria-label="Close">✕</button></div><h2>${left.length} card${left.length === 1 ? '' : 's'} left to draw</h2><p class="sheetnote">In no particular order. You draw 1 at the start of each of your turns after the first.</p>
      <div class="dkdeck">${left.map(c => `<span class="dchip" style="--sc:${SER[c.series].col}">${svgI(ROLE_ICON[c.series])}<span class="dv">${c.series === 'state' ? '' : c.value}</span><span class="dt">${esc(c.short || c.title)}</span></span>`).join('')}</div>`);
  };
  $('mLeave').onclick = () => {
    D().sheet(`<div class="sheettop"><span class="howstamp">Leave the run</span><button class="howx" data-close aria-label="Close">✕</button></div><h2>Leave this run?</h2><p class="sheetline">It still counts as one of today's runs, and it can't be picked up again.</p>
      <button class="btn danger" id="mLeaveGo" type="button">Leave the run</button><button class="btn alt" data-close type="button">Keep playing</button>`);
    $('mLeaveGo').onclick = () => { D().closeSheet(); leaveRun(); };
  };
}
function leaveRun() {
  RUN = null; saveRun(); ST = null;
  load(true).then(() => { D().show('sCampaigns'); if (CH) openChapter(CH.n); else drawCampaign(); }).catch(() => { D().goHome(); });
}

// ---------- wiring ----------
function boot() {
  const b = $('cmpBack'); if (b) b.onclick = () => D().goHome();
  // The home screen may already be drawn by the time this module loads.
  if ($('sHome') && $('sHome').classList.contains('on')) tile($('cmpSlot'));
}
window.Campaigns = { tile, open: openCampaign };
if (window.Declass) boot(); else window.addEventListener('load', boot);
