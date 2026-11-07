// Intercept · a Declass daily puzzle (built 27 Oct 2026). Twelve files on the desk, four hidden links of
// three. Select three, File it. Right: they're clipped together with the link. Wrong: a REJECTED stamp.
// The server deals, checks, scores, and pays; this page only shows. Hooks into declass.js via window.Declass.
(function () {
  'use strict';
  const D = () => window.Declass;
  const $ = id => document.getElementById(id);
  const esc = t => String(t == null ? '' : t).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const info = id => D().card(id);
  let P = null;          // the puzzle as the server last described it
  let sel = [];          // selected card positions
  let busy = false;
  let rejectedHit = -1;  // the mistake mark to stamp on the next draw
  // A finished puzzle is a straight path (7 Nov 2026): the review (score and the four links, one screen,
  // no way back but Done), then the card pick, then the reveal, then home.
  let stage = 'review';

  // ---------- home tile ----------
  function tileHTML(s) {
    // Coming soon is one slim line in the home page's coming up list (30 Oct 2026); live, it is a full Today's files row.
    if (!s || s.status === 'soon') return `<div class="cupln icpsoon" aria-label="Code Room, a Declass daily puzzle, coming soon"><span class="tg ic">CODE ROOM</span><span class="cw">Daily puzzle</span><span class="r">Coming soon</span></div>`;
    // the first part sits on its own line, the rest below it (29 Oct 2026)
    const two = sub => { const i = sub.indexOf(' · '); return i < 0 ? `<span>${sub}</span>` : `<span>${sub.slice(0, i)}</span><span>${sub.slice(i + 3)}</span>`; };
    const go = (sub, cls) => `<button class="icptile ${cls || 'live'}" id="icpTile" type="button"><b>Code Room</b>${two(sub)}</button>`;
    if (s.status === 'signin') return go('a Declass daily puzzle · Sign in to crack today\'s files', 'wait');
    if (s.status === 'new') return go('a Declass daily puzzle · Crack today\'s files');
    if (s.status === 'play') return go(`In progress · ${s.found} of 4 links · ${s.mistakes} of 3 mistakes`);
    // The score is points out of 100 (25 a link, minus 10 a mistake), so the tile says so (7 Nov 2026).
    if (s.status === 'solved') return go(`Cracked · Scored ${s.score} of 100 · ${s.canClaim ? 'Pick your card by midnight Eastern' : 'New files tomorrow'}`, s.canClaim ? 'live claim' : 'done');
    return go('Not cracked today · New files tomorrow', 'done');
  }
  function tile(el) {
    const s = D().state() && D().state().intercept;
    el.innerHTML = tileHTML(s);
    // The Field manual's Intercept section shows once the puzzle is open to this player.
    const soon = !s || s.status === 'soon';
    document.querySelectorAll('#fm-intercept, [data-go="fm-intercept"]').forEach(x => { x.hidden = soon; });
    const b = $('icpTile');
    if (b) b.onclick = () => { if (s.status === 'signin') { D().toast('Sign in to play the Code Room.'); return; } open(); };
  }

  // ---------- the screen ----------
  function open() {
    $('sIntercept').classList.remove('slim'); $('icpBarMarks').innerHTML = '';
    $('icpBody').innerHTML = '<p class="icpline">Opening the files…</p>';
    D().show('sIntercept');
    D().api('intercept').then(d => {
      if (d.status === 'soon') { $('icpBody').innerHTML = '<p class="icpline">Coming soon.</p>'; return; }
      if (d.status === 'signin') { $('icpBody').innerHTML = '<p class="icpline">Sign in on the Declass home page to play.</p>'; return; }
      if (d.status === 'new') return intro(d);
      P = d.puzzle; sel = []; stage = P.status === 'solved' && P.canClaim ? 'pick' : 'review'; draw();
    }).catch(() => { $('icpBody').innerHTML = '<p class="icpline">The files could not be opened. Try again in a moment.</p>'; });
  }
  function minutesLeft(iso) { return Math.max(0, Math.round((Date.parse(iso) - Date.now()) / 60000)); }
  function closesLine(iso) {
    const m = minutesLeft(iso);
    if (m <= 60) return `<p class="icpwarn">This file closes in ${m} minute${m === 1 ? '' : 's'}.</p>`;
    return `<p class="icpsmall">Today's files close at ${D().localTime(iso)}, midnight Eastern.</p>`;
  }
  function intro(d) {
    $('icpBody').innerHTML = `<h2 class="icph">Crack today's files</h2>
      <p class="icplead">Twelve files. Four hidden links, three files each. Find the links between the files.</p>
      <ul class="icprules"><li>Select three files and tap <b>File it</b>.</li><li>Three mistakes and the files close.</li><li>No clock. Take your time.</li></ul>
      ${closesLine(d.closes)}
      <button class="btn big icpgo" id="icpStart">Open today's files</button>`;
    $('icpStart').onclick = start;
  }
  function start() {
    if (busy) return; busy = true;
    $('icpStart').disabled = true;
    D().sfx('slide');
    D().api('intercept/start', {}).then(d => { busy = false; P = d.puzzle; sel = []; draw(); maybeGuide(); })
      .catch(e => {
        busy = false;
        const msg = e.message === 'no grid' ? 'The files are still being sorted. Try again in a moment.' : 'The files could not be opened. Try again in a moment.';
        $('icpBody').insertAdjacentHTML('beforeend', `<p class="icpwarn">${msg}</p>`);
        const b = $('icpStart'); if (b) b.disabled = false;
      });
  }

  // A magnifier in the corner of each card opens it full size (7 Nov 2026). Tap and hold also still works,
  // but iOS can answer a long press on a picture with its own share menu, so the magnifier is the main way.
  const mag = '<span class="zoomb" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M15 15l5 5" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg></span>';
  const clip = '<svg class="pclip" viewBox="0 0 24 60" aria-hidden="true"><path d="M8 40V12a5 5 0 0 1 10 0v34a8 8 0 0 1-16 0V16" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>';
  // The board shows tiles made for the puzzle (decided 7 Nov 2026, concept D): the card's original photo
  // and a typed label, so the subject reads at a glance on a phone. The label is the title and the year
  // only: the place gave links away (Brian, 7 Nov), and it stays on the full card behind the magnifier.
  // The label shows at once and the photo fades in when it arrives. The result screen and the pick show
  // the full cards.
  const tileLine = inf => String(inf.date || '').slice(0, 4);
  function fileHTML(i, extra) {
    const c = P.cards[i], inf = info(c.id) || {};
    const label = inf.tileLabel || inf.short || 'File';
    return `<button class="icpcard tile${sel.includes(i) ? ' sel' : ''}${extra || ''}" data-i="${i}" type="button" aria-pressed="${sel.includes(i)}" aria-label="${esc(label)}, ${esc(tileLine(inf))}"><span class="tp"><img src="${esc(inf.tilePhoto || inf.img || '')}" data-fallback="${esc(inf.img || '')}" alt="" draggable="false" loading="eager"></span><span class="tl"><b>${esc(label)}</b><small>${esc(tileLine(inf))}</small></span>${mag}</button>`;
  }
  // During play a found group is a slim row (three small cards and the link) so it doesn't push the open
  // files down the screen; the result screen shows the full clipped groups (7 Nov 2026).
  function rowHTML(g, k) {
    return `<div class="icprow${g.found === false ? ' missed' : ''}" style="--k:${k}"><div class="rcards">${g.idx.map(i => { const inf = info(P.cards[i].id) || {}; return `<button class="gcard" data-i="${i}" type="button" aria-label="See ${esc(inf.tileLabel || inf.short || 'this card')} full size"><img src="${esc(inf.tilePhoto || inf.img || '')}" alt="" draggable="false"></button>`; }).join('')}</div><p class="rlink">${g.found === false ? '<span class="gmiss">Not found · </span>' : ''}${esc(g.link)}<small>${g.idx.map(i => esc((info(P.cards[i].id) || {}).tileLabel || '')).join(' · ')}</small></p></div>`;
  }

  function marksHTML() {
    return `<div class="icpmarks" aria-label="${P.mistakes} of 3 mistakes used"><span class="ml">Mistakes</span>${[0, 1, 2].map(i => `<span class="mark${i < P.mistakes ? ' used' : ''}${i === rejectedHit ? ' hit' : ''}"><i>REJECTED</i></span>`).join('')}</div>`;
  }

  function draw() {
    if (!P) return;
    const done = P.status !== 'play';
    const taken = new Set(P.groups.flatMap(g => g.idx));
    const left = P.cards.map((_, i) => i).filter(i => !taken.has(i));
    let html = '';
    // Once the files are open the big title steps aside for a slim bar pinned to the top, holding the
    // mistake marks so a REJECTED stamp is always in view, however far down the desk you are (7 Nov 2026).
    $('sIntercept').classList.add('slim');
    $('sIntercept').classList.toggle('ended', done);
    $('icpBarMarks').innerHTML = done ? '' : marksHTML();
    if (P.practice) html += `<p class="icppractice">Practice round ${P.practice} · testers only · no Intel</p>`;
    if (!done) {
      html += P.groups.length ? `<div class="icprows">${P.groups.map(rowHTML).join('')}</div>` : '';
      html += `<div class="icpdesk" id="icpDesk">${left.map(i => fileHTML(i)).join('')}</div>`;
      html += `<div class="icpctl"><button class="btn alt" id="icpClear" type="button"${sel.length ? '' : ' disabled'}>Clear</button><button class="btn icpfile" id="icpFile" type="button"${sel.length === 3 ? '' : ' disabled'}>File it</button></div>`;
      html += `<p class="icpsmall">Tap the magnifier on a card to see it full size.</p>${P.expired ? '' : closesLine(P.closes)}`;
    } else {
      html += stage === 'pick' && P.status === 'solved' && P.canClaim ? pickScreenHTML() : resultHTML();
    }
    $('icpBody').innerHTML = html;
    rejectedHit = -1;
    wire();
  }

  function resultHTML() {
    const solved = P.status === 'solved';
    const m = P.mistakes;
    const head = solved
      ? `<div class="icpscore"><span class="sstamp">CRACKED</span><b>${P.score}</b><small>out of 100 · ${m === 0 ? 'No mistakes' : m + ' mistake' + (m > 1 ? 's' : '')}</small></div>`
      : `<div class="icpscore lost"><span class="sstamp">FILES CLOSED</span><b>${P.found} of 4</b><small>links found</small></div>`;
    const bonus = P.intel - 3;
    const why = solved ? (P.score === 100 ? 'a perfect solve' : 'the solve') : 'trying';
    const intel = P.practice ? '<p class="icpintel">Practice round · no Intel, and the card can\'t come Top Secret</p>'
      : `<p class="icpintel"><img class="itok" src="/declass/icons/intel.svg" alt="">+${P.intel} Intel · 3 for playing, ${bonus} for ${why}</p>`;
    let after = '';
    if (solved && P.claimed) {
      const inf = info(P.claimed.card);
      after = `<p class="icpnext">You picked <b>${esc(inf ? inf.short : 'a card')}</b>${P.claimed.finish ? ', ' + esc(D().FNAME[P.claimed.finish]) + (P.claimed.variant === 'living' ? ' Living Card' : '') : ''}. New files tomorrow.</p>`;
    } else if (solved) after = '<p class="icpnext">Tap Done to pick your card.</p>';
    else after = '<p class="icpnext">No card this time. New files tomorrow.</p>';
    return `${head}${intel}
      <div class="icprows review">${P.groups.map(rowHTML).join('')}</div>
      ${after}
      <div class="icpctl"><button class="btn alt" id="icpShare" type="button">Share</button><button class="btn" id="icpDone" type="button">Done</button></div>
      ${tester() ? '<div class="icpctl"><button class="btn alt icpreplay" id="icpReplay" type="button">Play again · tester practice</button></div>' : ''}`;
  }
  // The reward: pick any one of the twelve (7 Nov 2026, its own screen after the review).
  function pickScreenHTML() {
    return `<h2 class="icph">Pick a card</h2><p class="icplead">${P.perfect ? 'A perfect solve. Whatever you pick comes Silver or better.' : 'Solve it, pick a card. Solve it perfectly, it\'s Silver or better.'} Any of the twelve, even one you don't own yet.</p>
      ${pickLegend()}
      <div class="icpdesk pick" id="icpPick">${P.cards.map((c, i) => pickHTML(c, i)).join('')}</div>
      <p class="icpsmall">Tap the magnifier on a card to see it full size.</p>`;
  }
  // Testers can replay as often as they like (7 Nov 2026): the button shows with the preview flag on, and
  // the server checks the account is a tester. Practice rounds pay no Intel and never roll Top Secret.
  function tester() { try { return Boolean(localStorage.getItem('declass_icp')); } catch (e) { return false; } }
  function replay() {
    if (busy) return; busy = true;
    const b = $('icpReplay'); if (b) b.disabled = true;
    D().api('intercept/replay', {}).then(d => { busy = false; P = d.puzzle; sel = []; stage = 'review'; draw(); window.scrollTo(0, 0); D().sfx('slide'); })
      .catch(e => { busy = false; if (b) b.disabled = false; D().toast(e.message === 'no grid' ? 'The files are still being sorted. Try again.' : 'Practice rounds are for testers with the preview on.'); });
  }
  // Pick 1 (7 Nov 2026, Brian's choice on the design canvas): the real cards four across, each with four
  // squares under it for Copper, Silver, Gold, and Top Secret, filled for the finishes already in the
  // dossier (for the variant on offer: a Living Card shows the living finishes held). A card not yet held
  // says NEW TO YOU; one with every finish fades. On a perfect solve Copper can't drop, so its empty square fades.
  const FINS = ['copper', 'silver', 'gold', 'topsecret'];
  const FLABEL = { copper: 'Copper', silver: 'Silver', gold: 'Gold', topsecret: 'Top Secret' };
  function pickHTML(c, i) {
    const inf = info(c.id); if (!inf) return '';
    const h = D().holdings().get(c.id);
    const v = c.v === 'living' ? 'living' : 'still';
    const held = f => Boolean(h && h[v] && h[v][f]);
    const own = Boolean(h && FINS.some(held));
    const full = FINS.every(held);
    if (inf.flash) return `<div class="icpcard flash nopick" data-zi="${i}"><span class="pc"><img src="${esc(inf.img)}" alt="${esc(inf.short)}" draggable="false">${mag}</span><span class="pfin note">Flash cards can't be picked</span></div>`;
    const squares = FINS.map(f => `<i class="f-${f}${held(f) ? ' on' : ''}${!held(f) && f === 'copper' && P.perfect && !P.practice ? ' off' : ''}" title="${FLABEL[f]}${held(f) ? ', in your dossier' : ''}"></i>`).join('');
    const say = !own ? 'not in your dossier yet' : full ? 'you hold every finish' : 'you hold ' + FINS.filter(held).map(f => FLABEL[f]).join(', ');
    return `<button class="icpcard${own ? '' : ' unowned'}${full ? ' full' : ''}" data-pick="${i}" type="button" aria-label="Pick ${esc(inf.short)}${v === 'living' ? ', Living Card' : ''}, ${say}"><span class="pc"><img src="${esc(inf.img)}" alt="" draggable="false">${own ? '' : '<span class="wax" title="Not in your dossier yet"></span>'}${v === 'living' ? '<span class="ptag live">▶︎ Living</span>' : ''}${mag}</span>${own ? `<span class="pfin" aria-hidden="true">${squares}</span>` : '<span class="pfin new">New to you</span>'}</button>`;
  }
  function pickLegend() {
    return `<div class="pleg" aria-hidden="true">${FINS.map(f => `<span><i class="f-${f} on"></i>${FLABEL[f]}</span>`).join('')}<small>Filled: in your dossier · empty: still to collect</small></div>`;
  }

  // ---------- touch: tap selects, tap and hold shows the card full size ----------
  function holdable(el, onTap) {
    let timer = null, held = false, sx = 0, sy = 0;
    el.addEventListener('pointerdown', e => { held = false; sx = e.clientX; sy = e.clientY; clearTimeout(timer); timer = setTimeout(() => { held = true; zoom(el); }, 450); });
    el.addEventListener('pointermove', e => { if (Math.abs(e.clientX - sx) + Math.abs(e.clientY - sy) > 12) clearTimeout(timer); });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(k => el.addEventListener(k, () => clearTimeout(timer)));
    el.addEventListener('contextmenu', e => e.preventDefault());
    el.addEventListener('click', e => {
      if (held) { e.preventDefault(); held = false; return; }
      if (e.target.closest && e.target.closest('.zoomb')) { e.preventDefault(); zoom(el); return; }
      onTap();
    });
  }
  function zoom(el) {
    const i = Number(el.dataset.i != null ? el.dataset.i : el.dataset.pick != null ? el.dataset.pick : el.dataset.zi);
    const c = P.cards[i], inf = c && info(c.id); if (!inf) return;
    const z = $('icpZoom');
    z.innerHTML = `<img src="${esc(inf.img)}" alt="${esc(inf.short)}"><p>Tap anywhere to close</p>`;
    z.hidden = false;
    if (navigator.vibrate) try { navigator.vibrate(10); } catch (e) {}
  }

  function wire() {
    document.querySelectorAll('#icpDesk .icpcard').forEach(b => holdable(b, () => toggle(Number(b.dataset.i), b)));
    // Each tile photo fades in once it arrives (instantly if the phone already has it); one that fails
    // falls back to the full card image.
    document.querySelectorAll('.icpcard.tile img, .icprow .gcard img').forEach(im => {
      const shown = () => im.classList.add('ok');
      if (im.complete && im.naturalWidth) shown(); else im.addEventListener('load', shown, { once: true });
      if (im.dataset.fallback) im.addEventListener('error', () => { if (im.src !== im.dataset.fallback) im.src = im.dataset.fallback; }, { once: true });
    });
    document.querySelectorAll('.icpgroup .gcard, .icprow .gcard').forEach(b => holdable(b, () => zoom(b)));
    document.querySelectorAll('#icpPick .nopick').forEach(b => holdable(b, () => {}));
    const f = $('icpFile'); if (f) f.onclick = fileIt;
    const c = $('icpClear'); if (c) c.onclick = () => { sel = []; refreshSel(); };
    document.querySelectorAll('#icpPick [data-pick]').forEach(b => holdable(b, () => confirmPick(Number(b.dataset.pick))));
    const s = $('icpShare'); if (s) s.onclick = share;
    const dn = $('icpDone'); if (dn) dn.onclick = done;
    const rp = $('icpReplay'); if (rp) rp.onclick = replay;
  }
  function toggle(i, b) {
    if (busy) return;
    const k = sel.indexOf(i);
    if (k >= 0) sel.splice(k, 1);
    else { if (sel.length >= 3) { D().nudge(b); return; } sel.push(i); }
    D().sfx('slide');
    refreshSel();
  }
  function refreshSel() {
    document.querySelectorAll('#icpDesk .icpcard').forEach(b => { const on = sel.includes(Number(b.dataset.i)); b.classList.toggle('sel', on); b.setAttribute('aria-pressed', on); });
    $('icpFile').disabled = sel.length !== 3;
    $('icpClear').disabled = !sel.length;
  }

  function fileIt() {
    if (busy || sel.length !== 3) return;
    busy = true;
    // Answer the tap at once (7 Nov 2026): the guess goes to the server and the result can take a moment
    // on a phone, so the button says so and the three tiles pulse until it comes back.
    const fb = $('icpFile'); fb.disabled = true; fb.classList.add('wait'); fb.textContent = 'Filing…';
    document.querySelectorAll('#icpDesk .icpcard.sel').forEach(b => { b.classList.remove('shake'); b.classList.add('filing'); });
    D().sfx('slide', 0.5);
    const pick = sel.slice();
    D().api('intercept/guess', { day: P.day, pick }).then(d => {
      busy = false; unwait();
      if (d.result === 'tried') { D().toast('Already tried. That one doesn\'t count against you.'); P = d.puzzle; refreshSel(); return; }
      if (d.result === 'correct') {
        P = d.puzzle; sel = []; stage = 'review';
        D().sfx('stampA');
        if (P.status === 'solved') { D().sfx('goldA', 0.3); D().glowFor('gold'); }
        draw();
        const g = document.querySelectorAll(P.status === 'play' ? '.icprow' : '.icpgroup'); const last = g[P.status === 'solved' ? 0 : g.length - 1];
        if (P.status === 'play' && last) { last.classList.add('fresh'); }
        if (P.status !== 'play') { refreshHome(); window.scrollTo(0, 0); }
        return;
      }
      if (d.result === 'wrong') {
        // The shake clears itself when it ends, so it can never replay later and look like a hint (7 Nov 2026).
        document.querySelectorAll('#icpDesk .icpcard.sel').forEach(b => { b.classList.remove('shake'); void b.offsetWidth; b.classList.add('shake'); b.addEventListener('animationend', () => b.classList.remove('shake'), { once: true }); setTimeout(() => b.classList.remove('shake'), 600); });
        D().sfx('locked'); D().sfx('stampA', 0.15);
        rejectBanner(d.puzzle.mistakes);
        setTimeout(() => {
          rejectedHit = d.puzzle.mistakes - 1;
          P = d.puzzle;
          if (P.status !== 'play') { sel = []; stage = 'review'; draw(); refreshHome(); window.scrollTo(0, 0); return; }
          const marks = document.querySelector('.icpmarks'); if (marks) marks.outerHTML = marksHTML();
          rejectedHit = -1; refreshSel();
        }, 380);
        return;
      }
      P = d.puzzle; draw(); // finished or stale: show what the server has
    }).catch(e => {
      busy = false; unwait();
      if (e.message === 'expired') { D().toast('That file closed at midnight Eastern. New files are ready.'); open(); return; }
      D().toast('That did not go through. Try again in a moment.'); refreshSel();
    });
  }

  function unwait() {
    const fb = $('icpFile'); if (fb) { fb.classList.remove('wait'); fb.textContent = 'File it'; }
    document.querySelectorAll('#icpDesk .icpcard.filing').forEach(b => b.classList.remove('filing'));
  }

  // A wrong guess stamps REJECTED across the screen for a moment, wherever you are on the desk (7 Nov 2026).
  function rejectBanner(n) {
    let b = $('icpReject');
    if (!b) { b = document.createElement('div'); b.id = 'icpReject'; b.setAttribute('role', 'status'); document.body.appendChild(b); }
    b.innerHTML = `<b>REJECTED</b><small>${n >= 3 ? 'Three mistakes. The files close.' : n + ' of 3 mistakes'}</small>`;
    b.classList.remove('on'); void b.offsetWidth; b.classList.add('on');
    if (navigator.vibrate) try { navigator.vibrate([70, 50, 70]); } catch (e) {}
    clearTimeout(rejectBanner.t); rejectBanner.t = setTimeout(() => b.classList.remove('on'), 1800);
  }

  // ---------- pick a card ----------
  function confirmPick(i) {
    const c = P.cards[i], inf = info(c.id); if (!inf) return;
    const own = D().holdings().get(c.id);
    const living = c.v === 'living';
    const odds = P.practice ? 'Practice round: the card is yours, but it can\'t come Top Secret, and a duplicate pays no Intel.'
      : P.perfect ? 'A perfect solve: it comes Silver, Gold, or Top Secret.' : 'The finish is set by luck: Copper, Silver, Gold, or Top Secret.';
    const have = !own ? 'This card isn\'t in your dossier yet.' : 'You already hold this card. If the finish lands on one you hold, it turns into Intel like any duplicate.';
    D().sheet(`<div class="sheettop"><span class="howstamp">Code Room</span><button class="howx" data-close aria-label="Close">✕</button></div>
      <h2>Take ${esc(inf.short)}?</h2>
      <p class="sheetline">${esc(inf.kind === 'namethis' ? 'Name This' : 'No. ' + String(inf.num).padStart(3, '0'))}${living ? ' · Living Card' : ''}</p>
      <p class="sheetnote">${odds} ${have}</p>
      <button class="btn" id="icpTake">Take this card</button><button class="btn alt" data-close>Pick another</button>`);
    $('icpTake').onclick = () => {
      $('icpTake').disabled = true;
      D().api('intercept/claim', { day: P.day, index: i }).then(d => {
        D().closeSheet();
        P = d.puzzle;
        D().claimReveal(d); // the normal turn and reveal, then home (7 Nov 2026)
      }).catch(e => {
        D().closeSheet();
        D().toast(e.message === 'already claimed' ? 'You already picked today\'s card.' : e.message === 'not offered' ? 'Flash cards can\'t be picked.' : 'That did not go through. Try again in a moment.');
        open();
      });
    };
  }

  // ---------- leaving ----------
  function refreshHome() { D().refresh().catch(() => {}); }
  function home() { D().goHome(); }

  // ---------- the guided first puzzle ----------
  const GUIDE = [
    ['Four hidden links', 'These twelve files hide four links. Each link joins exactly three of them: a ship, a battle, a person, something in the photos.'],
    ['File three at a time', 'Tap three files you think belong together, then tap File it. Right, and they\'re clipped together with the link. Tap the magnifier on a card to see it full size.'],
    ['Three mistakes', 'A wrong guess gets a REJECTED stamp, and three stamps close the files. The date and series on a card are never the link.'],
  ];
  function maybeGuide() {
    if (D().seen('icpGuide')) return;
    let k = 0;
    const step = () => {
      const [h, p] = GUIDE[k];
      D().sheet(`<div class="sheettop"><span class="howstamp">Your first Code Room · ${k + 1} of ${GUIDE.length}</span><button class="howx" data-close aria-label="Close">✕</button></div>
        <h2>${h}</h2><p class="sheetnote">${p}</p>
        <button class="btn" id="icpGuideGo">${k < GUIDE.length - 1 ? 'Next' : 'Crack the files'}</button>`);
      $('icpGuideGo').onclick = () => { k++; if (k < GUIDE.length) step(); else { D().closeSheet(); D().mark('icpGuide'); } };
    };
    step();
    D().mark('icpGuide');
  }

  // ---------- share picture ----------
  async function paint(cv) {
    await Promise.all(['700 40px Oswald', '400 20px "Special Elite"'].map(f => document.fonts.load(f).catch(() => {})));
    const W = 1080, H = 1350, c = cv.getContext('2d');
    // Intercept's Night Desk (30 Oct 2026): the Declass share picture's desk, lit blue near the top.
    c.fillStyle = '#17140f'; c.fillRect(0, 0, W, H);
    const g = c.createRadialGradient(W / 2, H * 0.18, W * 0.1, W / 2, H * 0.2, H * 0.62); g.addColorStop(0, 'rgba(61,88,132,.26)'); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.fillRect(0, 0, W, H);
    c.globalAlpha = 0.05; c.fillStyle = '#EDE4CF'; for (let y = 0; y < H; y += 6) c.fillRect(0, y, W, 1); c.globalAlpha = 1;
    c.textAlign = 'center'; c.fillStyle = '#EDE4CF'; c.font = '700 84px Oswald'; c.fillText('CODE ROOM', W / 2, 112);
    c.fillStyle = '#b9ad92'; c.font = '400 30px "Special Elite"'; c.fillText('a Declass daily puzzle · ' + new Date(P.day + 'T12:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }), W / 2, 158);
    const solved = P.status === 'solved';
    const res = solved ? `CRACKED · ${P.score} OF 100 · ${P.mistakes === 0 ? 'NO MISTAKES' : P.mistakes + ' MISTAKE' + (P.mistakes > 1 ? 'S' : '')}` : `FILES CLOSED · ${P.found} OF 4 LINKS`;
    c.save(); c.font = '700 34px Oswald'; const rw = c.measureText(res).width; c.translate(W / 2, 222); c.rotate(-2 * Math.PI / 180);
    c.strokeStyle = solved ? '#7fa3dd' : '#d0574a'; c.fillStyle = c.strokeStyle; c.lineWidth = 4; c.strokeRect(-rw / 2 - 20, -36, rw + 40, 50); c.fillText(res, 0, 0); c.restore();
    const rows = P.groups, top = 280, rowH = 250, cw = 168, ch = cw * 1.25;
    const imgs = await Promise.all(rows.flatMap(r => r.idx.map(i => { const inf = info(P.cards[i].id); return inf ? D().loadImg(inf.img).catch(() => null) : Promise.resolve(null); })));
    rows.forEach((r, k) => {
      const y = top + k * rowH;
      c.globalAlpha = r.found ? 1 : 0.45;
      r.idx.forEach((_, j) => { const im = imgs[k * 3 + j]; const x = 48 + j * (cw - 22); c.save(); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 14; c.translate(x + cw / 2, y + ch / 2); c.rotate(((j - 1) * 3) * Math.PI / 180); if (im) c.drawImage(im, -cw / 2, -ch / 2, cw, ch); else { c.fillStyle = '#2a241e'; c.fillRect(-cw / 2, -ch / 2, cw, ch); } c.restore(); });
      // the typed label on a paper strip
      const lx = 440, lw = W - lx - 48;
      c.fillStyle = r.found ? '#EDE4CF' : '#6b6354'; c.fillRect(lx, y + 40, lw, 150);
      c.fillStyle = '#1A1612'; c.textAlign = 'left'; c.font = '400 30px "Special Elite"';
      const words = (r.found ? '' : 'Not found. ').concat(r.link).split(' '); let line = '', ly = y + 88;
      for (const w of words) { const tryl = line ? line + ' ' + w : w; if (c.measureText(tryl).width > lw - 40 && line) { c.fillText(line, lx + 20, ly); line = w; ly += 38; } else line = tryl; }
      c.fillText(line, lx + 20, ly);
      c.globalAlpha = 1;
    });
    c.textAlign = 'center'; c.fillStyle = '#EDE4CF'; c.font = '700 44px Oswald'; c.fillText('DECLASS', W / 2, 1290);
    c.fillStyle = '#c9bd9f'; c.font = '400 28px "Special Elite"'; c.fillText('a WW2 Dispatches game · ww2dispatches.com/declass', W / 2, 1326);
  }
  async function share() {
    const solved = P.status === 'solved';
    const text = solved
      ? `Cracked today's Code Room files: ${P.score} of 100, ${P.mistakes === 0 ? 'no mistakes' : P.mistakes + ' mistake' + (P.mistakes > 1 ? 's' : '')}. ww2dispatches.com/declass #Declass`
      : `Today's Code Room files beat me: ${P.found} of 4 links. ww2dispatches.com/declass #Declass`;
    if (navigator.clipboard) navigator.clipboard.writeText(text).catch(() => {});
    const cv = document.createElement('canvas'); cv.width = 1080; cv.height = 1350;
    let blob = null;
    try { await paint(cv); blob = await new Promise(r => cv.toBlob(r, 'image/png')); } catch (e) { blob = null; }
    const file = blob ? new File([blob], 'intercept.png', { type: 'image/png' }) : null;
    if (file && navigator.canShare && navigator.canShare({ files: [file] })) { navigator.share({ files: [file], text }).catch(() => {}); return; }
    if (blob) {
      const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'intercept.png';
      document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000);
      D().toast('Picture saved. The caption is copied, ready to paste.');
    } else D().toast('The caption is copied, ready to paste.');
  }

  // Done on the review: to the card pick if one is waiting, otherwise home (7 Nov 2026).
  function done() {
    if (P && P.status === 'solved' && P.canClaim) { stage = 'pick'; draw(); window.scrollTo(0, 0); D().sfx('slide'); return; }
    home();
  }
  // The Declass button only shows while the files are open; a finished puzzle leaves by Done.
  function leave() { home(); }
  window.Intercept = { tile, open, paint, _state: () => P };
  const back = document.getElementById('icpBack');
  if (back) back.onclick = leave;
  // close the full size view
  const z = document.getElementById('icpZoom');
  if (z) z.addEventListener('click', () => { z.hidden = true; });
})();
