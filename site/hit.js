// Visit counts for ww2dispatches.com (2 Nov 2026). Sends one small note per page view to /api/hit: which page,
// whether this browser already came by today (kept in this browser only), and where the visit came from.
// No cookies and no ids leave the browser. Skipped when the browser asks not to be tracked. A browser marked as the
// admin's (ww_me, set by the console or by signing in to Declass as admin) only adds to an excluded admin count.
// 18 Nov 2026: also says which dispatch, Campaign Series part or newsletter issue was opened, and counts clicks on links
// that leave the site, the buttons into Declass, the newsletter signup, and Name This files opened. Totals only, as before.
// 24 Nov 2026: clicks to a Stripe gift link count as out:support (Ko-fi is retired), and a return to /support?thanks=once
// counts as one completed gift.
(function () {
  var ls = function (k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } };
  var ss = function (k, v) { try { if (v === undefined) return sessionStorage.getItem(k); sessionStorage.setItem(k, v); } catch (e) { return null; } };
  var off = navigator.globalPrivacyControl || navigator.doNotTrack === '1';
  var me = function () { return ls('ww_me') === '1'; };
  var queue = [], timer = null;
  function send(body) {
    if (off) return;
    try { fetch('/api/hit', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body), keepalive: true, credentials: 'omit' }).catch(function () {}); } catch (e) {}
  }
  function flush() { clearTimeout(timer); timer = null; if (queue.length && !me()) send({ e: queue }); queue = []; }
  // game actions, batched: wwHit('card')
  window.wwHit = function (name) { if (me()) return; queue.push(name); if (queue.length >= 20) flush(); else if (!timer) timer = setTimeout(flush, 5000); };
  addEventListener('pagehide', flush);
  document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'hidden') flush(); });

  var path = location.pathname.replace(/\/+$/, '') || '/';
  var page = path === '/' || path === '/index.html' ? 'home' : /^\/declass(\/index\.html)?$/.test(path) ? 'declass'
    : /^\/newsletter(\/index\.html)?$/.test(path) ? 'newsletter' : /^\/newsletter\//.test(path) ? 'issue'
    : /^\/campaign-series(\/|$)/.test(path) ? 'campaign' : /^\/name-this(\/|$)/.test(path) ? 'namethis'
    : /^\/privacy/.test(path) ? 'privacy' : /^\/support/.test(path) ? 'support' : /^\/about(\.html)?$/.test(path) ? 'about'
    : /^\/on-this-day(\/|$)/.test(path) ? 'onthisday' : /^\/dispatches(\/|$)/.test(path) ? 'dispatch' : 'other';
  // Which dispatch, series part or issue this is (the address says so), for the per page counts.
  var detail = '', m, clean = path.replace(/\.html$/, '').replace(/\/index$/, '');
  if (page === 'dispatch' && (m = clean.match(/^\/dispatches\/(\d{3}-[a-z0-9-]{1,60})$/))) detail = 'dispatch/' + m[1];
  else if (page === 'campaign' && (m = clean.match(/^\/campaign-series(?:\/([a-z0-9-]{1,50})(?:\/((?:day|part)-\d{2}))?)?$/))) detail = 'campaign/' + (m[1] ? m[1] + (m[2] ? '/' + m[2] : '') : 'shelf');
  else if (page === 'issue' && (m = clean.match(/^\/newsletter\/([a-z0-9-]{1,60})$/))) detail = 'issue/' + m[1];

  // Clicks worth knowing about: links that leave the site (by where they go), buttons into Declass, the newsletter
  // signup, and Name This files opened. Reads the page as it is, so the pages themselves need no changes; if the Name
  // This markup changes (button.reveal with data-id, #oc-threads, #oc-x), update the two lines that name it here.
  var OUT = [['substack', /substack\.com$/], ['instagram', /instagram\.com$/], ['threads', /threads\.(net|com)$/], ['x', /(^|\.)(x|twitter)\.com$/], ['tiktok', /tiktok\.com$/], ['youtube', /(youtube\.com|youtu\.be)$/], ['facebook', /facebook\.com$/], ['support', /(^|\.)buy\.stripe\.com$/]];
  document.addEventListener('click', function (ev) {
    if (off || me()) return;
    var t = ev.target && ev.target.closest ? ev.target.closest('a[href], button.reveal') : null, c = [];
    if (!t) return;
    if (t.tagName === 'BUTTON') {
      if (page === 'namethis' && t.getAttribute('aria-expanded') === 'false' && t.getAttribute('data-id')) c.push('ntopen:' + t.getAttribute('data-id'));
    } else {
      var u; try { u = new URL(t.href, location.href); } catch (e) { return; }
      if (!/^https?:$/.test(u.protocol)) return;
      if (u.host !== location.host) {
        var name = 'other'; for (var i = 0; i < OUT.length; i++) if (OUT[i][1].test(u.hostname)) { name = OUT[i][0]; break; }
        c.push('out:' + name);
        if (page === 'namethis' && (t.id === 'oc-threads' || t.id === 'oc-x')) c.push('cta:guess');
      } else if (page !== 'declass' && /^\/declass\/?$/.test(u.pathname)) {
        var card = u.searchParams.get('card');
        if (card) { c.push('cta:collect'); c.push('collect:' + card); } else c.push('cta:play');
      }
    }
    if (c.length) send({ c: c, pg: page });
  }, true);
  document.addEventListener('submit', function (ev) {
    if (off || me()) return;
    if (ev.target && /substack\.com/.test(ev.target.action || '')) send({ c: ['cta:subscribe'], pg: page });
  }, true);

  if (me()) { send({ admin: 1 }); return; }

  // A completed gift: Stripe sends the giver back to /support?thanks=once, and the page takes the query off the
  // address as soon as it loads, before this script runs. The browser's record of how the page was opened still
  // has the original address, so read that. A reload opens the clean address, so a gift counts once.
  var gift = false;
  if (page === 'support') {
    var opened = location.href;
    try { var nav = performance.getEntriesByType('navigation')[0]; if (nav && nav.name) opened = nav.name; } catch (e) {}
    try { gift = new URL(opened).searchParams.get('thanks') === 'once' || /[?&]thanks=once(&|$)/.test(location.search); } catch (e) {}
  }
  var d = new Date(), today = d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate();
  var seen = {}; try { seen = JSON.parse(ls('ww_day') || '{}'); } catch (e) {}
  if (seen.d !== today) seen = { d: today, p: [] };
  if (!seen.x) seen.x = [];
  var body = { p: page };
  if (!seen.p.length) body.day1 = 1;
  if (seen.p.indexOf(page) < 0) { body.v = 1; seen.p.push(page); }
  if (detail) { body.d = detail; if (seen.x.indexOf(detail) < 0) { body.dv = 1; seen.x.push(detail); } }
  if (gift) body.g = 'once';
  if (!ls('ww_v')) { body.nw = 1; ls('ww_v', '1'); ls('ww_land', page); } // ww_land: the first page this browser ever saw, sent along if it later makes a Declass account
  ls('ww_day', JSON.stringify(seen));
  // source: counted once per visit (browser session), on the first page
  if (!ss('ww_s')) {
    var q = new URLSearchParams(location.search), src = q.get('utm_source') || q.get('ref') || '';
    if (!src && document.referrer) { try { var r = new URL(document.referrer); if (r.host !== location.host) src = r.host; } catch (e) {} }
    // A social app's built in browser often hides where the visitor came from, but it names itself (13 Nov 2026).
    if (!src) { var ua = navigator.userAgent || ''; src = /Barcelona/i.test(ua) ? 'threads' : /Instagram/i.test(ua) ? 'instagram' : /FBAN|FBAV|FB_IAB|FBIOS/i.test(ua) ? 'facebook' : /musical_ly|BytedanceWebview|TikTok/i.test(ua) ? 'tiktok' : /Twitter/i.test(ua) ? 'x' : ''; }
    body.s = src;
    ss('ww_s', '1');
    if (!ls('ww_src')) ls('ww_src', src || 'direct'); // first ever source, sent along if this browser later makes a Declass account
  }
  send(body);
})();
