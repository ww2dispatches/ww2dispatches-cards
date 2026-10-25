// Declass: a WW2 Dispatches game. The page talks to the server at /api/...; every pull is decided,
// numbered, signed, and saved there. Build session 4: landing, starter pack, save your dossier,
// home with today's files, choose an envelope, the opening, the cards, the dossier, the card view.
(function () {
  'use strict';
  const $ = id => document.getElementById(id);

  // ---------- tester key (private test): arrives once as ?key=..., remembered in this browser ----------
  const KEY_STORE = 'declass_key';
  let testerKey = '';
  try {
    const url = new URL(location.href), k = url.searchParams.get('key');
    if (k) { localStorage.setItem(KEY_STORE, k); url.searchParams.delete('key'); history.replaceState(null, '', url.pathname + url.search + url.hash); }
    testerKey = localStorage.getItem(KEY_STORE) || '';
  } catch (e) { testerKey = new URLSearchParams(location.search).get('key') || ''; }

  function api(path, body) {
    return fetch('/api/' + path, {
      method: body ? 'POST' : 'GET',
      headers: Object.assign({ 'x-declass-key': testerKey }, body ? { 'content-type': 'application/json' } : {}),
      body: body ? JSON.stringify(body) : undefined,
      credentials: 'same-origin',
    }).then(r => r.json().catch(() => ({})).then(d => { if (!r.ok) throw new Error(d.error || String(r.status)); return d; }));
  }

  // ---------- constants ----------
  const FIN = ['copper', 'silver', 'gold', 'topsecret'];
  const FNAME = { copper: 'Copper', silver: 'Silver', gold: 'Gold', topsecret: 'Top Secret' };
  const SERIES = [['battle', 'Battle Lines', '#B04A3E'], ['home', 'Home Front', '#5E6B3A'], ['blue', 'Blueprint', '#3D5884'], ['state', 'Statecraft', '#B8862B'], ['namethis', 'Name This', '#5B4B8A']];
  const ERAS = [['leadup', 'The lead up', '1933 to August 1939'], ['1939'], ['1940'], ['1941'], ['1942'], ['1943'], ['1944'], ['1945'], ['aftermath', 'The aftermath', 'September 1945 on']];
  const IC = { x: '<path d="M5 4l14 16M19 4L5 20"/>', instagram: '<rect x="4" y="4" width="16" height="16" rx="5"/><circle cx="12" cy="12" r="3.6"/><circle cx="17" cy="7" r=".6" fill="currentColor"/>', threads: '<path d="M16.5 11.5c-.5-3-2.5-4.5-5-4.5-3 0-5 2.3-5 5.5S8.5 18 12 18c3 0 5-1.6 5-4 0-2-1.6-3-3.8-3-2 0-3.2 1-3.2 2.3 0 1.2 1 2 2.3 2 2 0 3-1.6 3.2-4.3"/>', facebook: '<path d="M14 8h2V4.5h-2.5C11 4.5 10 6 10 8.3V10H8v3.4h2V20h3.4v-6.6H16l.5-3.4h-3.1V8.6c0-.4.2-.6.6-.6z"/>', youtube: '<rect x="3.5" y="6" width="17" height="12" rx="3.5"/><path d="M10.5 9.5v5l4.2-2.5z" fill="currentColor"/>', tiktok: '<path d="M13 4v10.5a3 3 0 1 1-3-3M13 4c.5 2.5 2.3 4 5 4"/>' };
  const PNAME = { x: 'X', instagram: 'Instagram', threads: 'Threads', facebook: 'Facebook', youtube: 'YouTube', tiktok: 'TikTok' };

  // ---------- data ----------
  let CFG = null, CAT = [], BYID = new Map(), ST = null;
  const DETAIL = new Map();
  const STARTER_STORE = 'declass_starter';
  let STARTER = null; // a pack opened before sign in: {token, pulls, revealed}
  try { STARTER = JSON.parse(localStorage.getItem(STARTER_STORE) || 'null'); } catch (e) {}
  function saveStarterLocal() { try { STARTER ? localStorage.setItem(STARTER_STORE, JSON.stringify(STARTER)) : localStorage.removeItem(STARTER_STORE); } catch (e) {} }

  const signedIn = () => Boolean(ST && ST.player);
  const myPulls = () => signedIn() ? ST.pulls : (STARTER ? STARTER.pulls : []);
  function setCatalog(cards) { CAT = cards; BYID = new Map(cards.map(c => [c.id, c])); }
  const refreshState = () => api('state').then(d => { ST = d; return d; });
  const refreshCatalog = () => api('catalog').then(d => setCatalog(d.cards));

  // ---------- helpers ----------
  const esc = t => String(t == null ? '' : t).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const pad3 = n => String(n).padStart(3, '0');
  const ser4 = n => String(n).padStart(4, '0');
  const ord = n => { const s = ['th', 'st', 'nd', 'rd'], v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); };
  const delay = ms => new Promise(r => setTimeout(r, ms));
  const etHour = iso => Number(new Date(iso).toLocaleString('en-US', { timeZone: 'America/New_York', hour: 'numeric', hourCycle: 'h23' }));
  const etTime = iso => new Date(iso).toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour: 'numeric', minute: '2-digit' }).replace('AM', 'A.M.').replace('PM', 'P.M.') + ' ET';
  const localTime = iso => new Date(iso).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  const localDayTime = iso => new Date(iso).toLocaleString([], { weekday: 'short', hour: 'numeric', minute: '2-digit' });
  const localDate = iso => new Date(iso).toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' });
  function leftText(iso) {
    const ms = Date.parse(iso) - Date.now();
    if (ms <= 0) return 'closing now';
    const h = Math.floor(ms / 3600000), m = Math.floor(ms % 3600000 / 60000);
    return h >= 24 ? Math.floor(h / 24) + ' day' + (h >= 48 ? 's' : '') + ' left' : (h ? h + 'h ' : '') + m + 'm left';
  }
  const label = info => info.kind === 'namethis' ? 'Name This' : 'No. ' + pad3(info.num);
  function slotName(key) {
    if (!key) return '';
    if (key.startsWith('d:')) return (etHour(key.slice(2)) < 12 ? 'Morning' : 'Evening') + ' envelope';
    if (key.startsWith('p:')) return 'Priority envelope';
    if (key.startsWith('c:')) return 'Commemorative file';
    if (key === 's:starter') return 'Starter pack';
    return 'Envelope';
  }
  function show(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.toggle('on', s.id === id));
    window.scrollTo(0, 0);
    renderGoogleButtons();
  }
  function toast(t) { const el = $('toast'); el.textContent = t; el.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => { el.hidden = true; }, 2800); }
  function nudge(el) { sfx('locked'); el.classList.remove('shake'); void el.offsetWidth; el.classList.add('shake'); }

  // What the player holds: card id -> {still: {finish: n}, living: {finish: n}, n}
  function holdings(pulls) {
    const m = new Map();
    for (const p of pulls) {
      if (!m.has(p.card)) m.set(p.card, { still: {}, living: {}, n: 0 });
      const h = m.get(p.card);
      h[p.variant][p.finish] = (h[p.variant][p.finish] || 0) + 1;
      h.n++;
    }
    return m;
  }
  function bestOf(h) {
    if (!h) return null;
    for (let i = FIN.length - 1; i >= 0; i--) for (const v of ['living', 'still']) if (h[v][FIN[i]]) return { variant: v, finish: FIN[i] };
    return null;
  }
  function bestFinish(h) { // the best finish across both variants, for grid borders
    if (!h) return null;
    for (let i = FIN.length - 1; i >= 0; i--) if (h.still[FIN[i]] || h.living[FIN[i]]) return FIN[i];
    return null;
  }

  // ---------- the light on gold and Top Secret (Card Finishes mockup) ----------
  let lightTouched = 0, lightT = 0;
  function setLight(x, y, manual) {
    if (manual) lightTouched = Date.now();
    const r = document.documentElement.style;
    r.setProperty('--ang', (135 + x * 60) + 'deg');
    r.setProperty('--ang2', (45 + y * 90) + 'deg');
    r.setProperty('--pos', (50 + x * 80) + '% ' + (50 + y * 80) + '%');
    r.setProperty('--gang', (118 + x * 50) + 'deg');
  }
  // A real mouse moves the light. On phones only a finger drag does: iPhone Safari sends a fake
  // mouse move before each tap, and if the page changes during it, Safari swallows the tap.
  document.addEventListener('pointermove', e => { if (e.pointerType === 'mouse') setLight(e.clientX / innerWidth - 0.5, e.clientY / innerHeight - 0.5, true); });
  document.addEventListener('touchmove', e => { const t = e.touches[0]; if (t) setLight(t.clientX / innerWidth - 0.5, t.clientY / innerHeight - 0.5, true); }, { passive: true });
  window.addEventListener('deviceorientation', e => { if (e.gamma != null) setLight(Math.max(-0.5, Math.min(0.5, e.gamma / 60)), Math.max(-0.5, Math.min(0.5, (e.beta - 45) / 60)), true); });
  (function idle() {
    if (!document.hidden && Date.now() - lightTouched > 1500) { lightT += 0.01; setLight(Math.sin(lightT) * 0.35, Math.cos(lightT * 0.7) * 0.35); }
    requestAnimationFrame(idle);
  })();

  // ---------- a card in its finish frame ----------
  function cardFace(info, finish, variant, serial, opts) {
    opts = opts || {};
    const living = variant === 'living' && info.filmMp4;
    const src = opts.puzzle && info.imgPuzzle ? info.imgPuzzle : info.img;
    const media = living
      ? `<video class="film" src="${esc(info.filmMp4)}" poster="${esc(info.filmPoster || info.img)}" muted loop playsinline preload="auto"${opts.autoplay ? ' autoplay' : ''}></video><button class="spk" type="button" aria-label="Film sound">🔈</button>`
      : `<img src="${esc(src)}" alt="${esc(info.short)}${info.kind === 'namethis' ? '' : ', ' + esc(info.title)}" draggable="false">`;
    return `<div class="cf f-${finish}"><div class="frame"><div class="card">${media}<span class="sheen"></span><span class="badge">Top Secret</span>${info.kind === 'namethis' ? '<span class="ansst">ANSWER</span>' : ''}</div><span class="corner c1"></span><span class="corner c2"></span><span class="corner c3"></span><span class="corner c4"></span><span class="serial">${serial ? 'Worldwide serial ' + ser4(serial) : ''}</span></div></div>`;
  }
  // Start a Living Card's film (muted). If the phone blocks it, show a play button.
  function startFilm(root, info) {
    const v = root.querySelector('video.film');
    if (!v) return;
    const spk = root.querySelector('.spk');
    if (spk) spk.onclick = e => {
      e.stopPropagation();
      if (!info.filmSound) { toast('This one is silent film.'); return; }
      v.muted = !v.muted; spk.textContent = v.muted ? '🔈' : '🔊';
      if (!v.muted) v.play().catch(() => {});
    };
    const p = v.play();
    if (p && p.catch) p.catch(() => {
      if (root.querySelector('.play')) return;
      const b = document.createElement('button');
      b.className = 'play'; b.type = 'button'; b.textContent = '▶'; b.setAttribute('aria-label', 'Play film');
      b.onclick = e => { e.stopPropagation(); v.play().then(() => b.remove()).catch(() => {}); };
      v.parentNode.appendChild(b);
    });
  }

  // ---------- envelopes (Declass mockup) ----------
  function envHTML(i, env) {
    const k = env.kind, pr = k === 'priority', st = k === 'starter', cm = k === 'commemorative';
    const c = cm ? ['#1d1a17', '#24201c', '#2a2520'] : pr ? ['#C9A774', '#C5A26E', '#CDAB79'] : ['#E8DFC7', '#E6DCC3', '#EAE1C9'];
    const lbl = cm ? 'THREE DAYS ONLY' : pr ? 'DEEP ARCHIVE' : st ? 'FIRST FILE' : env.deep ? 'DEEP ARCHIVE' : etTime(env.at).toUpperCase();
    const stamp = cm ? `<div class="prio">${esc(env.stamp)}</div><div class="lbl">COMMEMORATIVE FILE · ${lbl}<b>WW2 DISPATCHES</b></div>`
      : pr ? `<div class="prio">PRIORITY</div><div class="lbl">STREAK REWARD · ${lbl}<b>WW2 DISPATCHES</b></div>`
      : st ? `<div class="prio stp">STARTER PACK</div><div class="lbl">YOUR ${lbl} · FIVE CARDS<b>WW2 DISPATCHES</b></div>`
      : `<div class="lbl">INCOMING DISPATCH · ${esc(lbl)}<b>WW2 DISPATCHES</b></div>`;
    return `<svg class="body" viewBox="0 0 360 200" preserveAspectRatio="none" aria-hidden="true"><rect width="360" height="200" fill="${c[0]}"/><polygon points="0,0 180,126 0,200" fill="${c[1]}"/><polygon points="360,0 180,126 360,200" fill="${c[1]}"/><polygon points="0,200 180,126 360,200" fill="${c[2]}"/><polyline points="0,200 180,126 360,200" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.5"/></svg>
      <div class="flap"></div><div class="seal">SEALED<br>WW2</div><div class="no">${i ? 'No. ' + i + ' of 3' : ''}</div>${stamp}<div class="cstamp">CLASSIFIED</div><div class="dstamp">DECLASS</div><div class="edge"></div>`;
  }
  const envClass = k => k === 'priority' ? ' priority' : k === 'commemorative' ? ' commem' : '';

  // ---------- home ----------
  function slotButton(cls, title, sub, onclick) {
    const b = document.createElement('button');
    b.className = 'slotbtn ' + cls;
    b.innerHTML = `<b>${title}</b><span>${sub}</span>`;
    b.onclick = () => onclick(b);
    return b;
  }
  function renderHome() {
    let todayHasUpcoming = false;
    const p = ST && ST.player, files = $('files');
    files.innerHTML = '';
    const locked = signedIn() && ST.waiting.length > 0;
    const guard = (b, fn) => { if (locked) return nudge(b); fn(); };

    $('streakN').textContent = p ? p.streak : 0;
    $('streakHint').textContent = !p ? 'Sign in to start a streak'
      : p.streak ? (p.nextPriorityIn === 3 ? 'Priority envelope earned' : 'Priority envelope in ' + p.nextPriorityIn + ' day' + (p.nextPriorityIn > 1 ? 's' : ''))
      : 'Open an envelope to start';

    if (p) {
      if (locked) {
        const n = ST.waiting.length;
        files.appendChild(slotButton('pend', n + ' card' + (n > 1 ? 's' : '') + ' waiting to be turned', 'They are already in your dossier. Tap to see them.', resumeWaiting));
      }
      for (const e of ST.commemorative) {
        files.appendChild(slotButton('comm ' + (e.opened ? 'done' : locked ? 'locked' : 'live'), 'Commemorative file · ' + esc(e.name),
          e.opened ? 'Opened · back next commemorative day' : 'Everyone gets one · ' + leftText(e.closes),
          b => { if (!e.opened) guard(b, () => pick(e)); }));
      }
      if (!p.starterDone) {
        files.appendChild(slotButton('starter ' + (locked ? 'locked' : 'live'), 'Starter pack', 'Five cards, free: today\'s dispatch and one from each series',
          b => guard(b, () => pick({ kind: 'starter' }))));
      }
      if (ST.priority > 0) {
        files.appendChild(slotButton('prio ' + (locked ? 'locked' : 'live'), 'Priority envelope' + (ST.priority > 1 ? 's ×' + ST.priority : ''), 'Three cards from the deep archive · never expires',
          b => guard(b, () => pick({ kind: 'priority' }))));
      }
      // Today's files (option A, 25 Oct 2026): one row per envelope time today in the player's own
      // day, each not out yet, out, or opened. Yesterday's envelopes drop off once opened; one still
      // unopened gets a Last call row while its 24 hours run.
      const dayStart = new Date(); dayStart.setHours(0, 0, 0, 0);
      const dayEnd = new Date(dayStart.getTime()); dayEnd.setDate(dayEnd.getDate() + 1);
      const isToday = iso => { const x = Date.parse(iso); return x >= dayStart.getTime() && x < dayEnd.getTime(); };
      const slotTitle = at => (etHour(at) < 12 ? 'Morning' : 'Evening') + ' envelope';
      for (const e of ST.envelopes.filter(e => !isToday(e.at) && !e.opened)) {
        files.appendChild(slotButton(locked ? 'locked' : 'live', 'Last call · ' + (etHour(e.at) < 12 ? "Yesterday's morning" : "Yesterday's evening"),
          (e.deep ? 'Sunday deep archive · ' : '') + 'Closes ' + localTime(e.closes) + ' · ' + leftText(e.closes),
          b => guard(b, () => pick(e))));
      }
      const today = ST.envelopes.filter(e => isToday(e.at)).map(e => Object.assign({ out: true }, e))
        .concat((ST.upcoming || []).filter(u => isToday(u.at)).map(u => Object.assign({ out: false }, u)))
        .sort((a, b) => a.at.localeCompare(b.at));
      for (const e of today) {
        const deep = e.deep ? 'Sunday deep archive · ' : '';
        if (!e.out) {
          files.appendChild(slotButton('wait', slotTitle(e.at), deep + 'Arrives ' + localTime(e.at), () => {}));
          continue;
        }
        files.appendChild(slotButton(e.opened ? 'done' : locked ? 'locked' : 'live', slotTitle(e.at),
          e.opened ? deep + 'Opened · out since ' + localTime(e.at) : deep + 'Out since ' + localTime(e.at) + ' · ' + leftText(e.closes),
          b => { if (!e.opened) guard(b, () => pick(e)); }));
      }
      todayHasUpcoming = today.some(e => !e.out);
    }
    $('signBar').hidden = Boolean(p);
    $('signBar').querySelector('span').textContent = STARTER
      ? 'Your starter pack is waiting in this browser. Save your dossier to keep it and collect every day.'
      : 'Sign in to keep a dossier and open a new envelope file every day.';
    let nextText = '';
    if (ST && ST.next && !(signedIn() && todayHasUpcoming)) {
      const n = new Date(ST.next), tmr = new Date(); tmr.setDate(tmr.getDate() + 1);
      const when = n.toDateString() === new Date().toDateString() ? 'today at ' : n.toDateString() === tmr.toDateString() ? 'tomorrow at ' : n.toLocaleDateString([], { weekday: 'long' }) + ' at ';
      nextText = 'Next file arrives ' + when + localTime(ST.next);
    }
    $('nextFile').textContent = nextText;

    // the last envelope's cards
    const pulls = myPulls();
    let last = [];
    if (signedIn() && pulls.length) { const k = pulls[0].slot; last = pulls.filter(x => x.slot === k).slice().reverse(); }
    else if (STARTER) last = STARTER.pulls.filter((x, i) => STARTER.revealed[i]);
    $('recent').innerHTML = last.length ? `<h2>Last envelope <small>${esc(signedIn() ? slotName(last[0].slot) + ' · ' + localDate(last[0].at) : 'Starter pack')}</small></h2><div class="recent">${last.map(x => miniHTML(x.card, holdingsNow())).join('')}</div>` : '';
    wireMinis($('recent'), last.map(x => x.card));

    // dossier tiles
    const H = holdingsNow();
    const total = CAT.length, have = CAT.filter(c => H.has(c.id)).length;
    $('dossierSummary').textContent = `${have} of ${total} cards`;
    $('seriesTiles').innerHTML = SERIES.map(([k, name, col]) => {
      const all = CAT.filter(c => c.series === k), h = all.filter(c => H.has(c.id)).length;
      return `<button class="tile${k === 'namethis' ? ' wide' : ''}" data-series="${k}"><i style="background:${col}"></i><b>${name}</b><span>${h} of ${all.length}</span><div class="bar"><i style="width:${all.length ? h / all.length * 100 : 0}%"></i></div></button>`;
    }).join('');
    $('seriesTiles').insertAdjacentHTML('beforeend', '<button class="tile wide" id="tileSets" style="border-color:var(--navy)"><b>Sets</b><span>Monthly files and collections</span></button>');
    $('tileSets').onclick = renderSets;
    $('seriesTiles').querySelectorAll('[data-series]').forEach(b => { b.onclick = () => section('series', b.dataset.series); });
    $('yearTiles').innerHTML = ERAS.map(([k, name, span]) => {
      const all = CAT.filter(c => c.kind === 'dispatch' && c.era === k), h = all.filter(c => H.has(c.id)).length;
      return `<button class="tile" data-year="${k}" ${all.length ? '' : 'disabled'}><i style="background:var(--ink)"></i><b>${name || k}</b><span>${all.length ? h + ' of ' + all.length : 'None posted yet'}</span>${span ? `<span>${span}</span>` : ''}<div class="bar"><i style="width:${all.length ? h / all.length * 100 : 0}%"></i></div></button>`;
    }).join('');
    $('yearTiles').querySelectorAll('[data-year]').forEach(b => { b.onclick = () => section('year', b.dataset.year); });
    $('allSub').textContent = `${have} of ${total} cards`;
    $('footDelete').hidden = !p;
    $('footWho').innerHTML = p ? `File ${esc(p.fileNumber)} · <button id="signOut">Sign out</button>` : '';
    if (p) $('signOut').onclick = () => { try { google.accounts.id.disableAutoSelect(); } catch (e) {} api('auth/signout', {}).then(() => location.reload()); };
  }
  const holdingsNow = () => holdings(myPulls());

  // ---------- small cards in grids ----------
  function miniHTML(id, H) {
    const info = BYID.get(id);
    if (!info) return '';
    const h = H.get(id), best = bestFinish(h);
    const dots = `<div class="fd">${FIN.map(f => `<i class="f-${f}${h && (h.still[f] || h.living[f]) ? ' on' : ''}" title="${FNAME[f]}"></i>`).join('')}${info.hasFilm ? `<b class="${h && FIN.some(f => h.living[f]) ? 'on' : ''}" title="Living Card">▶</b>` : ''}</div>`;
    if (!best) return `<div class="mini sealed"><span class="thumb">?</span><span class="no">${esc(label(info))}</span><span class="nm">${esc(info.short)}</span>${dots}</div>`;
    return `<button class="mini" data-id="${esc(id)}"><img class="thumb f-${best}" loading="lazy" src="${esc(info.img)}" alt="${esc(info.short)}"><span class="no">${esc(label(info))}</span><span class="nm">${esc(info.short)}</span>${dots}</button>`;
  }
  function wireMinis(el, list) {
    el.querySelectorAll('.mini[data-id]').forEach(b => { b.onclick = () => view(b.dataset.id, list.filter((x, i, a) => holdingsNow().has(x) && a.indexOf(x) === i)); });
  }

  // ---------- sections ----------
  let allFilter = 'all', lastSection = null;
  function section(kind, key) {
    lastSection = [kind, key];
    const H = holdingsNow();
    let list, title;
    $('filters').hidden = kind !== 'all';
    if (kind === 'series') {
      list = CAT.filter(c => c.series === key);
      title = SERIES.find(s => s[0] === key)[1];
    } else if (kind === 'year') {
      list = CAT.filter(c => c.kind === 'dispatch' && c.era === key).sort((a, b) => a.date < b.date ? -1 : a.date > b.date ? 1 : 0);
      const e = ERAS.find(x => x[0] === key); title = e[1] || key;
    } else {
      const F = { all: () => true, missing: c => !H.has(c.id), living: c => c.hasFilm };
      SERIES.forEach(([k]) => { F[k] = c => c.series === k; });
      list = CAT.filter(F[allFilter]).slice().reverse();
      title = 'All cards';
      $('filters').innerHTML = [['all', 'All'], ['missing', 'Missing'], ...SERIES.map(s => [s[0], s[1]]), ['living', 'Has a Living Card']]
        .map(([k, l]) => `<button data-f="${k}" class="${k === allFilter ? 'on' : ''}">${l}</button>`).join('');
      $('filters').querySelectorAll('button').forEach(b => { b.onclick = () => { allFilter = b.dataset.f; section('all'); }; });
    }
    $('sectionTitle').textContent = title;
    const h = list.filter(c => H.has(c.id)).length;
    $('sectionSub').textContent = `${h} of ${list.length} cards · Swatches show the finishes you hold, ▶ a Living Card`;
    $('sectionGrid').innerHTML = list.length ? list.map(c => miniHTML(c.id, H)).join('') : '<p class="sub" style="grid-column:1/-1">Nothing here yet.</p>';
    wireMinis($('sectionGrid'), list.map(c => c.id));
    viewFrom = 'sSection';
    show('sSection');
  }
  $('backSection').onclick = () => { renderHome(); show('sHome'); };
  $('allBtn').onclick = () => { allFilter = 'all'; section('all'); };

  // ---------- choose your envelope ----------
  let cur = null;
  function pick(env) {
    cur = env;
    $('pickSub').textContent = env.kind === 'commemorative' ? `A commemorative file for ${env.name}. Everyone gets one. Choose the one you want.`
      : env.kind === 'priority' ? 'Three came in for your streak. Choose the one you want.'
      : env.kind === 'starter' ? 'Your first file. Three came in. Choose the one you want.'
      : 'Three came in with this dispatch. Choose the one you want.';
    $('backPick').onclick = () => show(env.kind === 'starter' && !signedIn() ? 'sLanding' : 'sHome');
    const st = $('stack'); st.innerHTML = '';
    for (let i = 1; i <= 3; i++) {
      const e = document.createElement('div');
      e.className = 'env' + envClass(env.kind); e.tabIndex = 0; e.setAttribute('role', 'button'); e.setAttribute('aria-label', 'Sealed envelope ' + i);
      e.innerHTML = envHTML(i, env);
      e.onclick = () => chosen(i);
      e.onkeydown = ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); chosen(i); } };
      st.appendChild(e);
    }
    show('sPick');
  }

  // ---------- the opening ----------
  let busy = false, pendingTeletype = false;
  function chosen(i) {
    if (busy) return;
    busy = true;
    const env = cur;
    const req = env.kind === 'starter' ? api('starter', {}) : api('open', { slot: env.kind === 'priority' ? 'priority' : env.key });
    const before = holdingsNow();
    const b = $('bigEnv');
    b.className = 'big';
    b.innerHTML = `<div class="env${envClass(env.kind)}">${envHTML(i, env)}</div><div class="cardsout"><i></i><i></i><i></i></div>`;
    $('tearing').textContent = env.kind === 'commemorative' ? (env.title || env.stamp) : 'Declassifying…';
    duckMusic(true); sfx('slide'); sfx('stampA', 0.25); sfx('seal', 0.95);
    $('tearing').classList.toggle('goldt', env.kind === 'commemorative');
    show('sOpen');
    // preload the pictures (and films) as soon as the server answers
    req.then(d => d.pulls.forEach(p => { if (p.cardInfo) { new Image().src = p.cardInfo.img; if (p.variant === 'living' && p.cardInfo.filmMp4) { const v = document.createElement('video'); v.preload = 'auto'; v.muted = true; v.src = p.cardInfo.filmMp4; } } })).catch(() => {});
    setTimeout(() => b.classList.add('stamp'), 250);
    setTimeout(() => { b.classList.add('go'); $('tearing').textContent = env.kind === 'starter' ? 'Five cards inside.' : env.kind === 'commemorative' ? (env.title || env.stamp) : 'Three cards inside.'; }, 950);
    setTimeout(() => b.classList.add('fade'), 2100);
    Promise.all([req, delay(2850)]).then(([d]) => {
      busy = false;
      if (env.kind === 'starter' && !signedIn()) {
        STARTER = { token: d.token, pulls: d.pulls, revealed: d.pulls.map(() => false) };
        saveStarterLocal();
        startCards(d.pulls, 'starterLocal', before, env);
      } else {
        startCards(d.pulls, 'server', before, env);
        if (d.player && ST) ST.player = d.player;
        pendingTeletype = Boolean(d.earnedPriority);
      }
    }).catch(err => {
      busy = false;
      const msg = err.message;
      refreshState().then(() => {
        if (msg === 'cards waiting' && ST.waiting.length) return resumeWaiting();
        renderHome(); show(signedIn() || STARTER ? 'sHome' : 'sLanding');
        toast(msg === 'already opened' ? 'You already opened that one.' : msg === 'not available' ? 'That envelope is no longer available.' : 'Something went wrong. Try again in a moment.');
      }).catch(() => { show('sHome'); toast('Something went wrong. Try again in a moment.'); });
    });
  }

  // ---------- the cards ----------
  let pulls = [], revealed = [], answered = [], idx = 0, cardMode = 'server', cardEnv = null, tags = [];
  function computeTags(list, before) {
    const run = new Map();
    before.forEach((h, k) => run.set(k, { still: Object.assign({}, h.still), living: Object.assign({}, h.living) }));
    return list.map(p => {
      const h = run.get(p.card) || { still: {}, living: {} };
      let tag;
      if (p.variant === 'living') tag = !FIN.some(f => h.living[f]) ? ['live', 'LIVING CARD'] : !h.living[p.finish] ? ['slot', 'NEW FINISH'] : ['dup', 'DUPLICATE'];
      else tag = !FIN.some(f => h.still[f] || h.living[f]) ? ['new', 'NEW CARD'] : !h.still[p.finish] ? ['slot', 'NEW FINISH'] : ['dup', 'DUPLICATE'];
      h[p.variant][p.finish] = (h[p.variant][p.finish] || 0) + 1;
      run.set(p.card, h);
      return tag;
    });
  }
  function startCards(list, mode, before, env) {
    pulls = list; cardMode = mode; cardEnv = env || null;
    revealed = mode === 'starterLocal' ? STARTER.revealed.slice() : list.map(() => false);
    answered = list.map(() => false);
    tags = computeTags(list, before || new Map());
    idx = Math.max(0, revealed.indexOf(false));
    renderCard();
    show('sCards');
  }
  function backText(p, i) {
    const k = (cardEnv && cardEnv.kind) || (p.slot && p.slot.startsWith('p:') ? 'priority' : p.slot && p.slot.startsWith('c:') ? 'commemorative' : p.slot === 's:starter' ? 'starter' : 'daily');
    const first = i === 0 && (!p.slot || p.slot.startsWith('d:') || p.slot === 's:starter');
    if (k === 'priority' || k === 'commemorative') return 'From the deep archive';
    if (k === 'starter') return first ? "Today's dispatch" : 'Your starter pack';
    if (first && p.cardInfo && p.cardInfo.kind === 'dispatch' && p.variant === 'still' && i === 0) return "Today's dispatch";
    return cardEnv && cardEnv.deep ? 'From the deep archive' : 'From the archive';
  }
  function renderCard(dir) {
    const p = pulls[idx], info = p.cardInfo;
    $('count').textContent = `Card ${idx + 1} of ${pulls.length}`;
    const tag = tags[idx];
    $('stage').innerHTML = `<div class="flip${revealed[idx] ? ' up' : ''}" id="flip"><div class="face backf"><div class="badge">WW2</div><small>${esc(backText(p, idx))}</small></div><div class="face frontf">${tag ? `<span class="tag ${tag[0]}">${tag[1]}</span>` : ''}${info ? cardFace(info, p.finish, p.variant, p.serial, { puzzle: info.kind === 'namethis' }) : '<p class="sub">This card has left the archive.</p>'}</div></div>`;
    const f = $('flip');
    if (dir) { f.classList.add('in'); requestAnimationFrame(() => requestAnimationFrame(() => f.classList.remove('in'))); }
    f.onclick = reveal;
    if (revealed[idx] && info && p.variant === 'living') startFilm(f, info);
    $('hint').innerHTML = !revealed[idx] ? 'Tap to turn it over' : hintAfter(p, idx);
    $('prevBtn').disabled = idx === 0;
    $('nextBtn').disabled = !revealed[idx] || idx === pulls.length - 1;
    $('dots').innerHTML = pulls.map((_, i) => `<i class="${i === idx ? 'cur' : ''}"></i>`).join('');
    $('summary').hidden = !(revealed.every(Boolean) && cardMode !== 'starterLocal');
    if (!$('summary').hidden) renderSummary();
  }
  function hintAfter(p, i) {
    const info = p.cardInfo || {};
    if (info.kind === 'namethis') return answered[i] ? `<span class="answer">Answer: ${esc(info.answer)}</span>` : 'Can you name it? Tap to reveal the answer.';
    if (p.finish === 'topsecret' && p.serial) return `<b>The ${ord(p.serial)} Top Secret ${p.variant === 'living' ? 'living ' : ''}${esc(info.short)} pulled anywhere in the world.</b>`;
    return i < pulls.length - 1 ? 'Swipe or tap Next' : "That's the envelope.";
  }
  function glow(f) { if (f === 'copper') return; const g = $('glow'); g.className = 'glow'; void g.offsetWidth; g.className = 'glow ' + f; }
  function reveal() {
    const p = pulls[idx];
    if (revealed[idx]) { answerNT(); return; }
    revealed[idx] = true;
    glow(p.finish);
    sfx(FINISH_SOUND[p.finish][p.variant === 'living' ? 1 : 0]);
    $('flip').classList.add('up');
    if (p.cardInfo && p.variant === 'living') startFilm($('flip'), p.cardInfo);
    if (cardMode === 'starterLocal') { STARTER.revealed = revealed.slice(); saveStarterLocal(); }
    else if (p.id) api('turn', { ids: [p.id] }).catch(() => {});
    $('hint').innerHTML = hintAfter(p, idx);
    maybeTiltPrompt(p.finish);
    $('nextBtn').disabled = idx === pulls.length - 1;
    if (revealed.every(Boolean)) {
      if (cardMode === 'starterLocal') { $('hint').textContent = "That's your starter pack."; setTimeout(showSave, 1100); return; }
      $('summary').hidden = false; renderSummary();
    }
  }
  function answerNT() {
    const p = pulls[idx];
    if (!p.cardInfo || p.cardInfo.kind !== 'namethis' || answered[idx]) return;
    answered[idx] = true;
    sfx('stampA');
    const st = document.querySelector('#flip .ansst');
    if (st) { st.classList.remove('hit'); void st.offsetWidth; st.classList.add('hit'); }
    if (p.cardInfo.img && p.cardInfo.img !== p.cardInfo.imgPuzzle) { const im = document.querySelector('#flip .card img'); if (im) setTimeout(() => { im.src = p.cardInfo.img; }, 250); }
    $('hint').innerHTML = hintAfter(p, idx);
  }
  function renderSummary() {
    const H = holdingsNow();
    const ids = pulls.map(p => p.card);
    $('summaryRow').innerHTML = pulls.slice(0, 3).map(p => miniHTML(p.card, H)).join('');
    wireMinis($('summaryRow'), ids);
  }
  function go(n) {
    if (n < 0 || n >= pulls.length) return;
    if (n > idx && !revealed[idx]) return;
    const p = pulls[idx];
    if (p && p.cardInfo && p.cardInfo.kind === 'namethis') answered[idx] = true;
    $('flip').classList.add('out');
    document.querySelectorAll('.tiltask').forEach(el => el.remove());
    setTimeout(() => { idx = n; renderCard(true); }, 220);
  }
  $('nextBtn').onclick = () => go(idx + 1);
  $('prevBtn').onclick = () => go(idx - 1);
  function swipe(el, left, right) {
    let sx = null;
    el.addEventListener('touchstart', e => { sx = e.touches[0].clientX; }, { passive: true });
    el.addEventListener('touchend', e => { if (sx === null) return; const dx = e.changedTouches[0].clientX - sx; sx = null; if (Math.abs(dx) > 50) (dx < 0 ? left : right)(); });
  }
  swipe($('viewer'), () => go(idx + 1), () => go(idx - 1));
  document.addEventListener('keydown', e => {
    if (!$('sCards').classList.contains('on')) return;
    if (e.key === 'ArrowRight') go(idx + 1);
    if (e.key === 'ArrowLeft') go(idx - 1);
    if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); reveal(); }
  });
  function leaveCards() {
    document.querySelectorAll('#stage video').forEach(v => v.pause());
    document.querySelectorAll('.tiltask').forEach(el => el.remove());
    duckMusic(false);
    if (pendingTeletype) { pendingTeletype = false; setTimeout(() => sfx('teletype'), 500); }
    if (cardMode === 'starterLocal') {
      if (revealed.every(Boolean) && !signedIn()) return showSave();
      renderHome(); return show('sHome');
    }
    Promise.all([refreshState(), refreshCatalog()]).then(() => { renderHome(); show('sHome'); }).catch(() => { renderHome(); show('sHome'); });
  }
  $('doneBtn').onclick = leaveCards;
  $('backCards').onclick = leaveCards;
  function resumeWaiting() { startCards(ST.waiting, 'server', holdings(ST.pulls.filter(p => p.turned)), null); }

  // ---------- save your dossier ----------
  function showSave() {
    const H = holdingsNow();
    $('saveGrid').innerHTML = STARTER ? STARTER.pulls.map(p => miniHTML(p.card, H)).join('') : '';
    $('saveGrid').querySelectorAll('button').forEach(b => { b.disabled = true; b.style.cursor = 'default'; });
    show('sSave');
  }
  $('skipSave').onclick = () => { renderHome(); show('sHome'); toast('Your starter pack is saved in this browser for now.'); };

  // ---------- Google sign in ----------
  let gisReady = false;
  function loadGoogle() {
    if (!CFG || !CFG.googleClientId || document.getElementById('gsi')) return;
    const s = document.createElement('script');
    s.id = 'gsi'; s.src = 'https://accounts.google.com/gsi/client'; s.async = true;
    s.onload = () => {
      if (!window.google || !google.accounts) return;
      google.accounts.id.initialize({ client_id: CFG.googleClientId, callback: onCredential });
      gisReady = true; renderGoogleButtons();
    };
    document.head.appendChild(s);
  }
  function renderGoogleButtons() {
    if (!gisReady) return;
    ['gLand', 'gSave', 'gHome'].forEach(id => {
      const el = $(id);
      if (!el || el.dataset.done || !el.offsetParent) return;
      google.accounts.id.renderButton(el, { theme: 'outline', size: 'large', shape: 'rectangular', text: 'signin_with', width: 280 });
      el.dataset.done = '1';
    });
  }
  function onCredential(res) {
    const hadStarter = Boolean(STARTER);
    api('auth/google', { credential: res.credential, starter: STARTER ? STARTER.token : undefined })
      .then(d => {
        if (d.starterSaved || (d.player && d.player.starterDone)) { STARTER = null; saveStarterLocal(); }
        return refreshState().then(() => d);
      })
      .then(d => {
        renderHome(); show('sHome');
        toast(d.starterSaved ? "Dossier saved. Today's files are ready." : hadStarter ? 'Welcome back. Your dossier is loaded.' : 'Signed in. Your dossier is loaded.');
      })
      .catch(e => toast('Sign in did not work (' + e.message + ').'));
  }

  // ---------- card view ----------
  let viewList = [], vi = 0, viewSel = null, viewFrom = 'sHome';
  function view(id, list) {
    viewList = list && list.length ? list : [id];
    vi = Math.max(0, viewList.indexOf(id));
    viewSel = null;
    if ($('sSection').classList.contains('on')) viewFrom = 'sSection';
    else if ($('sCards').classList.contains('on')) viewFrom = 'sCards';
    else viewFrom = 'sHome';
    renderView();
    show('sView');
  }
  function serialFor(pl, id, variant, finish) {
    const p = pl.find(x => x.card === id && x.variant === variant && x.finish === finish && x.serial);
    return p ? p.serial : null;
  }
  function renderView() {
    const id = viewList[vi], info = BYID.get(id), pl = myPulls(), h = holdings(pl).get(id);
    if (!info || !h) return;
    if (!viewSel || !h[viewSel.variant][viewSel.finish]) viewSel = bestOf(h);
    $('viewCount').textContent = info.kind === 'namethis' ? 'Name This · ' + info.short : `Dispatch No. ${pad3(info.num)} · ${info.seriesName}`;
    document.querySelectorAll('#stage2 video').forEach(v => v.pause());
    $('stage2').innerHTML = cardFace(info, viewSel.finish, viewSel.variant, serialFor(pl, id, viewSel.variant, viewSel.finish), { autoplay: true });
    if (viewSel.variant === 'living') startFilm($('stage2'), info);
    $('viewPos').textContent = `${vi + 1} of ${viewList.length}`;
    $('vPrev').disabled = vi === 0; $('vNext').disabled = vi === viewList.length - 1;
    const row = (variant, lbl) => `<div class="rowlbl">${lbl}</div>` + FIN.map(f => {
      const n = h[variant][f] || 0;
      return n ? `<button class="s4 f-${f}${variant === viewSel.variant && f === viewSel.finish ? ' cur' : ''}" data-v="${variant}" data-f="${f}">${FNAME[f]}<small>×${n}</small></button>` : '<div class="s4 off">?<small>Sealed</small></div>';
    }).join('');
    $('slots4').innerHTML = row('still', 'Still') + (info.hasFilm ? row('living', 'Living Card') : '');
    $('slots4').querySelectorAll('button.s4').forEach(b => { b.onclick = () => { viewSel = { variant: b.dataset.v, finish: b.dataset.f }; renderView(); }; });
    const mine = pl.filter(p => p.card === id).slice().sort((a, b) => (b.at || '').localeCompare(a.at || ''));
    $('history').innerHTML = `<h3>Pulled ${mine.length} time${mine.length === 1 ? '' : 's'}</h3><ul>${mine.map(p => `<li><span>${p.at ? esc(localDate(p.at)) + ' · ' : ''}${esc(slotName(p.slot) || 'Starter pack')}${p.variant === 'living' ? ' · ▶ living' : ''}</span><span class="fin f-${p.finish}">${FNAME[p.finish]}${p.serial ? ' · Serial ' + ser4(p.serial) : ''}</span></li>`).join('')}</ul>`;
    renderText(info, h);
  }
  function renderText(info, h) {
    const holdsLiving = FIN.some(f => h.living[f]);
    const paint = d => {
      if (viewList[vi] !== info.id) return;
      const L = d.links || {}, F = (d.film && d.film.links) || {};
      const icon = (k, u) => u ? `<a href="${esc(u)}" target="_blank" rel="noopener" title="${PNAME[k]}" aria-label="${PNAME[k]}"><svg viewBox="0 0 24 24">${IC[k]}</svg></a>` : '';
      const cardRow = ['x', 'instagram', 'threads', 'facebook'].map(k => icon(k, L[k])).join('');
      const filmRow = ['youtube', 'tiktok', 'x', 'instagram', 'threads', 'facebook'].map(k => icon(k, F[k])).join('');
      const paras = String(d.story || '').split(/\n\s*\n/).filter(Boolean);
      let s = `<div class="kick">${info.kind === 'namethis' ? 'NAME THIS' : 'DISPATCH ' + pad3(info.num) + ' · ' + esc(info.seriesName.toUpperCase())} · ${esc(info.date)}${info.place ? ' · ' + esc(info.place.toUpperCase()) : ''}</div><h3>${esc(info.title)}</h3>`;
      if (info.kind === 'namethis' && d.clue) s += `<p class="ntclue">The clue was: ${esc(d.clue)}</p>`;
      if (paras.length) s += `<div class="story clip" id="ctStory">${paras.map(x => `<p>${esc(x)}</p>`).join('')}</div>` + (paras.length > 1 ? '<button class="more" id="ctMore">Read the full dispatch</button>' : '');
      if (d.photoCredit) s += `<h4>The photo</h4><p class="m">${esc(d.photoCredit)}${d.photoUrl ? ` <a href="${esc(d.photoUrl)}" target="_blank" rel="noopener">Source</a>` : ''}</p>`;
      if (d.film && holdsLiving) s += `<h4>The film</h4><p class="m">${esc(d.film.caption)}${d.film.sourceUrl ? ` <a href="${esc(d.film.sourceUrl)}" target="_blank" rel="noopener">National Archives</a>` : ''}</p>`;
      if (d.sources && d.sources.length) s += `<h4>Sources</h4><p class="m">${d.sources.map(x => `<a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.title)}</a>`).join('<br>')}</p>`;
      if (cardRow || filmRow) {
        s += '<h4>See the original posts</h4>';
        if (cardRow) s += `<div class="prow"><span>Card</span><div class="icons">${cardRow}</div></div>`;
        if (filmRow) { s += `<div class="prow"><span>Film</span><div class="icons">${filmRow}</div></div>`; if (!holdsLiving) s += '<div class="notyet">Living Card not yet pulled</div>'; }
      } else s += '<h4>See the original posts</h4><p class="m">Links appear here once the posts go out.</p>';
      $('ctext').innerHTML = s;
      const mb = $('ctMore');
      if (mb) mb.onclick = () => { const st = $('ctStory'); st.classList.toggle('clip'); mb.textContent = st.classList.contains('clip') ? 'Read the full dispatch' : 'Show less'; };
    };
    if (DETAIL.has(info.id)) return paint(DETAIL.get(info.id));
    $('ctext').innerHTML = '<p class="m">Loading the file…</p>';
    api('card?id=' + encodeURIComponent(info.id)).then(d => { DETAIL.set(info.id, d.card); paint(d.card); }).catch(() => { $('ctext').innerHTML = ''; });
  }
  $('vPrev').onclick = () => { if (vi > 0) { vi--; viewSel = null; renderView(); } };
  $('vNext').onclick = () => { if (vi < viewList.length - 1) { vi++; viewSel = null; renderView(); } };
  swipe($('viewer2'), () => $('vNext').click(), () => $('vPrev').click());
  $('backView').onclick = () => {
    document.querySelectorAll('#stage2 video').forEach(v => v.pause());
    if (viewFrom === 'sSection' && lastSection) section(lastSection[0], lastSection[1]);
    else if (viewFrom === 'sCards') show('sCards');
    else { renderHome(); show('sHome'); }
  };

  // ---------- How to play ----------
  function openHow() { $('how').hidden = false; document.body.style.overflow = 'hidden'; $('how').scrollTop = 0; }
  function closeHow() { $('how').hidden = true; document.body.style.overflow = ''; }
  document.querySelectorAll('[data-how]').forEach(b => { b.onclick = openHow; });
  $('howGo').onclick = closeHow; $('howX').onclick = closeHow;
  $('how').addEventListener('click', e => { if (e.target.id === 'how') closeHow(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !$('how').hidden) closeHow(); });

  // ---------- landing ----------
  $('landEnv').innerHTML = `<div class="env">${envHTML(0, { kind: 'starter' })}</div>`;
  const openStarter = () => pick({ kind: 'starter' });
  $('openStarter').onclick = openStarter;
  $('landEnv').onclick = () => { sfx('rustle'); setTimeout(openStarter, 250); };
  $('landEnv').onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openStarter(); } };

  // ---------- sound effects (made live in the browser) and music (Declass Sound Kit) ----------
  const SNDKEY = 'declass-sound';
  const SND = { sfx: true, music: true };
  try { Object.assign(SND, JSON.parse(localStorage.getItem(SNDKEY) || '{}')); } catch (e) {}
  let actx = null, master = null, sfxGain = null, nbuf = null;
  function ac() {
    if (!actx) {
      actx = new (window.AudioContext || window.webkitAudioContext)();
      master = actx.createGain(); master.gain.value = 0.8; master.connect(actx.destination);
      sfxGain = actx.createGain(); sfxGain.gain.value = SND.sfx ? 1 : 0; sfxGain.connect(master);
    }
    if (actx.state === 'suspended') actx.resume();
    return actx;
  }
  function noise() { if (!nbuf) { const c = ac(); nbuf = c.createBuffer(1, c.sampleRate * 2, c.sampleRate); const d = nbuf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; } return nbuf; }
  function genv(g, t, a, peak, dec) { g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(peak, t + a); g.gain.exponentialRampToValueAtTime(0.0001, t + a + dec); }
  function nz(t, dur, type, freq, q, peak, attack) { const c = ac(); const s = c.createBufferSource(); s.buffer = noise(); const f = c.createBiquadFilter(); f.type = type; f.frequency.value = freq; f.Q.value = q || 1; const g = c.createGain(); genv(g, t, attack || 0.002, peak, dur); s.connect(f).connect(g).connect(sfxGain); s.start(t, Math.random()); s.stop(t + dur + 0.1); return { f, g, s }; }
  function tone(t, freq, dur, type, peak, attack, endFreq) { const c = ac(); const o = c.createOscillator(); o.type = type || 'sine'; o.frequency.setValueAtTime(freq, t); if (endFreq) o.frequency.exponentialRampToValueAtTime(endFreq, t + dur); const g = c.createGain(); genv(g, t, attack || 0.004, peak, dur); o.connect(g).connect(sfxGain); o.start(t); o.stop(t + dur + 0.1); return o; }
  function bell(t, f, dur, peak) { [[1, 1], [2.76, 0.5], [5.4, 0.25], [8.9, 0.12]].forEach(([m, a]) => tone(t, f * m, dur * (1 / m ** 0.3), 'sine', peak * a, 0.003)); }
  function chime(t, f, dur, peak) { [[1, 1], [2, 0.35], [3, 0.12]].forEach(([m, a]) => tone(t, f * m, dur, 'sine', peak * a, 0.005)); }
  const Sx = {
    stampA(t) { tone(t, 140, 0.18, 'sine', 0.9, 0.002, 45); nz(t, 0.09, 'lowpass', 900, 0.7, 0.8); nz(t + 0.01, 0.05, 'bandpass', 2200, 1.2, 0.25); },
    seal(t) { for (let i = 0; i < 5; i++) nz(t + i * 0.018 + Math.random() * 0.01, 0.012, 'bandpass', 3000 + Math.random() * 2500, 4, 0.5); const r = nz(t + 0.12, 0.38, 'bandpass', 2400, 0.6, 0.35, 0.03); r.f.frequency.setValueAtTime(1600, t + 0.12); r.f.frequency.linearRampToValueAtTime(3800, t + 0.5); },
    slide(t) { const r = nz(t, 0.26, 'bandpass', 1200, 0.8, 0.28, 0.06); r.f.frequency.setValueAtTime(800, t); r.f.frequency.linearRampToValueAtTime(2000, t + 0.26); },
    snapA(t) { nz(t, 0.025, 'highpass', 2500, 0.7, 0.8); tone(t, 900, 0.03, 'triangle', 0.15, 0.001, 500); },
    silverB(t) { Sx.snapA(t); [1318.5, 1567.98, 1975.5].forEach((f, i) => chime(t + 0.04 + i * 0.05, f, 0.6, 0.12)); },
    goldA(t) { Sx.snapA(t); [1046.5, 1318.5, 1567.98, 2093].forEach((f, i) => chime(t + 0.05 + i * 0.09, f, 0.9, 0.18)); },
    tsC(t) {
      Sx.snapA(t); let x = t + 0.15;
      for (let i = 0; i < 8; i++) { nz(x, 0.012, 'bandpass', 2600, 3, 0.55); tone(x, 1800, 0.01, 'square', 0.06, 0.001); x += 0.06 - i * 0.004; }
      const sw = nz(x, 0.55, 'bandpass', 500, 2, 0.35, 0.4); sw.f.frequency.setValueAtTime(400, x); sw.f.frequency.exponentialRampToValueAtTime(5000, x + 0.55);
      const hit = x + 0.58; tone(hit, 90, 0.5, 'sine', 0.7, 0.003, 45); nz(hit, 0.25, 'lowpass', 1200, 0.7, 0.5);
      [261.63, 329.63, 392, 523.25, 659.25].forEach(f => { tone(hit, f, 1.8, 'sawtooth', 0.045, 0.03); tone(hit, f * 1.003, 1.8, 'sawtooth', 0.035, 0.03); });
      bell(hit + 0.05, 1046.5, 2.2, 0.32);
      for (let i = 0; i < 14; i++) chime(hit + 0.25 + i * 0.07, [2093, 2637, 3136, 2349, 2794][i % 5], 0.5, 0.07 * (1 - i / 16));
    },
    lCopper(t) { Sx.snapA(t); Sx.projector(t + 0.12, 0.75); },
    lSilver(t) { Sx.silverB(t); Sx.projector(t + 0.35, 0.7); },
    lGold(t) { Sx.goldA(t); Sx.projector(t + 0.6, 0.7); },
    lTS(t) { Sx.tsC(t); Sx.projector(t + 2.0, 0.65); },
    projector(t, vol) {
      vol = vol || 1; const c = ac(); const D = 3.2;
      const s = c.createBufferSource(); s.buffer = noise(); const f = c.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 650; const g = c.createGain();
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.22 * vol, t + 0.6); g.gain.setValueAtTime(0.22 * vol, t + D - 0.7); g.gain.exponentialRampToValueAtTime(0.0001, t + D);
      s.connect(f).connect(g).connect(sfxGain); s.start(t, Math.random()); s.stop(t + D + 0.1);
      const lfo = c.createOscillator(); lfo.frequency.setValueAtTime(6, t); lfo.frequency.linearRampToValueAtTime(24, t + 1); const lg = c.createGain(); lg.gain.value = 0.08; lfo.connect(lg).connect(g.gain); lfo.start(t); lfo.stop(t + D);
      const m = c.createOscillator(); m.type = 'sawtooth'; m.frequency.setValueAtTime(45, t); m.frequency.exponentialRampToValueAtTime(96, t + 1); const mg = c.createGain();
      mg.gain.setValueAtTime(0.0001, t); mg.gain.exponentialRampToValueAtTime(0.035 * vol, t + 0.7); mg.gain.setValueAtTime(0.035 * vol, t + D - 0.7); mg.gain.exponentialRampToValueAtTime(0.0001, t + D); m.connect(mg).connect(sfxGain); m.start(t); m.stop(t + D + 0.1);
      let x = t + 0.2, gap = 0.14; while (x < t + D - 0.3) { nz(x, 0.007, 'bandpass', 3200, 4, 0.11 * vol); x += gap; gap = Math.max(0.042, gap * 0.9); }
    },
    rustle(t) { for (let i = 0; i < 6; i++) nz(t + i * 0.05 + Math.random() * 0.03, 0.06, 'bandpass', 1500 + Math.random() * 2500, 0.9, 0.18, 0.01); },
    teletype(t) { for (let i = 0; i < 9; i++) nz(t + i * 0.055 + Math.random() * 0.012, 0.018, 'bandpass', 2000 + Math.random() * 1500, 2.5, 0.45); bell(t + 0.58, 1975.5, 1.1, 0.25); },
    locked(t) { tone(t, 160, 0.08, 'sine', 0.35, 0.002, 110); nz(t, 0.03, 'lowpass', 600, 0.8, 0.25); },
  };
  function sfx(k, d) { if (!SND.sfx) return; try { const c = ac(); Sx[k](c.currentTime + 0.02 + (d || 0)); } catch (e) {} }
  const FINISH_SOUND = { copper: ['snapA', 'lCopper'], silver: ['silverB', 'lSilver'], gold: ['goldA', 'lGold'], topsecret: ['tsC', 'lTS'] };
  let audio = null, duck = null, musicStarted = false;
  function musicNode() {
    ac();
    if (!audio) {
      audio = new Audio('/declass/theme.mp3'); audio.loop = true; audio.preload = 'auto';
      try {
        const src = actx.createMediaElementSource(audio);
        duck = actx.createGain(); const mg = actx.createGain(); mg.gain.value = 0.35;
        src.connect(duck).connect(mg).connect(master);
      } catch (e) { audio.volume = 0.35; }
    }
  }
  // iPhone browsers only let audio start on a finished tap, so keep trying on each tap until it plays.
  let musicTrying = false;
  function startMusic() {
    if (!SND.music || musicTrying) return;
    musicNode();
    musicTrying = true;
    const p = audio.play();
    if (p && p.then) p.then(() => { musicStarted = true; musicTrying = false; }).catch(() => { musicTrying = false; });
    else { musicStarted = true; musicTrying = false; }
  }
  function stopMusic() { if (audio) audio.pause(); musicStarted = false; }
  function duckMusic(down) {
    if (!duck) return;
    const t = actx.currentTime; duck.gain.cancelScheduledValues(t); duck.gain.setValueAtTime(duck.gain.value, t);
    duck.gain.linearRampToValueAtTime(down ? 0.18 : 1, t + (down ? 0.4 : 1.2));
  }
  const onGesture = () => { ac(); if (SND.music && !musicStarted) startMusic(); tiltResume(); };
  ['touchend', 'click', 'keydown'].forEach(ev => document.addEventListener(ev, onGesture, { capture: true }));
  const ICON = {
    sfx: '<path d="M4 9h4l5-4v14l-5-4H4z"/>',
    sfxOn: '<path d="M16 9.5a4 4 0 0 1 0 5M18.5 7a7.5 7.5 0 0 1 0 10"/>',
    music: '<path d="M9 18V5l11-2v13"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/>',
    slash: '<path d="M3 3l18 18"/>',
  };
  function paintSnd() {
    document.querySelectorAll('.sndbtn').forEach(b => {
      const t = b.dataset.t, on = SND[t], name = t === 'sfx' ? 'Sound' : 'Music';
      b.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true">${ICON[t]}${t === 'sfx' && on ? ICON.sfxOn : ''}${on ? '' : ICON.slash}</svg>${name}${on ? '' : ' off'}`;
      b.title = (t === 'sfx' ? 'Sound effects ' : 'Music ') + (on ? 'on, tap to turn off' : 'off, tap to turn on');
      b.setAttribute('aria-label', b.title);
      b.classList.toggle('off', !on); b.setAttribute('aria-pressed', String(on));
    });
  }
  document.querySelectorAll('.sndbtn').forEach(b => {
    b.onclick = e => {
      e.stopPropagation();
      const t = b.dataset.t; SND[t] = !SND[t];
      try { localStorage.setItem(SNDKEY, JSON.stringify(SND)); } catch (err) {}
      if (t === 'sfx') { ac(); sfxGain.gain.value = SND.sfx ? 1 : 0; } else { SND.music ? startMusic() : stopMusic(); }
      paintSnd();
    };
  });
  paintSnd();

  // ---------- iPhone tilt (asked once, on the first gold or Top Secret card) ----------
  const TILT_KEY = 'declass_tilt';
  const tiltNeedsAsk = () => typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function';
  const lsGet = k => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const lsSet = (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} };
  function askTilt() {
    return DeviceOrientationEvent.requestPermission().then(r => {
      lsSet(TILT_KEY, r === 'granted' ? 'granted' : 'declined');
      toast(r === 'granted' ? 'Tilt is on. Move your phone to catch the light.' : 'Tilt stays off. Drag a finger across the card to move the light.');
    }).catch(() => lsSet(TILT_KEY, 'declined'));
  }
  let tiltResumed = false;
  function tiltResume() { // a permission given earlier still needs a tap each visit to switch back on
    if (tiltResumed || !tiltNeedsAsk() || lsGet(TILT_KEY) !== 'granted') return;
    tiltResumed = true; DeviceOrientationEvent.requestPermission().catch(() => {});
  }
  function maybeTiltPrompt(finish) {
    if ((finish !== 'gold' && finish !== 'topsecret') || !tiltNeedsAsk() || lsGet(TILT_KEY)) return;
    const box = document.createElement('div');
    box.className = 'tiltask';
    box.innerHTML = '✨ Tilt your phone to catch the light.<br><button class="yes" type="button">Turn on tilt</button><button class="no" type="button">Not now</button>';
    box.querySelector('.yes').onclick = e => { e.stopPropagation(); box.remove(); askTilt(); };
    box.querySelector('.no').onclick = e => { e.stopPropagation(); box.remove(); lsSet(TILT_KEY, 'notnow'); };
    $('hint').after(box);
  }
  if (tiltNeedsAsk()) { $('howTilt').hidden = false; $('howTilt').onclick = () => askTilt(); }

  // ---------- sharing (Declass Share Button mockup) ----------
  const RANK = f => FIN.indexOf(f);
  const phrase = x => 'a ' + (x.variant === 'living' ? 'living ' : '') + (x.finish === 'topsecret' ? 'Top Secret' : FNAME[x.finish].toLowerCase()) + ' ' + x.info.short + (x.finish === 'topsecret' && x.serial ? ', worldwide serial ' + ser4(x.serial) : '');
  function listText(items) { const n = items.map(phrase); return n.length < 3 ? n.join(' and ') : n.slice(0, -1).join(', ') + ', and ' + n[n.length - 1]; }
  let shPrefix = 'Declassed ';
  const shLine = items => shPrefix + listText(items) + '. ww2dispatches.com/declass #Declass';
  const imgCache = new Map();
  function loadImg(src) {
    if (!imgCache.has(src)) imgCache.set(src, new Promise((ok, bad) => { const i = new Image(); i.crossOrigin = 'anonymous'; i.onload = () => ok(i); i.onerror = bad; i.src = src; }));
    return imgCache.get(src);
  }
  const shareSrc = x => x.variant === 'living' && x.info.filmPoster ? x.info.filmPoster : x.info.img;
  function grad(c, x, y, w, h, stops) { const g = c.createLinearGradient(x, y, x + w, y + h); stops.forEach(([o, col]) => g.addColorStop(o, col)); return g; }
  function framed(c, img, x, y, w, f, serial) {
    const pad = { copper: 0.014, silver: 0.03, gold: 0.06, topsecret: 0.06 }[f] * w, cw = w - 2 * pad, ch = cw * 1.25, fh = ch + 2 * pad;
    c.save(); c.shadowColor = 'rgba(0,0,0,.55)'; c.shadowBlur = w * 0.06; c.shadowOffsetY = w * 0.025;
    if (f === 'copper') c.fillStyle = '#9C5B2E';
    if (f === 'silver') c.fillStyle = grad(c, x, y, w, fh, [[0, '#7f858e'], [0.35, '#cfd4da'], [0.5, '#9ea4ad'], [0.65, '#dde1e6'], [1, '#7f858e']]);
    if (f === 'gold') c.fillStyle = grad(c, x, y, w, fh, [[0, '#8f6612'], [0.28, '#e8c65a'], [0.46, '#b8902a'], [0.62, '#f3dc7f'], [0.86, '#9a6f14'], [1, '#c9a23a']]);
    if (f === 'topsecret') c.fillStyle = grad(c, x, y, w, fh, [[0, '#8e97a4'], [0.18, '#e9eef5'], [0.3, '#c7cfdb'], [0.45, '#f6f8fb'], [0.58, '#aeb6c2'], [0.72, '#e9eef5'], [1, '#8e97a4']]);
    c.fillRect(x, y, w, fh); c.restore();
    if (f === 'topsecret') { c.save(); c.globalCompositeOperation = 'color'; c.globalAlpha = 0.45; c.fillStyle = grad(c, x, y + fh, w, -fh, [[0, '#ff6e6e'], [0.25, '#ffe16e'], [0.5, '#6effaa'], [0.75, '#6eaaff'], [1, '#d76eff']]); c.fillRect(x, y, w, fh); c.restore(); }
    if (f === 'gold' || f === 'topsecret') {
      const ink = f === 'gold' ? 'rgba(70,45,5,.6)' : 'rgba(40,44,50,.55)'; c.strokeStyle = ink; c.lineWidth = Math.max(1, w * 0.003); const ins = w * 0.016; c.strokeRect(x + ins, y + ins, w - 2 * ins, fh - 2 * ins);
      const b = w * 0.07; c.lineWidth = Math.max(2, w * 0.005);
      [[x + ins, y + ins, 1, 1], [x + w - ins, y + ins, -1, 1], [x + ins, y + fh - ins, 1, -1], [x + w - ins, y + fh - ins, -1, -1]].forEach(([cx, cy, sx, sy]) => { c.beginPath(); c.moveTo(cx, cy + sy * b); c.lineTo(cx, cy); c.lineTo(cx + sx * b, cy); c.stroke(); });
      const m = w * 0.022; c.fillStyle = '#EDE4CF'; c.fillRect(x + pad - m, y + pad - m, cw + 2 * m, ch + 2 * m); c.strokeStyle = ink; c.lineWidth = Math.max(1, w * 0.003); c.strokeRect(x + pad - m, y + pad - m, cw + 2 * m, ch + 2 * m);
    }
    if (f === 'silver') { c.strokeStyle = 'rgba(40,44,50,.4)'; c.lineWidth = 1; c.strokeRect(x + pad, y + pad, cw, ch); }
    c.drawImage(img, x + pad, y + pad, cw, ch);
    if (f === 'gold') { c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = grad(c, x, y, w, fh, [[0, 'rgba(255,228,150,0)'], [0.42, 'rgba(255,228,150,0)'], [0.5, 'rgba(255,235,170,.35)'], [0.58, 'rgba(255,228,150,0)'], [1, 'rgba(255,228,150,0)']]); c.fillRect(x + pad, y + pad, cw, ch); c.restore(); }
    if (f === 'topsecret') {
      c.save(); c.globalCompositeOperation = 'screen'; c.fillStyle = grad(c, x, y, w, fh, [[0, 'rgba(255,120,120,.22)'], [0.25, 'rgba(255,235,120,.22)'], [0.5, 'rgba(120,255,190,.22)'], [0.75, 'rgba(120,190,255,.22)'], [1, 'rgba(230,120,255,.22)']]); c.fillRect(x + pad, y + pad, cw, ch); c.restore();
      c.save(); c.translate(x + pad + cw * 0.39, y + pad + ch * 0.06); c.rotate(-8 * Math.PI / 180); c.font = `700 ${w * 0.026}px Oswald`; const t = 'TOP SECRET', tw = c.measureText(t).width; c.strokeStyle = '#b02a1f'; c.lineWidth = Math.max(1.5, w * 0.004); c.strokeRect(-w * 0.01, -w * 0.026, tw + w * 0.02, w * 0.036); c.fillStyle = '#b02a1f'; c.fillText(t, 0, 0); c.restore();
      if (serial) { c.font = `400 ${w * 0.03}px "Special Elite"`; c.fillStyle = '#8e2a20'; c.textAlign = 'center'; c.fillText('Worldwide serial ' + ser4(serial), x + w / 2, y + fh - pad * 0.32); c.textAlign = 'left'; }
    }
  }
  function fitFont(c, text, weight, size, family, maxW) { let s = size; c.font = `${weight} ${s}px ${family}`; while (c.measureText(text).width > maxW && s > 18) { s -= 2; c.font = `${weight} ${s}px ${family}`; } return s; }
  // The finish chip (in the finish's own material) and the dispatch line beside it, centered as one row.
  // Both texts are centered on their capital letters so they sit level with the chip.
  const FORMAT_LABEL = { spec: 'Spec Sheet', photo: 'Photo of the Day', quote: 'Quote of the Day' };
  function shareChipRow(c, W, cy, x) {
    const chipText = (x.finish === 'topsecret' ? 'TOP SECRET' + (x.serial ? ' · ' + ser4(x.serial) : '') : FNAME[x.finish].toUpperCase()) + (x.variant === 'living' ? ' · LIVING CARD' : '');
    const info = x.info;
    const line = info.kind === 'namethis' ? 'Name This' : 'Dispatch No. ' + pad3(info.num) + (FORMAT_LABEL[info.format] ? ' · ' + FORMAT_LABEL[info.format] : '');
    const spaced = t => t.split('').join(String.fromCharCode(8202)); // hair spaces for the chip's letter spacing
    c.font = '700 26px Oswald'; const chipLabel = spaced(chipText); const chipTW = c.measureText(chipLabel).width; const capChip = c.measureText('H').actualBoundingBoxAscent || 19;
    c.font = '400 28px "Special Elite"'; const lineW = c.measureText(line).width; const capLine = c.measureText('H').actualBoundingBoxAscent || 19;
    const padX = 16, chipH = 42, chipW = chipTW + padX * 2, gap = 16, total = chipW + gap + lineW;
    const x0 = (W - total) / 2, top = cy - chipH / 2;
    const fills = {
      copper: () => '#9C5B2E',
      silver: () => grad(c, x0, top, chipW, 0, [[0, '#7e838c'], [0.5, '#dde1e6'], [1, '#7e838c']]),
      gold: () => grad(c, x0, top, chipW, 0, [[0, '#a67c1e'], [0.5, '#f0cf68'], [1, '#a67c1e']]),
      topsecret: () => grad(c, x0, top, chipW, 0, [[0, '#c9d2dd'], [0.25, '#f2c6d8'], [0.5, '#e9eef5'], [0.75, '#c9f0dc'], [1, '#c7d6f5']]),
    };
    const ink = { copper: '#f6ead8', silver: '#1A1612', gold: '#2a1f08', topsecret: '#8e2a20' };
    c.fillStyle = fills[x.finish](); c.beginPath();
    if (c.roundRect) c.roundRect(x0, top, chipW, chipH, 5); else c.rect(x0, top, chipW, chipH);
    c.fill();
    c.textAlign = 'left';
    c.fillStyle = ink[x.finish]; c.font = '700 26px Oswald'; c.fillText(chipLabel, x0 + padX, cy + capChip / 2);
    c.fillStyle = '#b9ad92'; c.font = '400 28px "Special Elite"'; c.fillText(line, x0 + chipW + gap, cy + capLine / 2);
    c.textAlign = 'center';
  }
  async function paintShare(cv, items) {
    await Promise.all(['700 40px Oswald', '400 20px "Special Elite"'].map(f => document.fonts.load(f).catch(() => {})));
    const imgs = await Promise.all(items.map(x => loadImg(shareSrc(x)).catch(() => null)));
    const W = 1080, H = 1350, c = cv.getContext('2d');
    c.textAlign = 'left'; c.fillStyle = '#17140f'; c.fillRect(0, 0, W, H);
    const g = c.createRadialGradient(W / 2, H * 0.48, W * 0.1, W / 2, H * 0.5, H * 0.75); g.addColorStop(0, 'rgba(176,74,62,.22)'); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.fillRect(0, 0, W, H);
    c.globalAlpha = 0.05; c.fillStyle = '#EDE4CF'; for (let y = 0; y < H; y += 6) c.fillRect(0, y, W, 1); c.globalAlpha = 1;
    // blue DECLASSED stamp, top left
    c.save(); c.translate(58, 58); c.rotate(-4 * Math.PI / 180); c.strokeStyle = '#5b8fd6'; c.fillStyle = '#5b8fd6'; c.lineWidth = 4; c.font = '700 30px Oswald'; c.textAlign = 'left';
    const tw = c.measureText('D E C L A S S E D').width; c.strokeRect(-14, -30, tw + 28, 41); c.fillText('D E C L A S S E D', 0, 0); c.restore();
    // the name, then the finish chip and the dispatch line (Option B)
    const best = items[0];
    c.textAlign = 'center'; c.fillStyle = '#EDE4CF';
    fitFont(c, best.info.short.toUpperCase(), 700, 68, 'Oswald', W - 120);
    c.fillText(best.info.short.toUpperCase(), W / 2, 110);
    shareChipRow(c, W, 148, best);
    if (items.length > 1) { c.textAlign = 'center'; c.fillStyle = '#b9ad92'; const sub = 'with ' + listText(items.slice(1)); fitFont(c, sub, 400, 28, '"Special Elite"', W - 100); c.fillText(sub, W / 2, 204); }
    // cards: cy is roughly the card's middle
    const draw = (x, k, cx, cy, w, rot) => { c.save(); c.translate(cx, cy); c.rotate(rot * Math.PI / 180); if (imgs[k]) framed(c, imgs[k], -w / 2, -w * 0.62, w, x.finish, x.serial); c.restore(); };
    if (items.length === 1) draw(items[0], 0, W / 2, 188 + 830 * 0.62, 830, 0);
    else if (items.length === 2) { const cw = 610; draw(items[1], 1, W / 2 + 205, 730, cw, 7); draw(items[0], 0, W / 2 - 205, 716, cw, -5); }
    else { const cw = 560; draw(items[1], 1, W / 2 - 240, 756, cw, -9); draw(items[2], 2, W / 2 + 240, 756, cw, 9); draw(items[0], 0, W / 2, 713, cw, 0); }
    // footer
    c.textAlign = 'center'; c.fillStyle = '#EDE4CF'; c.font = '700 46px Oswald'; c.fillText('DECLASS', W / 2, 1280);
    c.fillStyle = '#c9bd9f'; fitFont(c, 'a WW2 Dispatches game · ww2dispatches.com/declass', 400, 30, '"Special Elite"', W - 60);
    c.fillText('a WW2 Dispatches game · ww2dispatches.com/declass', W / 2, 1316);
    const file = best.file;
    c.fillStyle = '#9a8f78'; c.font = '400 22px "Special Elite"';
    c.fillText((file ? 'File ' + file + ' · ' : '') + new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }), W / 2, 1341);
    c.textAlign = 'left';
  }
  let shAll = [], shSel = [], shBlob = null, shText = '';
  const shChosen = () => shAll.filter((x, i) => shSel[i]).sort((a, b) => RANK(b.finish) - RANK(a.finish) || (b.variant === 'living') - (a.variant === 'living'));
  async function shRefresh() {
    const items = shChosen();
    shBlob = null; shText = shLine(items);
    $('shLine').textContent = shText;
    $('shGo').disabled = true;
    try {
      await paintShare($('shPv'), items);
      shBlob = await new Promise(r => $('shPv').toBlob(r, 'image/png'));
    } catch (e) { shBlob = null; }
    $('shGo').disabled = false;
  }
  function shDrawPicks() {
    const row = $('shCards'); row.innerHTML = '';
    if (shAll.length < 2) { $('shLbl').textContent = ''; return; }
    shAll.forEach((x, i) => {
      const b = document.createElement('button');
      b.className = 'shpc' + (shSel[i] ? '' : ' off'); b.type = 'button';
      b.innerHTML = `<img src="${esc(x.info.img)}" alt=""><b>✓</b><small>${esc(FNAME[x.finish] + ' ' + x.info.short)}</small>`;
      b.onclick = () => { if (shSel[i] && shSel.filter(Boolean).length === 1) return; shSel[i] = !shSel[i]; shDrawPicks(); shRefresh(); };
      row.appendChild(b);
    });
    const n = shSel.filter(Boolean).length;
    $('shLbl').textContent = n === 1 ? 'Starts with your best card. Tap a card to add or remove it.' : n + ' cards in the picture';
  }
  // items: [{info, finish, variant, serial, file}]
  function openShare(items, prefix) {
    shPrefix = prefix || 'Declassed ';
    shAll = items.filter(x => x.info);
    if (!shAll.length) return;
    const best = shAll.reduce((m, x, i) => RANK(x.finish) > RANK(shAll[m].finish) ? i : m, 0);
    shSel = shAll.map((_, i) => i === best);
    $('shTitle').textContent = shAll.length > 1 ? 'Pick what to share' : 'Share this card';
    $('shui').hidden = false; $('shui').scrollTop = 0;
    shDrawPicks(); shRefresh();
  }
  $('shBack').onclick = () => { $('shui').hidden = true; };
  $('shGo').onclick = () => {
    const text = shText;
    if (navigator.clipboard) navigator.clipboard.writeText(text).catch(() => {});
    const file = shBlob ? new File([shBlob], 'declass.png', { type: 'image/png' }) : null;
    if (file && navigator.canShare && navigator.canShare({ files: [file] })) {
      navigator.share({ files: [file], text }).then(() => { $('shui').hidden = true; }).catch(() => {});
      return;
    }
    if (shBlob) {
      const a = document.createElement('a'); a.href = URL.createObjectURL(shBlob); a.download = 'declass.png';
      document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000);
      toast('Picture saved. The caption is copied, ready to paste.');
    } else toast('The caption is copied, ready to paste.');
  };
  const pullItem = p => ({ info: p.cardInfo || BYID.get(p.card), finish: p.finish, variant: p.variant, serial: p.serial, file: p.file });
  $('shareBtn').onclick = () => openShare(pulls.map(pullItem), cardEnv && cardEnv.kind === 'commemorative' ? `Declassed the ${cardEnv.name} file: ` : 'Declassed ');
  $('vShare').onclick = () => {
    const id = viewList[vi], pl = myPulls();
    const p = pl.filter(x => x.card === id && x.variant === viewSel.variant && x.finish === viewSel.finish).sort((a, b) => (b.serial ? 1 : 0) - (a.serial ? 1 : 0))[0];
    if (p) openShare([pullItem(p)]);
  };

  // ---------- sets: monthly files (stamps) and collections (pins) ----------
  const PINS = [[25, 'copper'], [50, 'silver'], [100, 'gold']];
  const MET = { copper: ['#6e3a17', '#c98652', '#9C5B2E'], silver: ['#6f757e', '#e3e7ec', '#9ea4ad'], gold: ['#7a560c', '#f3dc7f', '#b8902a'] };
  let suid = 0;
  function stampSVG(name, date) {
    const id = 'sp' + (suid++);
    return `<svg viewBox="0 0 100 100"><defs><path id="${id}" d="M50,50 m-36,0 a36,36 0 1,1 72,0 a36,36 0 1,1 -72,0"/></defs><circle cx="50" cy="50" r="46" fill="none" stroke="currentColor" stroke-width="4"/><circle cx="50" cy="50" r="31" fill="none" stroke="currentColor" stroke-width="1.5"/><text font-family="Oswald" font-weight="700" font-size="9" letter-spacing="1.5" fill="currentColor"><textPath href="#${id}" startOffset="25%" text-anchor="middle">${esc(name.toUpperCase())}</textPath></text><text x="50" y="55" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="13" fill="currentColor" textLength="48" lengthAdjust="spacingAndGlyphs">COMPLETE</text><text x="50" y="66" text-anchor="middle" font-family="Special Elite" font-size="6" fill="currentColor">${esc(date)}</text></svg>`;
  }
  function pinSVG(n, metal) {
    const id = 'pg' + (suid++), m = MET[metal];
    return `<svg viewBox="0 0 60 60"><defs><linearGradient id="${id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${m[1]}"/><stop offset=".5" stop-color="${m[2]}"/><stop offset="1" stop-color="${m[0]}"/></linearGradient></defs><circle cx="30" cy="30" r="27" fill="url(#${id})"/><circle cx="30" cy="30" r="21" fill="none" stroke="${m[0]}" stroke-width="1.4" opacity=".7"/><text x="30" y="37.5" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="20" fill="${m[0]}">${n}</text></svg>`;
  }
  const etMonth = iso => new Date(iso).toLocaleDateString('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit' }).slice(0, 7);
  const monthName = ym => new Date(ym + '-15T12:00:00Z').toLocaleDateString('en-US', { month: 'long', year: 'numeric', timeZone: 'UTC' });
  const monthEnd = ym => { const [y, m] = ym.split('-').map(Number); return new Date(Date.UTC(y, m, 0, 12)); };
  const stampDate = d => d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).toUpperCase();
  function setsModel() {
    const H = holdingsNow(), firstAt = new Map();
    for (const p of myPulls()) { const t = p.at || new Date().toISOString(); if (!firstAt.has(p.card) || t < firstAt.get(p.card)) firstAt.set(p.card, t); }
    const nowYm = etMonth(new Date().toISOString());
    const byMonth = new Map();
    CAT.filter(c => c.kind === 'dispatch').forEach(c => { const ym = etMonth(c.postAt); if (!byMonth.has(ym)) byMonth.set(ym, []); byMonth.get(ym).push(c); });
    const months = [...byMonth.keys()].sort().reverse().map(ym => {
      const all = byMonth.get(ym), held = all.filter(c => H.has(c.id)).length, closed = ym < nowYm;
      let stamp = null;
      if (closed && held === all.length) {
        const last = all.reduce((m, c) => (firstAt.get(c.id) > m ? firstAt.get(c.id) : m), '');
        const end = monthEnd(ym);
        stamp = stampDate(last && new Date(last) > end ? new Date(last) : end);
      }
      return { ym, name: monthName(ym), all: all.length, held, closed, stamp };
    });
    const cap = s => s.charAt(0).toUpperCase() + s.slice(1);
    const distinct = key => [...new Set(CAT.flatMap(c => c[key] || []))].sort();
    const groups = [
      ['Series', SERIES.map(([k, name, col]) => [name, col, c => c.series === k])],
      ['Years', ERAS.map(([k, name]) => [name || k, '#1A1612', c => c.kind === 'dispatch' && c.era === k])],
      ['Theaters', distinct('theater').map(t => [cap(t), '#3D5884', c => (c.theater || []).includes(t)])],
      ['Nations', ['US', 'Britain', 'Soviet Union', 'Germany', 'Japan'].map(n => [n, '#6b3d2e', c => (c.nations || []).includes(n)])],
      ['Subjects', distinct('subjects').map(t => [cap(t), '#5E6B3A', c => (c.subjects || []).includes(t)])],
    ].map(([g, list]) => [g, list.map(([name, col, fn]) => {
      const all = CAT.filter(fn), held = all.filter(c => H.has(c.id)).length;
      return { name, col, all: all.length, held, pins: PINS.filter(([k]) => held >= k), next: PINS.find(([k]) => held < k) };
    }).filter(x => x.all >= 5)]).filter(([, list]) => list.length);
    return { months, groups };
  }
  function renderSets() {
    const { months, groups } = setsModel();
    let h = '<h2>Monthly files</h2>';
    const stamps = months.filter(m => m.stamp);
    if (stamps.length) h += `<div class="sshelf">${stamps.map(m => `<div class="stp" title="${esc(m.name)}">${stampSVG(m.name, m.stamp)}</div>`).join('')}</div>`;
    months.filter(m => !m.stamp).forEach(m => {
      const full = m.held === m.all;
      const end = monthEnd(m.ym).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', timeZone: 'UTC' });
      const txt = !m.closed ? (full ? 'Currently complete · the stamp lands when the month closes' : `${m.held} of ${m.all} · closes ${end}`) : `${m.held} of ${m.all} · closed, still collectable`;
      h += `<div class="srow" style="--c:#7a5c2e"><div class="nm"><b>${esc(m.name)} files</b><small class="${full ? 'cc' : m.all - m.held === 1 ? 'near' : ''}">${txt}</small><i><em style="width:${m.all ? m.held / m.all * 100 : 0}%"></em></i></div></div>`;
    });
    groups.forEach(([g, list]) => {
      h += `<h2>${esc(g)}</h2>`;
      list.forEach(x => {
        const full = x.held === x.all;
        h += `<div class="srow" style="--c:${x.col}"><div class="nm"><b>${esc(x.name)}</b><small class="${full ? 'cc' : ''}">${full ? 'Currently complete · ' + x.held + ' cards' : x.held + ' of ' + x.all}${x.next ? ' · next pin at ' + x.next[0] : ''}</small><i><em style="width:${x.held / x.all * 100}%"></em></i></div><div class="spins">${x.pins.map(([k, m]) => `<div class="spin">${pinSVG(k, m)}</div>`).join('')}</div></div>`;
      });
    });
    h += '<p class="snote">A month\'s stamp is permanent once the month closes with every card held, even if you catch up later. Collections appear once they have five cards, and say "Currently complete" until the next card posts. Pins count different cards, never duplicates.</p>';
    $('sets').innerHTML = h;
    show('sSets');
  }
  $('backSets').onclick = () => { renderHome(); show('sHome'); };

  // ---------- Delete my dossier ----------
  $('deleteBtn').onclick = () => show('sDelete');
  $('deleteNo').onclick = () => { renderHome(); show('sHome'); };
  $('deleteYes').onclick = () => {
    $('deleteYes').disabled = true;
    api('delete', {}).then(() => {
      try { google.accounts.id.disableAutoSelect(); } catch (e) {}
      ST = null; STARTER = null; saveStarterLocal(); show('sDeleted');
    }).catch(e => toast('That did not work (' + e.message + ').')).finally(() => { $('deleteYes').disabled = false; });
  };
  $('deletedOk').onclick = () => location.replace('/declass');

  // ---------- checking a file number from a share picture ----------
  function checkFile(n) {
    show('sFile');
    $('backFile').onclick = () => { history.replaceState(null, '', '/declass'); route(); };
    api('file?n=' + encodeURIComponent(n)).then(d => {
      const x = { info: d.card, finish: d.finish, variant: d.variant, serial: d.serial };
      $('fileTitle').innerHTML = '<span class="filegood">GENUINE</span><br>File ' + esc(d.file);
      $('fileSub').textContent = `${phrase(x).replace(/^a /, 'A ')}, declassed ${localDate(d.at)}.`;
      $('fileCard').innerHTML = cardFace(d.card, d.finish, d.variant, d.serial, { autoplay: true });
      if (d.variant === 'living') startFilm($('fileCard'), d.card);
    }).catch(() => {
      $('fileTitle').textContent = 'No file matches that number';
      $('fileSub').textContent = 'Check the number on the picture and try again. Every card pulled in Declass has a file number that checks out here.';
      $('fileCard').innerHTML = '';
    });
  }

  // ---------- boot ----------
  function route() {
    if (signedIn()) {
      if (STARTER && ST.player.starterDone) { STARTER = null; saveStarterLocal(); }
      renderHome(); show('sHome');
    } else if (STARTER) {
      if (STARTER.revealed.some(r => !r)) startCards(STARTER.pulls, 'starterLocal', new Map(), { kind: 'starter' });
      else { renderHome(); show('sHome'); }
    } else show('sLanding');
  }
  // keep the times fresh if the page stays open
  setInterval(() => { if ($('sHome').classList.contains('on')) refreshState().then(renderHome).catch(() => {}); }, 60000);

  show('sLoading');
  api('config').then(cfg => {
    CFG = cfg;
    if (!cfg.open) return show('sSoon');
    loadGoogle();
    return Promise.all([api('catalog'), api('state')]).then(([c, s]) => {
      setCatalog(c.cards); ST = s;
      const file = new URLSearchParams(location.search).get('file');
      if (file) checkFile(file); else route();
    });
  }).catch(() => show('sSoon'));
})();
