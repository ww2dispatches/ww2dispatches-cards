// The automatic player from the test bench (5 Nov 2026), rewritten against the engine. It plays worse
// than a person, so its win rates are for comparing setups, not for promising players anything.
import * as E from '../../site/declass/campaigns/engine.js';

export function playRun(campaign, chapter, deck, seed) {
  const st = E.newRun(campaign, chapter, deck, seed);
  const choices = [];
  const go = c => { const r = E.act(campaign, st, c); if (!r.ok) throw new Error(JSON.stringify(c) + ': ' + r.error); choices.push(c); };
  go({ a: 'keep' });
  let guard = 0;
  while (!st.over && guard++ < 400) {
    if (st.phase === 'enemy') {
      const ul = st.hand.find(i => st.cards[i].series === 'state' && st.cards[i].keyword === 'ultimatum' && !E.whyNot(campaign, st, i));
      if (ul !== undefined) {
        const ts = E.ultimatumTargets(st).sort((a, b) => E.incoming(st, b) - E.incoming(st, a));
        if (ts.length && E.incoming(st, ts[0]) >= 2) go({ a: 'ultimatum', card: ul, unit: ts[0].uid });
      }
      const inc = E.alive(st).filter(u => E.incoming(st, u) > 0).sort((a, b) => E.incoming(st, b) - E.incoming(st, a));
      const used = new Set();
      for (const u of inc) {
        const a = E.incoming(st, u);
        const free = st.line.filter(m => E.canBlock(m) && !used.has(m.uid));
        let m = free.find(m => m.op == null && m.arm > a) || free.find(m => m.arm > a) || (st.resolve - a <= 4 ? free.slice().sort((x, y) => y.arm - x.arm)[0] : null);
        let ms = m ? [m] : (st.resolve - a <= 4 ? free.slice(0, 3) : []);
        if (ms.length) { ms.forEach(x => used.add(x.uid)); go({ a: 'block', unit: u.uid, machines: ms.map(x => x.uid) }); }
      }
      go({ a: 'lock' }); continue;
    }
    let prog = true;
    while (prog) {
      prog = false;
      const order = st.hand.slice().sort((a, b) => { const r = { blue: 0, battle: 1, state: 2, home: 3 }; return r[st.cards[a].series] - r[st.cards[b].series] || st.cards[b].value - st.cards[a].value; });
      for (const i of order) {
        const c = st.cards[i]; if (E.whyNot(campaign, st, i)) continue;
        if (c.series === 'blue') { go({ a: 'place', card: i }); prog = true; break; }
        if (c.series === 'battle') { const ms = st.line.filter(m => E.fitsMachine(st, m, c) && !m.fresh && E.opValue(st, m) < c.value); if (!ms.length) continue; go({ a: 'attach', card: i, machine: ms[0].uid }); prog = true; break; }
        if (c.series === 'state') {
          if (c.keyword === 'ultimatum') continue;
          if (c.keyword === 'lend') go({ a: 'lend', card: i, pick: E.lendable(campaign, st)[0] });
          else if (c.keyword === 'evac') go({ a: 'evac', card: i, pick: E.evacuable(st)[0] });
          else go({ a: 'backchannel', card: i });
          prog = true; break;
        }
        if (c.series === 'home') {
          if (st.resolve > 7 && !st.line.some(m => m.arm < st.cards[m.card].value - 1)) continue;
          if (st.resolve < st.rules.resolveCap) go({ a: 'rally', card: i, to: 'resolve' });
          else go({ a: 'rally', card: i, to: st.line.find(m => m.arm < st.cards[m.card].value).uid });
          prog = true; break;
        }
      }
    }
    const threat = E.alive(st).map(u => E.coming(st, u)).filter(a => a > 0).sort((a, b) => b - a);
    const unarmed = st.line.filter(m => m.op == null || m.fresh || m.state !== 'ready');
    const need = threat.slice(unarmed.length);
    const armed = st.line.filter(m => E.canAttack(st, m)).sort((a, b) => b.arm - a.arm);
    for (const a of need) { if (!armed.length) break; if (a >= 2 || st.resolve - a <= 5) armed.shift(); }
    for (const m of armed) { const ts = E.targetsFor(st, m); if (!ts.length) break; go({ a: 'attack', machine: m.uid, unit: ts[0].uid }); }
    go({ a: 'end' });
  }
  return { state: st, choices };
}
