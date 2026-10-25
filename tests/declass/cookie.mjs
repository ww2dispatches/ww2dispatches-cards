import { createHmac } from 'node:crypto';
const b64u = b => Buffer.from(b).toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
export function cookie(p){ const payload=b64u(JSON.stringify({p,e:Math.floor(Date.now()/1000)+86400*30})); return 'declass_session='+payload+'.'+b64u(createHmac('sha256','s').update('session:'+payload).digest()); }
