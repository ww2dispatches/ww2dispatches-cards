// The Declass panel on the ww2dispatches.com home page (Declass Home Panel mockup). Four looks:
// new visitor, file ready, all opened, signed out. It asks the game server; until launch the
// server only answers testers (the key this browser remembers from the private link), so the
// public never sees the panel before then.
(function () {
  var panel = document.getElementById('dcl');
  if (!panel || !window.fetch) return;
  var key = '';
  try { key = localStorage.getItem('declass_key') || ''; } catch (e) {}
  var hasStarter = false;
  try { hasStarter = Boolean(localStorage.getItem('declass_starter')); } catch (e) {}
  function get(path) {
    return fetch('/api/' + path, { headers: { 'x-declass-key': key }, credentials: 'same-origin' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
  }
  function at(iso) { var d = new Date(iso), t = new Date(), tm = new Date(); tm.setDate(t.getDate() + 1);
    var time = d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    return d.toDateString() === t.toDateString() ? 'today ' + time : d.toDateString() === tm.toDateString() ? 'tomorrow ' + time : d.toLocaleDateString([], { weekday: 'short' }) + ' ' + time; }
  function etHour(iso) { return Number(new Date(iso).toLocaleString('en-US', { timeZone: 'America/New_York', hour: 'numeric', hourCycle: 'h23' })); }
  function set(cls, stamp, title, sub, go, quiet) {
    panel.className = 'dcl ' + cls;
    document.getElementById('dcl-stamp').textContent = stamp;
    document.getElementById('dcl-t').innerHTML = title;
    document.getElementById('dcl-s').textContent = sub;
    var b = document.getElementById('dcl-go');
    b.textContent = go; b.classList.toggle('quiet', Boolean(quiet));
    panel.hidden = false;
  }
  get('config').then(function (cfg) {
    if (!cfg.open) return;
    return get('state').then(function (s) {
      var p = s.player, next = s.next ? 'Next file ' + at(s.next) + '.' : '';
      if (!p && !hasStarter) {
        return set('waiting', 'FREE TO PLAY', 'Open your first file',
          'A sealed file comes with every dispatch we post. Collect the cards. Your first pack of five is free.', 'Play free');
      }
      if (!p) return set('waiting', 'PLAY', 'File waiting', 'Sign in to open it and keep your streak.', 'Sign in to open it');
      var ready = s.envelopes.filter(function (e) { return !e.opened; });
      var comm = s.commemorative.filter(function (e) { return !e.opened; });
      var n = ready.length + comm.length + (s.priority || 0) + (p.starterDone ? 0 : 1);
      var streak = p.streak ? p.streak + ' day streak. ' : '';
      if (s.waiting && s.waiting.length) return set('waiting', 'PLAY', 'Cards waiting', s.waiting.length + (s.waiting.length === 1 ? ' card' : ' cards') + ' waiting to be turned. ' + streak, 'Turn them');
      if (n) {
        var isToday = function (e) { return new Date(e.at).toDateString() === new Date().toDateString(); };
        var todays = ready.filter(isToday);
        var name = comm.length ? 'Commemorative file · ' + comm[0].name : todays.length ? (etHour(todays[todays.length - 1].at) < 12 ? 'Morning file ready' : 'Evening file ready') : ready.length ? 'Last call' : s.priority ? 'Priority envelope ready' : !p.starterDone ? 'Starter pack ready' : 'Files ready';
        return set('waiting' + (comm.length ? ' comm' : ''), 'PLAY', name + ' <em>' + n + ' ready</em>', streak + next, 'Declassify it');
      }
      return set('opened', 'PLAY', 'All declassed', streak + next, 'Open your dossier', true);
    });
  }).catch(function () {});
})();
