// Name This (board P4): the open case on top, then the Evidence Drawer of closed cases, newest
// first. The server hands over only puzzles that have posted, and the open case comes with no
// answer at all (functions/name-this/_middleware.js). A closed file shows the question card
// until the visitor opens it; "Open the file" swaps in the answer card and the answer.
//
// Speed (14 Nov 2026): cards are the site's light webp copies (a small thumbnail plus a 720 px
// copy, picked by screen size), every answer card is fetched quietly once the drawer is drawn,
// and opening a file changes only that folder, keeping the question card up until the answer
// card is ready, so the folder never goes blank.
(function () {
  var esc = WW2.esc, cases = [], cat = "All", shown = {}, cache = {};
  var CATS = ["All", "Ships", "Aircraft", "People", "Machines"];
  var SIZES = "(min-width: 900px) 230px, 46vw";
  function decode(s) { try { return decodeURIComponent(escape(atob(s))); } catch (e) { return ""; } }
  function srcset(full, thumb) { return thumb ? esc(thumb) + " 288w, " + esc(full) + " 720w" : ""; }
  function imgAttrs(full, thumb) {
    return 'src="' + esc(full) + '"' + (thumb ? ' srcset="' + srcset(full, thumb) + '" sizes="' + SIZES + '"' : "");
  }
  // Fetch an image ahead of time (the browser keeps it, so the swap is instant later).
  function preload(full, thumb) {
    var key = full; if (!full || cache[key]) return cache[key];
    var im = new Image();
    if (thumb) { im.sizes = SIZES; im.srcset = srcset(full, thumb).replace(/&amp;/g, "&"); }
    im.src = full;
    cache[key] = im.decode ? im.decode().catch(function () {}) : Promise.resolve();
    return cache[key];
  }

  function openCase(c) {
    var img = document.getElementById("oc-img");
    img.src = c.q;
    img.alt = "Name This, open case. Mystery photo. Clue: " + c.clue;
    document.getElementById("oc-posted").textContent = "Posted " + c.posted + " · " + c.place;
    document.getElementById("oc-clue").textContent = "Clue: " + c.clue;
    document.getElementById("oc-threads").href = c.threads;
    document.getElementById("oc-x").href = c.x;
    document.getElementById("opencase").hidden = false;
  }

  function fileHtml(c) {
    return '<li class="file" data-id="' + esc(c.id) + '"><span class="ftab">' + esc(c.case) + " · " + esc(c.posted) + "</span>" +
      '<div class="folder"><img ' + imgAttrs(c.q, c.qT) + ' alt="' + esc("Mystery photo, " + c.case + ". Clue: " + c.clue) +
      '" width="720" height="900" loading="lazy" decoding="async">' +
      '<button type="button" class="reveal" data-id="' + esc(c.id) + '" aria-expanded="false">Open the file</button></div></li>';
  }

  function drawer() {
    var closed = cases.filter(function (c) { return !c.open; });
    var chips = document.getElementById("chips");
    chips.innerHTML = CATS.map(function (k) {
      var n = k === "All" ? closed.length : closed.filter(function (c) { return c.cat === k; }).length;
      if (!n && k !== "All") return "";
      return '<button type="button" class="toggle" data-cat="' + k + '" aria-pressed="' + (cat === k) + '">' + k + " " + n + "</button>";
    }).join("");
    chips.hidden = closed.length < 2;
    document.getElementById("nofiles").hidden = closed.length > 0;
    var list = closed.filter(function (c) { return cat === "All" || c.cat === cat; });
    document.getElementById("files").innerHTML = list.map(fileHtml).join("");
    list.forEach(function (c) { if (shown[c.id]) setFile(c, true, true); });
  }

  // Open or close one folder in place. The answer card replaces the question card only once it has loaded.
  function setFile(c, on, instant) {
    var li = document.querySelector('.file[data-id="' + c.id + '"]'); if (!li) return;
    var img = li.querySelector("img"), btn = li.querySelector(".reveal"), ans = li.querySelector(".answer");
    btn.setAttribute("aria-expanded", on ? "true" : "false");
    btn.textContent = on ? "Close the file" : "Open the file";
    li.classList.toggle("open", on);
    var full = on && c.aImg ? c.aImg : c.q, thumb = on && c.aImg ? c.aT : c.qT;
    var swap = function () {
      if (li.classList.contains("open") !== on) return;  // tapped again while loading
      if (thumb) { img.sizes = SIZES; img.srcset = srcset(full, thumb).replace(/&amp;/g, "&"); } else img.removeAttribute("srcset");
      img.src = full;
      img.alt = on ? "Answer card: " + decode(c.a) : "Mystery photo, " + c.case + ". Clue: " + c.clue;
    };
    if (instant) swap(); else { btn.classList.add("busy"); (preload(full, thumb) || Promise.resolve()).then(function () { btn.classList.remove("busy"); swap(); }); }
    if (on && !ans) {
      var d = document.createElement("div"); d.className = "answer";
      d.innerHTML = "<small>Answer</small><b>" + esc(decode(c.a)) + "</b><span>" + esc(c.hist) + " · " + esc(c.place) + "</span>";
      btn.parentNode.insertBefore(d, btn);
    } else if (!on && ans) ans.remove();
  }

  document.getElementById("chips").addEventListener("click", function (e) {
    var b = e.target.closest("button[data-cat]"); if (!b) return;
    cat = b.dataset.cat; drawer();
  });
  document.getElementById("files").addEventListener("click", function (e) {
    var b = e.target.closest("button.reveal"); if (!b) return;
    var c = cases.filter(function (x) { return x.id === b.dataset.id; })[0]; if (!c) return;
    shown[c.id] = !shown[c.id];
    setFile(c, shown[c.id], false);
  });

  fetch("/name-this/cases.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (data) {
    cases = data.cases || [];
    var open = cases.filter(function (c) { return c.open; })[0];
    if (open) openCase(open);
    drawer();
    // Quietly fetch every answer card once the page has settled, so opening a file is instant.
    var warm = function () { cases.forEach(function (c) { if (!c.open && c.aImg) preload(c.aImg, c.aT); }); };
    if (window.requestIdleCallback) requestIdleCallback(warm, { timeout: 2500 }); else setTimeout(warm, 1200);
  }).catch(function () { document.getElementById("nofiles").hidden = false; });
})();
