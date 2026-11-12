// Name This (board P4): the open case on top, then the Evidence Drawer of closed cases, newest
// first. The server hands over only puzzles that have posted, and the open case comes with no
// answer at all (functions/name-this/_middleware.js). A closed file shows the question card
// until the visitor opens it; "Open the file" swaps in the answer card and the answer.
(function () {
  var esc = WW2.esc, cases = [], cat = "All", shown = {};
  var CATS = ["All", "Ships", "Aircraft", "People", "Machines"];
  function decode(s) { try { return decodeURIComponent(escape(atob(s))); } catch (e) { return ""; } }

  function openCase(c) {
    document.getElementById("oc-img").src = c.q;
    document.getElementById("oc-img").alt = "Name This, open case. Mystery photo. Clue: " + c.clue;
    document.getElementById("oc-posted").textContent = "Posted " + c.posted + " · " + c.place;
    document.getElementById("oc-clue").textContent = "Clue: " + c.clue;
    document.getElementById("oc-threads").href = c.threads;
    document.getElementById("oc-x").href = c.x;
    document.getElementById("opencase").hidden = false;
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
    var list = closed.filter(function (c) { return cat === "All" || c.cat === cat; });
    document.getElementById("nofiles").hidden = closed.length > 0;
    document.getElementById("files").innerHTML = list.map(function (c) {
      var on = !!shown[c.id], ans = c.a ? decode(c.a) : "";
      return '<li class="file' + (on ? " open" : "") + '"><span class="ftab">' + esc(c.case) + " · " + esc(c.posted) + "</span>" +
        '<div class="folder"><img src="' + esc(on && c.aImg ? c.aImg : c.q) + '" alt="' +
        esc(on ? "Answer card: " + ans : "Mystery photo, " + c.case + ". Clue: " + c.clue) + '" width="1080" height="1350" loading="lazy">' +
        (on ? '<div class="answer"><small>Answer</small><b>' + esc(ans) + "</b><span>" + esc(c.hist) + " · " + esc(c.place) + "</span></div>" : "") +
        '<button type="button" class="reveal" data-id="' + esc(c.id) + '" aria-expanded="' + on + '">' + (on ? "Close the file" : "Open the file") + "</button></div></li>";
    }).join("");
  }

  document.getElementById("chips").addEventListener("click", function (e) {
    var b = e.target.closest("button[data-cat]"); if (!b) return;
    cat = b.dataset.cat; drawer();
  });
  document.getElementById("files").addEventListener("click", function (e) {
    var b = e.target.closest("button.reveal"); if (!b) return;
    var id = b.dataset.id; shown[id] = !shown[id]; drawer();
    var again = document.querySelector('button.reveal[data-id="' + id + '"]'); if (again) again.focus();
  });

  fetch("/name-this/cases.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (data) {
    cases = data.cases || [];
    var open = cases.filter(function (c) { return c.open; })[0];
    if (open) openCase(open);
    drawer();
  }).catch(function () { document.getElementById("nofiles").hidden = false; });
})();
