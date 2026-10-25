import { rollFinish, rollLiving } from '../../functions/_lib/odds.js';
const N = 2_000_000;
for (const v of ['still','living']) {
  const c = {}; for (let i=0;i<N;i++){ const f=rollFinish(v); c[f]=(c[f]||0)+1; }
  console.log(v, Object.fromEntries(Object.entries(c).map(([k,x])=>[k,(100*x/N).toFixed(3)+'%'])));
}
let l=0; for (let i=0;i<N;i++) if (rollLiving()) l++; console.log('living rate', (l/N).toFixed(4), 'expected', (1/6).toFixed(4));
