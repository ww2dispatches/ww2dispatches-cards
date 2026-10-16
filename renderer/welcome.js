// Renders the pinned "Start here" welcome card from welcome.json into cards/.
// Usage: node renderer/welcome.js
// Reuses card.html for fonts, paper grain, and colors. Four photo tiles, one per series.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const CHROME = process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";

function drawWelcome(cfg, photos) {
  return (async () => {
    await Promise.all(["700 10px Oswald","600 10px Oswald",'400 10px "Special Elite"'].map(f=>document.fonts.load(f)));
    const imgs = await Promise.all(photos.map(u=>new Promise((ok,bad)=>{const i=new Image(); i.onload=()=>ok(i); i.onerror=bad; i.src=u;})));
    function tileStamp(ctx,u,label,accent,x,y){
      ctx.font=`600 ${2.3*u}px Oswald`; ctx.letterSpacing=`${.14*2.3*u}px`;
      const tw=ctx.measureText(label).width, sw=tw+3.2*u, sh=4*u;
      ctx.save(); ctx.translate(x+sw/2,y+sh/2); ctx.rotate(-2*Math.PI/180);
      ctx.fillStyle=accent; ctx.fillRect(-sw/2,-sh/2,sw,sh);
      ctx.strokeStyle=PAPER; ctx.lineWidth=.26*u; ctx.strokeRect(-sw/2+.45*u,-sh/2+.45*u,sw-.9*u,sh-.9*u);
      ctx.fillStyle=PAPER; ctx.textAlign="center"; ctx.textBaseline="middle"; ctx.fillText(label,.06*u,.12*u);
      const r=rng(31);
      for(let i=0;i<Math.floor(sw*sh/(u*u)*5);i++){ctx.globalAlpha=.12+r()*.3; const rr=(.04+r()*r()*.2)*u; ctx.beginPath(); ctx.arc(-sw/2+r()*sw,-sh/2+r()*sh,rr,0,Math.PI*2); ctx.fill();}
      ctx.globalAlpha=1; ctx.restore();
    }
    function bigStamp(ctx,u,label,accent,cx,cy){
      ctx.font=`600 ${2.9*u}px Oswald`; ctx.letterSpacing=`${.14*2.9*u}px`;
      const tw=ctx.measureText(label).width, sw=tw+4*u, sh=5*u;
      ctx.save(); ctx.translate(cx-sw/2,cy); ctx.rotate(-2*Math.PI/180);
      ctx.fillStyle=accent; ctx.fillRect(-sw/2,-sh/2,sw,sh);
      ctx.strokeStyle=PAPER; ctx.lineWidth=.32*u; ctx.strokeRect(-sw/2+.55*u,-sh/2+.55*u,sw-1.1*u,sh-1.1*u);
      ctx.fillStyle=PAPER; ctx.textAlign="center"; ctx.textBaseline="middle"; ctx.fillText(label,.07*u,.15*u);
      const r=rng(31);
      for(let i=0;i<Math.floor(sw*sh/(u*u)*5);i++){ctx.globalAlpha=.12+r()*.3; const rr=(.04+r()*r()*.22)*u; ctx.beginPath(); ctx.arc(-sw/2+r()*sw,-sh/2+r()*sh,rr,0,Math.PI*2); ctx.fill();}
      ctx.globalAlpha=1; ctx.restore();
    }
    const out={};
    for (const [kind,W,H] of [["x",1600,1440],["instagram",1080,1350]]) {
      const cv=document.createElement("canvas"); cv.width=W; cv.height=H;
      const ctx=cv.getContext("2d"), u=W/100, m=3.2*u, topH=14.5*u, botH=(kind==="x"?17:19)*u;
      ctx.fillStyle=PAPER; ctx.fillRect(0,0,W,H);
      if(!grainTile) grainTile=makeGrain();
      ctx.fillStyle=ctx.createPattern(grainTile,"repeat"); ctx.fillRect(0,0,W,H);
      const vg=ctx.createRadialGradient(W/2,H/2,Math.min(W,H)*.35,W/2,H/2,Math.max(W,H)*.72);
      vg.addColorStop(0,"rgba(120,88,48,0)"); vg.addColorStop(1,"rgba(120,88,48,.24)"); ctx.fillStyle=vg; ctx.fillRect(0,0,W,H);

      // Top band
      ctx.textAlign="left"; ctx.textBaseline="alphabetic";
      ctx.fillStyle=INK; ctx.font=`700 ${4.4*u}px Oswald`; ctx.letterSpacing=`${.02*4.4*u}px`;
      ctx.fillText("WW2 DISPATCHES",m,7.7*u);
      ctx.fillStyle=NAVY; ctx.font=`400 ${2.4*u}px "Special Elite"`; ctx.letterSpacing=`${.04*2.4*u}px`;
      ctx.fillText(cfg.subline,m,11.3*u);
      bigStamp(ctx,u,cfg.stamp,"#B04A3E",W-m-.4*u,topH/2+.2*u);

      // 2 x 2 photo grid, one tile per series
      const gap=1.2*u, gx=m, gy=topH, gw=W-2*m, gh=H-topH-botH;
      const tw=(gw-gap)/2, th=(gh-gap)/2;
      cfg.tiles.forEach((t,i)=>{
        const img=imgs[i], x=gx+(i%2)*(tw+gap), y=gy+Math.floor(i/2)*(th+gap);
        const z=(t.zoom||100)/100, s=Math.max(tw/img.naturalWidth,th/img.naturalHeight)*z;
        const dw=img.naturalWidth*s, dh=img.naturalHeight*s;
        const fx=t.focusX!=null?t.focusX:50, fy=t.focusY!=null?t.focusY:40;
        ctx.save(); ctx.beginPath(); ctx.rect(x,y,tw,th); ctx.clip();
        ctx.filter="sepia(.12) contrast(1.04)"; ctx.drawImage(img,x-(dw-tw)*(fx/100),y-(dh-th)*(fy/100),dw,dh); ctx.filter="none"; ctx.restore();
        ctx.lineWidth=.3*u; ctx.strokeStyle=INK; ctx.strokeRect(x+.15*u,y+.15*u,tw-.3*u,th-.3*u);
        const [name,accent]=SERIES[SKEY[t.series]];
        tileStamp(ctx,u,name.toUpperCase(),accent,x+1.4*u,y+th-5.6*u);
      });

      // Bottom band
      const head=cfg.headline, hb=H-botH+8*u;
      ctx.textAlign="left"; ctx.fillStyle=INK; ctx.font=`700 ${6.2*u}px Oswald`; ctx.letterSpacing=`${.01*6.2*u}px`;
      ctx.fillText(head,m,hb);
      ctx.fillStyle=NAVY; ctx.font=`400 ${2.5*u}px "Special Elite"`; ctx.letterSpacing=`${.04*2.5*u}px`;
      const lines=wrap(ctx,cfg.line,kind==="x"?(W-2*m)*.62:(W-2*m),2);
      lines.forEach((ln,i)=>ctx.fillText(ln,m,hb+3.8*u+i*3.3*u));
      ctx.textAlign="right"; ctx.font=`400 ${2.4*u}px "Special Elite"`; ctx.letterSpacing=`${.02*2.4*u}px`;
      ctx.fillText("@ww2dispatches",W-m,H-2.6*u);
      out[kind]=cv.toDataURL("image/jpeg",.92);
    }
    return out;
  })();
}

(async () => {
  const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, "welcome.json"), "utf8"));
  const photos = cfg.tiles.map(t => "data:image/jpeg;base64," + fs.readFileSync(path.join(ROOT, t.photo)).toString("base64"));
  const browser = await chromium.launch({ executablePath: fs.existsSync(CHROME) ? CHROME : undefined });
  const page = await browser.newPage();
  await page.goto("file://" + path.join(__dirname, "card.html"));
  const out = await page.evaluate(`(${drawWelcome.toString()})(${JSON.stringify(cfg)}, ${JSON.stringify(photos)})`);
  for (const kind of ["x", "instagram"]) {
    const file = path.join(ROOT, "cards", `welcome-${kind}.jpg`);
    fs.writeFileSync(file, Buffer.from(out[kind].split(",")[1], "base64"));
    console.log("wrote", path.relative(ROOT, file));
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
