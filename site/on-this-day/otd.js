// On this day (/on-this-day/, 15 Nov 2026): the calendar, the series filters and the Name This drawer.
// The page itself comes from renderer/dispatch_pages.py and the server has already removed anything that
// has not posted yet, so this script only shows and hides what is there. Without it every month and
// every date shows in a long list, which is also what search engines read.
(function () {
  var W = window.WW2 || {};
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };
  var page = $(".otdpage"); if (!page) return;
  page.classList.add("js");
  var cells = $$(".otd-dy[data-md]"), panels = $$(".otd-day"), cals = $$(".otd-cal"), months = $$(".otd-mo");
  var series = "", current = "";
  var panel = function (md) { return document.getElementById("d-" + md); };

  // A date is open when at least one of its dispatches has posted and matches the series filter.
  function refresh() {
    cells.forEach(function (c) {
      var dots = $$(".otd-dots i", c), shown = 0;
      dots.forEach(function (i) { var on = !series || i.dataset.s === series; i.hidden = !on; if (on) shown++; });
      c.classList.toggle("has", shown > 0);
      c.tabIndex = shown ? 0 : -1;
      c.setAttribute("aria-label", c.getAttribute("aria-label").replace(/, \d+ dispatch(es)?$/, "") + (shown ? ", " + shown + (shown === 1 ? " dispatch" : " dispatches") : ""));
    });
    $$(".dmini", page).forEach(function (li) { li.hidden = !!series && li.dataset.s !== series; });
    panels.forEach(function (p) { p.classList.toggle("empty", !$$(".dmini", p).some(function (li) { return !li.hidden; })); });
    months.forEach(function (b) {
      var m = b.dataset.m, has = cells.some(function (c) { return c.classList.contains("has") && +c.dataset.md.slice(0, 2) === +m; });
      b.disabled = !has;
    });
  }
  function showMonth(m) {
    cals.forEach(function (s) { s.hidden = s.dataset.m !== String(m); });
    months.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.m === String(m) ? "true" : "false"); });
  }
  function select(md, push) {
    var p = panel(md); if (!p) return;
    current = md;
    panels.forEach(function (x) { x.hidden = x !== p; });
    cells.forEach(function (c) { if (c.dataset.md === md) c.setAttribute("aria-current", "date"); else c.removeAttribute("aria-current"); });
    showMonth(+md.slice(0, 2));
    if (push) history.replaceState(null, "", "#d-" + md);
  }
  function firstOpen() {
    var today = (W.denver ? W.denver().date : new Date().toISOString().slice(0, 10)).slice(5);
    var hash = (location.hash.match(/^#d-(\d\d-\d\d)$/) || [])[1];
    var open = function (md) { var c = cells.filter(function (x) { return x.dataset.md === md; })[0]; return c && c.classList.contains("has"); };
    if (hash && open(hash)) return hash;
    if (open(today)) return today;
    var past = cells.filter(function (c) { return c.classList.contains("has") && c.dataset.md <= today; });
    if (past.length) return past[past.length - 1].dataset.md;
    var any = cells.filter(function (c) { return c.classList.contains("has"); });
    return any.length ? any[any.length - 1].dataset.md : "";
  }
  cells.forEach(function (c) {
    c.addEventListener("click", function (e) {
      e.preventDefault();
      if (!c.classList.contains("has")) return;
      select(c.dataset.md, true);
      if (window.matchMedia("(max-width: 899px)").matches) panel(c.dataset.md).scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
  months.forEach(function (b) { b.addEventListener("click", function () { showMonth(b.dataset.m); }); });
  $$(".otd-chips .toggle[data-s]").forEach(function (b) {
    b.addEventListener("click", function () {
      series = b.dataset.s;
      $$(".otd-chips .toggle[data-s]").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      refresh();
      if (current && panel(current).classList.contains("empty")) { var md = firstOpen(); if (md) select(md, true); }
    });
  });
  window.addEventListener("hashchange", function () { var md = (location.hash.match(/^#d-(\d\d-\d\d)$/) || [])[1]; if (md) select(md, false); });

  // The Name This drawer: the newest cases from the same data the Name This page uses (the server
  // never sends the open case's answer). Loaded the first time the drawer opens.
  var ntBtn = $(".otd-ntbtn"), nt = $("#otd-nt"), loaded = false;
  if (ntBtn && nt) ntBtn.addEventListener("click", function () {
    var open = nt.hidden;
    nt.hidden = !open; ntBtn.setAttribute("aria-expanded", open ? "true" : "false"); ntBtn.setAttribute("aria-pressed", open ? "true" : "false");
    if (!open || loaded) return;
    loaded = true;
    fetch("/name-this/cases.json").then(function (r) { return r.json(); }).then(function (data) {
      var list = (data.cases || []).slice(0, 3), esc = W.esc || String;
      $("#otd-ntlist").innerHTML = list.length ? list.map(function (c) {
        return '<li><a href="/name-this/"><b>' + esc(c.posted) + "</b><span>" + (c.open ? "Open case, make your guess" : "Answer is out") + "</span></a></li>";
      }).join("") : "<li><span>The first case opens soon.</span></li>";
    }).catch(function () { $("#otd-ntlist").innerHTML = ""; });
  });

  refresh();
  var md = firstOpen();
  if (md) select(md, false); else if (cals[0]) showMonth(cals[0].dataset.m);
})();
