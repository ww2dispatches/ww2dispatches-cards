// The Campaign Shelf (board P1): shelve by theater or year, tap a spine to put the volume on the
// reading stand. On a phone the stand slides up from the bottom over a dim backdrop (tap the
// backdrop, the Put it back button, or Escape to slide it down); on a wide screen it sits beside
// the shelf. Data: the shelf-data block that renderer/site_pages.py writes into the page.
(function () {
  var vols = JSON.parse(document.getElementById("shelf-data").textContent);
  var byId = {}; vols.forEach(function (v) { byId[v.id] = v; });
  var shelves = document.getElementById("shelves"), stand = document.getElementById("stand"), scrim = document.getElementById("scrim");
  var note = shelves.querySelector(".shelfnote");
  var spines = {}; Array.prototype.forEach.call(document.querySelectorAll(".spine"), function (b) { spines[b.dataset.id] = b; });
  var esc = WW2.esc, phone = window.matchMedia("(max-width: 899px)");
  var picked = null, opener = null;
  var THEATERS = ["The Pacific", "The Western Front", "The Mediterranean", "The Eastern Front", "The Atlantic"];

  function status(v) {
    if (v.status === "live") {
      var now = WW2.now().getTime();
      if (now < Date.parse(v.start)) return { label: "Begins " + v.startLabel, cls: "gold" };
      if (now < Date.parse(v.end)) {
        var n = v.times.filter(function (t) { return Date.parse(t) <= now; }).length;
        return { label: "Now running · Day " + n + " of " + v.days, cls: "red" };
      }
      return { label: "Complete", cls: "green" };
    }
    if (v.status === "prep") return { label: "In preparation", cls: "gold" };
    return v.status === "planned" ? { label: "Planned", cls: "plain" } : { label: "Proposed", cls: "plain" };
  }

  // ---------- shelve by theater or year ----------
  function shelve(mode) {
    var groups = {}, names = [];
    vols.forEach(function (v) { var k = mode === "year" ? String(v.year) : v.theater; if (!groups[k]) { groups[k] = []; names.push(k); } groups[k].push(v); });
    names.sort(function (a, b) { return mode === "year" ? a - b : (THEATERS.indexOf(a) + 99) % 99 - (THEATERS.indexOf(b) + 99) % 99; });
    Array.prototype.forEach.call(shelves.querySelectorAll(".shelf"), function (s) { s.remove(); });
    names.forEach(function (name) {
      var sec = document.createElement("section"); sec.className = "shelf"; sec.setAttribute("aria-label", name);
      sec.innerHTML = "<h2>" + esc(name) + '</h2><div class="board hs"></div><div class="plank" aria-hidden="true"></div>';
      var board = sec.querySelector(".board");
      groups[name].forEach(function (v) { board.appendChild(spines[v.id]); });
      for (var i = 0; i < 4; i++) { var g = document.createElement("span"); g.className = "gap"; g.setAttribute("aria-hidden", "true"); board.appendChild(g); }
      shelves.insertBefore(sec, note);
    });
    Array.prototype.forEach.call(document.querySelectorAll(".modes .toggle"), function (b) { b.setAttribute("aria-pressed", b.dataset.mode === mode ? "true" : "false"); });
  }
  Array.prototype.forEach.call(document.querySelectorAll(".modes .toggle"), function (b) {
    b.addEventListener("click", function () { shelve(b.dataset.mode); });
  });

  // ---------- the reading stand ----------
  function fill(v) {
    var st = status(v), live = v.status === "live";
    var book = document.getElementById("st-book");
    book.style.setProperty("--cloth", v.cloth);
    if (live) {
      book.href = v.url; book.removeAttribute("aria-disabled"); book.setAttribute("aria-label", "Open " + v.title);
      book.innerHTML = '<span class="bk-vol">VOL. ' + esc(v.vol) + "</span>" +
        (v.cover ? '<span class="bk-plate"><img src="' + esc(v.cover) + '" alt="" style="object-position:' + esc(v.coverPos) + '"></span>' : "") +
        '<span class="bk-title">' + esc(v.title) + '</span><span class="bk-tap">Tap to open</span>';
    } else {
      book.removeAttribute("href"); book.setAttribute("aria-disabled", "true"); book.removeAttribute("aria-label");
      book.innerHTML = '<span class="bk-vol">VOL. ' + esc(v.vol) + '</span><span class="bk-title">' + esc(v.title) + '</span><span class="bk-stamp">' +
        ({ prep: "In prep", planned: "Planned" }[v.status] || "Proposed") + "</span>";
    }
    book.classList.toggle("stamped", !live);
    document.getElementById("st-theater").textContent = v.theater;
    document.getElementById("st-title").textContent = v.title;
    document.getElementById("st-dates").textContent = v.dates;
    var s = document.getElementById("st-status");
    s.textContent = st.label + " · " + (v.days ? v.days + " days" : "length to be set");
    s.className = "st-status " + st.cls;
    document.getElementById("st-blurb").textContent = v.blurb;
    var open = document.getElementById("st-open"); open.hidden = !live; if (live) open.href = v.url;
    var n = document.getElementById("st-note"); n.hidden = live; n.textContent = v.note || "";
    Object.keys(spines).forEach(function (id) { spines[id].classList.toggle("picked", id === v.id); });
  }

  function layout() {
    if (phone.matches) {
      stand.setAttribute("role", "dialog"); stand.setAttribute("aria-modal", "true");
      if (!stand.classList.contains("up")) { stand.hidden = true; scrim.hidden = true; }
    } else {
      stand.setAttribute("role", "region"); stand.removeAttribute("aria-modal");
      stand.hidden = false; scrim.hidden = true; stand.classList.remove("up", "down");
      document.body.classList.remove("sheet-open");
      if (!picked) { picked = vols[0].id; fill(vols[0]); }
    }
  }

  function pick(id, from) {
    picked = id; fill(byId[id]);
    if (!phone.matches) return;
    opener = from || spines[id];
    stand.hidden = false; scrim.hidden = false;
    stand.classList.remove("down"); scrim.classList.remove("down");
    void stand.offsetWidth;
    stand.classList.add("up"); scrim.classList.add("up");
    document.body.classList.add("sheet-open");
    stand.focus();
  }
  function close() {
    if (!phone.matches || stand.hidden) return;
    stand.classList.remove("up"); scrim.classList.remove("up");
    stand.classList.add("down"); scrim.classList.add("down");
    document.body.classList.remove("sheet-open");
    setTimeout(function () { stand.hidden = true; scrim.hidden = true; stand.classList.remove("down"); scrim.classList.remove("down"); }, 260);
    if (opener) opener.focus();
  }
  Object.keys(spines).forEach(function (id) { spines[id].addEventListener("click", function () { pick(id, spines[id]); }); });
  scrim.addEventListener("click", close);
  document.getElementById("st-close").addEventListener("click", close);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") close();
    if (e.key === "Tab" && phone.matches && !stand.hidden) {  // keep focus on the stand while it is up
      var f = stand.querySelectorAll("a[href], button:not([hidden])"), list = Array.prototype.filter.call(f, function (x) { return x.offsetParent; });
      if (!list.length) return;
      if (e.shiftKey && document.activeElement === list[0]) { e.preventDefault(); list[list.length - 1].focus(); }
      else if (!e.shiftKey && document.activeElement === list[list.length - 1]) { e.preventDefault(); list[0].focus(); }
    }
  });
  (phone.addEventListener ? phone.addEventListener("change", layout) : phone.addListener(layout));
  layout();
})();
