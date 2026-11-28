// The archive (Archive Site Design Notes, 28 Nov 2026): the calendar at /on-this-day/ and the 366 date pages.
// The pages come from renderer/dispatch_pages.py, and the server has already removed anything that has not
// posted yet (data-release, data-until), so this script only shows, hides and filters what is there.
// Without it the calendar shows every month and each day links straight to its date page.
(function () {
  var W = window.WW2 || {};
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };
  var MONTHS = "january february march april may june july august september october november december".split(" ");
  var dayUrl = function (md) { return "/on-this-day/" + MONTHS[+md.slice(0, 2) - 1] + "-" + (+md.slice(3)) + "/"; };
  var today = (W.denver ? W.denver().date : new Date().toISOString().slice(0, 10)).slice(5);

  // Old archive links (/on-this-day/#d-11-23) open that date's page.
  var old = (location.hash.match(/^#d-(\d\d-\d\d)$/) || [])[1];
  if (old && /^\/on-this-day\/?$/.test(location.pathname)) { location.replace(dayUrl(old)); return; }

  function chipsFor(root, onPick) {
    var chips = $$(".chips .toggle[data-s]", root);
    chips.forEach(function (b) {
      b.addEventListener("click", function () {
        chips.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        onPick(b.dataset.s);
      });
    });
  }

  // ---------- a date page ----------
  var ad = $(".adpage");
  if (ad) {
    var rows = $$(".ad-row", ad), empty = $(".ad-empty", ad);
    chipsFor(ad, function (s) {
      var shown = 0;
      rows.forEach(function (r) { var on = !s || r.dataset.s === s; r.hidden = !on; if (on) shown++; });
      if (empty) empty.hidden = shown > 0;
    });
    return;
  }

  // ---------- the calendar ----------
  var page = $(".otdpage"); if (!page) return;
  page.classList.add("js");
  var cals = $$(".otd-cal"), months = $$(".otd-mo"), cells = $$(".otd-dy[data-md]"), panels = $$(".otd-pv");
  var nav = $(".otd-nav"), mname = $(".otd-mname"), hint = $(".otd-hint");
  var series = "", month = 0, sel = "";
  if (nav) nav.hidden = false;
  if (hint) hint.hidden = false;

  // One mark per series that has posted on a day (the server sends one per dispatch).
  function marks() {
    cells.forEach(function (c) {
      var seen = {}, posted = $$(".otd-marks i:not(.none)", c), shown = 0;
      posted.forEach(function (i) {
        var dup = seen[i.dataset.s]; seen[i.dataset.s] = true;
        var on = !dup && (!series || i.dataset.s === series);
        i.hidden = !on; if (on) shown++;
      });
      var label = c.getAttribute("aria-label").replace(/, .*$/, "");
      c.setAttribute("aria-label", label + (posted.length ? (shown ? ", has a dispatch" : "") : ", no dispatch yet") + (c.dataset.md === today ? ", today" : ""));
    });
    panels.forEach(function (p) {
      $$(".pv-post", p).forEach(function (r) { r.hidden = !!series && r.dataset.s !== series; });
    });
  }
  function showMonth(m) {
    month = (m + 11) % 12 + 1;
    cals.forEach(function (s) { s.hidden = +s.dataset.m !== month; });
    months.forEach(function (b) { b.setAttribute("aria-pressed", +b.dataset.m === month ? "true" : "false"); });
    if (mname) mname.textContent = MONTHS[month - 1];
  }
  function select(md) {
    sel = md;
    panels.forEach(function (p) { p.hidden = p.dataset.md !== md; });
    cells.forEach(function (c) { c.classList.toggle("sel", c.dataset.md === md); });
    var p = document.getElementById("pv-" + md);
    if (p) { var t = $(".pv-today", p); if (t) t.hidden = md !== today; }
  }

  cells.forEach(function (c) {
    if (c.dataset.md === today) c.classList.add("today");
    // First tap previews the day, a second tap on the same day opens its page.
    c.addEventListener("click", function (e) {
      if (sel === c.dataset.md) return;
      e.preventDefault();
      select(c.dataset.md);
      var p = document.getElementById("pv-" + c.dataset.md);
      if (p && window.matchMedia("(max-width: 899px)").matches) {
        var r = p.getBoundingClientRect();
        if (r.top > window.innerHeight - 120) p.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    });
  });
  months.forEach(function (b) { b.addEventListener("click", function () { showMonth(+b.dataset.m); }); });
  $$(".otd-arrow").forEach(function (b) { b.addEventListener("click", function () { showMonth(month + +b.dataset.step); }); });
  chipsFor(page, function (s) { series = s; marks(); });

  var q = +(new URLSearchParams(location.search).get("m") || 0);
  marks();
  showMonth(q >= 1 && q <= 12 ? q : +today.slice(0, 2));
  select(q && q !== +today.slice(0, 2) ? (q < 10 ? "0" : "") + q + "-01" : today);
})();
