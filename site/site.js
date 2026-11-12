// WW2 Dispatches site: shared script for every page except inside Declass (Site Revamp doc).
// The menu, the newsletter signup boxes, and WW2.now(), the clock every page uses to decide
// what has posted. On a preview address (*.pages.dev) a test date can stand in for now:
// add ?asof=2026-12-01T07:00 (Denver time) to any page; ?asof=off clears it. The server
// side (functions/_lib/release.js) reads the same cookie, so pages and data agree.
(function () {
  var W = window.WW2 = window.WW2 || {};

  // ---------- test date (preview addresses only) ----------
  var preview = /\.pages\.dev$|^localhost$|^127\.0\.0\.1$/.test(location.hostname);
  function cookie(name) { var m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)")); return m ? decodeURIComponent(m[1]) : ""; }
  var asof = preview ? cookie("asof") : "";
  var q = preview ? new URLSearchParams(location.search).get("asof") : null;
  if (q !== null) {
    if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(q)) { asof = q; document.cookie = "asof=" + encodeURIComponent(q) + "; path=/; max-age=86400; SameSite=Lax"; }
    else { asof = ""; document.cookie = "asof=; path=/; max-age=0; SameSite=Lax"; }
  }
  // Denver wall clock to a real moment: try the two offsets Denver uses and keep the one that reads back right.
  function denverToDate(local) {
    var m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/.exec(local || ""); if (!m) return null;
    for (var off = 6; off <= 7; off++) {
      var d = new Date(Date.UTC(+m[1], m[2] - 1, +m[3], +m[4] + off, +m[5]));
      if (denverParts(d).stamp === local) return d;
    }
    return new Date(Date.UTC(+m[1], m[2] - 1, +m[3], +m[4] + 7, +m[5]));
  }
  function denverParts(d) {
    var p = {};
    new Intl.DateTimeFormat("en-CA", { timeZone: "America/Denver", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23" })
      .formatToParts(d).forEach(function (x) { p[x.type] = x.value; });
    return { date: p.year + "-" + p.month + "-" + p.day, time: p.hour + ":" + p.minute, stamp: p.year + "-" + p.month + "-" + p.day + "T" + p.hour + ":" + p.minute };
  }
  var fixed = asof ? denverToDate(asof) : null;
  W.now = function () { return fixed ? new Date(fixed.getTime()) : new Date(); };
  W.denver = function (d) { return denverParts(d || W.now()); };
  W.denverToDate = denverToDate;
  W.released = function (iso) { return Date.parse(iso) <= W.now().getTime(); };
  W.esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  if (fixed && !document.querySelector(".testdate")) {
    document.addEventListener("DOMContentLoaded", function () {
      var b = document.createElement("div"); b.className = "testdate";
      b.innerHTML = "Test date " + W.esc(asof.replace("T", " ")) + " MT <a href=\"?asof=off\">Clear</a>";
      document.body.appendChild(b);
    });
  }

  // ---------- menu ----------
  function setupMenu() {
    var btn = document.querySelector(".menubtn"), menu = document.getElementById("sitemenu"), bar = document.querySelector(".sitebar");
    if (!btn || !menu) return;
    function place() { if (bar) document.documentElement.style.setProperty("--barh", Math.round(bar.getBoundingClientRect().bottom) + "px"); }
    function open(on) {
      place();
      btn.setAttribute("aria-expanded", on ? "true" : "false");
      btn.setAttribute("aria-label", on ? "Close menu" : "Menu");
      menu.hidden = !on;
      document.body.classList.toggle("menu-open", on);
      if (on) { var first = menu.querySelector("a"); if (first) first.focus(); }
    }
    place();
    btn.addEventListener("click", function () { open(btn.getAttribute("aria-expanded") !== "true"); });
    menu.addEventListener("click", function (e) { if (e.target === menu || e.target.closest("a")) open(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !menu.hidden) { open(false); btn.focus(); } });
    window.addEventListener("resize", place);
  }

  // ---------- newsletter signup: posts to Substack in a hidden frame so the reader stays here ----------
  function setupSignup() {
    var forms = document.querySelectorAll("form.nl-form");
    if (!forms.length) return;
    if (!document.querySelector('iframe[name="substack-signup"]')) {
      var f = document.createElement("iframe"); f.name = "substack-signup"; f.title = "Newsletter signup"; f.hidden = true; document.body.appendChild(f);
    }
    Array.prototype.forEach.call(forms, function (form) {
      form.addEventListener("submit", function () {
        var sent = form.parentNode.querySelector(".sent"); if (sent) sent.hidden = false;
        setTimeout(function () { form.reset(); }, 300);
      });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { setupMenu(); setupSignup(); });
  else { setupMenu(); setupSignup(); }
})();
