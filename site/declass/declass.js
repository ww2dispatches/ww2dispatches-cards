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
  function nudge(el) { el.classList.remove('shake'); void el.offsetWidth; el.classList.add('shake'); }

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
    const p = ST && ST.player, files = $('files');
    files.innerHTML = '';
    const locked = signedIn() && ST.waiting.length > 0;
    const guard = (b, fn) => { if (locked) return nudge(b); fn(); };

    $('streakN').textContent = p ? p.streak : 0;
    $('streakHint').textContent = !p ? 'sign in to start a streak'
      : p.streak ? (p.nextPriorityIn === 3 ? 'priority envelope earned' : 'priority envelope in ' + p.nextPriorityIn + ' day' + (p.nextPriorityIn > 1 ? 's' : ''))
      : 'open an envelope to start';

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
      for (const e of ST.envelopes.slice().reverse()) {
        const name = (etHour(e.at) < 12 ? 'Morning' : 'Evening') + ' envelope' + (e.deep ? ' · deep archive' : '');
        files.appendChild(slotButton(e.opened ? 'done' : locked ? 'locked' : 'live', name,
          e.opened ? 'Opened · out since ' + localTime(e.at) : 'Out since ' + localTime(e.at) + ' · ' + leftText(e.closes),
          b => { if (!e.opened) guard(b, () => pick(e)); }));
      }
    }
    $('signBar').hidden = Boolean(p);
    $('signBar').querySelector('span').textContent = STARTER
      ? 'Your starter pack is waiting in this browser. Save your dossier to keep it and collect every day.'
      : 'Sign in to keep a dossier and open a new envelope file every day.';
    $('nextFile').textContent = ST && ST.next ? 'Next file arrives ' + localDayTime(ST.next) : '';

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
    $('seriesTiles').querySelectorAll('[data-series]').forEach(b => { b.onclick = () => section('series', b.dataset.series); });
    $('yearTiles').innerHTML = ERAS.map(([k, name, span]) => {
      const all = CAT.filter(c => c.kind === 'dispatch' && c.era === k), h = all.filter(c => H.has(c.id)).length;
      return `<button class="tile" data-year="${k}" ${all.length ? '' : 'disabled'}><i style="background:var(--ink)"></i><b>${name || k}</b><span>${all.length ? h + ' of ' + all.length : 'None posted yet'}</span>${span ? `<span>${span}</span>` : ''}<div class="bar"><i style="width:${all.length ? h / all.length * 100 : 0}%"></i></div></button>`;
    }).join('');
    $('yearTiles').querySelectorAll('[data-year]').forEach(b => { b.onclick = () => section('year', b.dataset.year); });
    $('allSub').textContent = `${have} of ${total} cards`;
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
    $('sectionSub').textContent = `${h} of ${list.length} cards · swatches show the finishes you hold, ▶ a Living Card`;
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
  let busy = false;
  function chosen(i) {
    if (busy) return;
    busy = true;
    const env = cur;
    const req = env.kind === 'starter' ? api('starter', {}) : api('open', { slot: env.kind === 'priority' ? 'priority' : env.key });
    const before = holdingsNow();
    const b = $('bigEnv');
    b.className = 'big';
    b.innerHTML = `<div class="env${envClass(env.kind)}">${envHTML(i, env)}</div><div class="cardsout"><i></i><i></i><i></i></div>`;
    $('tearing').textContent = env.kind === 'commemorative' ? env.stamp : 'Declassifying…';
    $('tearing').classList.toggle('goldt', env.kind === 'commemorative');
    show('sOpen');
    // preload the pictures (and films) as soon as the server answers
    req.then(d => d.pulls.forEach(p => { if (p.cardInfo) { new Image().src = p.cardInfo.img; if (p.variant === 'living' && p.cardInfo.filmMp4) { const v = document.createElement('video'); v.preload = 'auto'; v.muted = true; v.src = p.cardInfo.filmMp4; } } })).catch(() => {});
    setTimeout(() => b.classList.add('stamp'), 250);
    setTimeout(() => { b.classList.add('go'); $('tearing').textContent = env.kind === 'starter' ? 'Five cards inside.' : env.kind === 'commemorative' ? env.stamp : 'Three cards inside.'; }, 950);
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
    if (k === 'priority' || k === 'commemorative') return 'from the deep archive';
    if (k === 'starter') return first ? "today's dispatch" : 'your starter pack';
    if (first && p.cardInfo && p.cardInfo.kind === 'dispatch' && p.variant === 'still' && i === 0) return "today's dispatch";
    return cardEnv && cardEnv.deep ? 'from the deep archive' : 'from the archive';
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
    $('flip').classList.add('up');
    if (p.cardInfo && p.variant === 'living') startFilm($('flip'), p.cardInfo);
    if (cardMode === 'starterLocal') { STARTER.revealed = revealed.slice(); saveStarterLocal(); }
    else if (p.id) api('turn', { ids: [p.id] }).catch(() => {});
    $('hint').innerHTML = hintAfter(p, idx);
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
      return n ? `<button class="s4 f-${f}${variant === viewSel.variant && f === viewSel.finish ? ' cur' : ''}" data-v="${variant}" data-f="${f}">${FNAME[f]}<small>×${n}</small></button>` : '<div class="s4 off">?<small>sealed</small></div>';
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
  $('landEnv').onclick = openStarter;
  $('landEnv').onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openStarter(); } };

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
    return Promise.all([api('catalog'), api('state')]).then(([c, s]) => { setCatalog(c.cards); ST = s; route(); });
  }).catch(() => show('sSoon'));
})();
