// Renders extra Instagram carousel slides (1080 x 1350) for a dispatch.
// Usage: node renderer/slides.js <dispatch-id> [...]
// The dispatch JSON needs a "slides" array: [{photo: "photos/....jpg", caption: "short line", credit: "source"}].
// Slide 1 of the carousel is always the normal card (cards/dispatch-NNN-instagram.jpg).
// Output: cards/dispatch-NNN-slide-2.jpg, -slide-3.jpg, ... on cream paper with the series color rule.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const CHROME = process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";

function drawSlide(p, slide, photoUrl, idx, total) {
  return (async () => {
    await Promise.all(["700 10px Oswald","600 10px Oswald",'400 10px "Special Elite"'].map(f=>document.fonts.load(f)));
    const img = await new Promise((ok,bad)=>{const i=new Image(); i.onload=()=>ok(i); i.onerror=bad; i.src=photoUrl;});
    const W=1080,H=1350, cv=document.createElement("canvas"); cv.width=W; cv.height=H;
    const ctx=cv.getContext("2d"), u=W/100, m=3.2*u, topH=10*u;
    const [, accent]=SERIES[SKEY[(p.series||"").toLowerCase()]||"battle"];
    ctx.fillStyle=PAPER; ctx.fillRect(0,0,W,H);
    if(!grainTile) grainTile=makeGrain();
    ctx.fillStyle=ctx.createPattern(grainTile,"repeat"); ctx.fillRect(0,0,W,H);
    const vg=ctx.createRadialGradient(W/2,H/2,Math.min(W,H)*.35,W/2,H/2,Math.max(W,H)*.72);
    vg.addColorStop(0,"rgba(120,88,48,0)"); vg.addColorStop(1,"rgba(120,88,48,.24)"); ctx.fillStyle=vg; ctx.fillRect(0,0,W,H);

    ctx.textBaseline="alphabetic"; ctx.textAlign="left";
    ctx.fillStyle=INK; ctx.font=`700 ${3.4*u}px Oswald`; ctx.letterSpacing=`${.02*3.4*u}px`;
    ctx.fillText("WW2 DISPATCHES",m,6.4*u);
    ctx.textAlign="right"; ctx.fillStyle=NAVY; ctx.font=`400 ${2.4*u}px "Special Elite"`; ctx.letterSpacing=`${.04*2.4*u}px`;
    ctx.fillText("Dispatch "+pad(p.num)+"  ·  "+idx+" / "+total,W-m,6.4*u);
    ctx.fillStyle=accent; ctx.fillRect(m,topH-1.6*u,W-2*m,.5*u);

    // Photo fitted whole (no crop); photo and caption sit together as one block, centered
    ctx.font=`600 ${3.6*u}px Oswald`; ctx.letterSpacing=`${.02*3.6*u}px`;
    const lines=wrap(ctx,(slide.caption||"").toUpperCase(),W-2*m,2);
    const capH=lines.length?(3*u+lines.length*4.4*u):0;
    const px=m,pw=W-2*m,areaTop=topH+1*u,areaH=H-areaTop-8*u;
    const s=Math.min(pw/img.naturalWidth,(areaH-capH)/img.naturalHeight), dw=img.naturalWidth*s, dh=img.naturalHeight*s;
    const dx=px+(pw-dw)/2, dy=areaTop+(areaH-dh-capH)/2;
    ctx.filter="sepia(.12) contrast(1.04)"; ctx.drawImage(img,dx,dy,dw,dh); ctx.filter="none";
    ctx.lineWidth=.3*u; ctx.strokeStyle=INK; ctx.strokeRect(dx+.15*u,dy+.15*u,dw-.3*u,dh-.3*u);

    ctx.textAlign="left"; ctx.fillStyle=INK;
    lines.forEach((ln,i)=>ctx.fillText(ln,m,dy+dh+6.2*u+i*4.4*u));
    ctx.fillStyle=NAVY; ctx.font=`400 ${2.2*u}px "Special Elite"`; ctx.letterSpacing=`${.03*2.2*u}px`;
    ctx.fillText(slide.credit||"",m,H-3*u);
    ctx.textAlign="right"; ctx.fillText("@ww2dispatches",W-m,H-3*u);
    return cv.toDataURL("image/jpeg",.92);
  })();
}

(async () => {
  const ids = process.argv.slice(2);
  if (!ids.length) { console.error("Give one or more dispatch ids."); process.exit(1); }
  const browser = await chromium.launch({ executablePath: fs.existsSync(CHROME) ? CHROME : undefined });
  const page = await browser.newPage();
  await page.goto("file://" + path.join(__dirname, "card.html"));
  // card.html keeps pad() inside its script scope; it is a global function, so it is available here.
  for (const id of ids) {
    const p = JSON.parse(fs.readFileSync(path.join(ROOT, "dispatches", id + ".json"), "utf8"));
    const slides = p.slides || [];
    const total = slides.length + 1;
    for (let i = 0; i < slides.length; i++) {
      const sl = slides[i];
      const url = "data:image/jpeg;base64," + fs.readFileSync(path.join(ROOT, sl.photo)).toString("base64");
      const out = await page.evaluate(`(${drawSlide.toString()})(${JSON.stringify(p)}, ${JSON.stringify(sl)}, ${JSON.stringify(url)}, ${i + 2}, ${total})`);
      const file = path.join(ROOT, "cards", `dispatch-${String(p.num).padStart(3, "0")}-slide-${i + 2}.jpg`);
      fs.writeFileSync(file, Buffer.from(out.split(",")[1], "base64"));
      console.log("wrote", path.relative(ROOT, file));
    }
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
