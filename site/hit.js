// Visit counts for ww2dispatches.com (2 Nov 2026). Sends one small note per page view to /api/hit: which page,
// whether this browser already came by today (kept in this browser only), and where the visit came from.
// No cookies and no ids leave the browser. Skipped when the browser asks not to be tracked. A browser marked as the
// admin's (ww_me, set by the console or by signing in to Declass as admin) only adds to an excluded admin count.
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
    : /^\/privacy/.test(path) ? 'privacy' : /^\/support/.test(path) ? 'support' : 'other';
  if (me()) { send({ admin: 1 }); return; }
  var d = new Date(), today = d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate();
  var seen = {}; try { seen = JSON.parse(ls('ww_day') || '{}'); } catch (e) {}
  if (seen.d !== today) seen = { d: today, p: [] };
  var body = { p: page };
  if (!seen.p.length) body.day1 = 1;
  if (seen.p.indexOf(page) < 0) { body.v = 1; seen.p.push(page); }
  if (!ls('ww_v')) { body.nw = 1; ls('ww_v', '1'); }
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
