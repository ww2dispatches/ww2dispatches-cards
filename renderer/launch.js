// Renders the one time Weekly Dispatch launch announcement card (no dispatch number) into cards/.
// Usage: node renderer/launch.js
// Reuses card.html for fonts, paper grain, colors, and the rubber stamp. Photo: the home page D-Day photo.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const CHROME = process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";

function drawLaunch(photoUrl, W, H) {
  return (async () => {
    await Promise.all(["700 10px Oswald","600 10px Oswald",'400 10px "Special Elite"'].map(f=>document.fonts.load(f)));
    const img = await new Promise((ok,bad)=>{const i=new Image(); i.onload=()=>ok(i); i.onerror=bad; i.src=photoUrl;});
    const cv=document.createElement("canvas"); cv.width=W; cv.height=H;
    const ctx=cv.getContext("2d"), u=W/100, m=4*u, TEAL="#2B6A6C";
    ctx.fillStyle=PAPER; ctx.fillRect(0,0,W,H);
    if(!grainTile) grainTile=makeGrain();
    ctx.fillStyle=ctx.createPattern(grainTile,"repeat"); ctx.fillRect(0,0,W,H);
    const vg=ctx.createRadialGradient(W/2,H/2,Math.min(W,H)*.35,W/2,H/2,Math.max(W,H)*.72);
    vg.addColorStop(0,"rgba(120,88,48,0)"); vg.addColorStop(1,"rgba(120,88,48,.24)"); ctx.fillStyle=vg; ctx.fillRect(0,0,W,H);
    // top band
    ctx.textBaseline="alphabetic"; ctx.textAlign="left"; ctx.fillStyle=INK;
    ctx.font=`700 ${4.2*u}px Oswald`; ctx.letterSpacing=`${.02*4.2*u}px`; ctx.fillText("WW2 DISPATCHES",m,8*u);
    ctx.fillStyle=NAVY; ctx.font=`400 ${2.5*u}px "Special Elite"`; ctx.letterSpacing="0px"; ctx.fillText("Incoming dispatch · Priority",m,11.6*u);
    stamp(ctx,u,"NOW LIVE",TEAL,W-m,8*u);
    // photo window
    const top=15*u, bottomBand=(H/W>1.1?33:30)*u, ph=H-top-bottomBand, pw=W-2*m;
    const s=Math.max(pw/img.naturalWidth,ph/img.naturalHeight), dw=img.naturalWidth*s, dh=img.naturalHeight*s;
    ctx.save(); ctx.beginPath(); ctx.rect(m,top,pw,ph); ctx.clip();
    ctx.filter="sepia(.15) contrast(1.05)"; ctx.drawImage(img,m+(pw-dw)/2,top+(ph-dh)*.45,dw,dh); ctx.filter="none"; ctx.restore();
    ctx.strokeStyle=INK; ctx.lineWidth=.35*u; ctx.strokeRect(m,top,pw,ph);
    // bottom band
    let y=top+ph+8*u;
    ctx.fillStyle=INK; ctx.font=`700 ${7*u}px Oswald`; ctx.letterSpacing=`${.01*7*u}px`; ctx.fillText("THE WEEKLY DISPATCH",m,y);
    y+=5*u; ctx.fillStyle=NAVY; ctx.font=`400 ${2.9*u}px "Special Elite"`; ctx.fillText("One story from the war, told in full. Every Sunday.",m,y);
    y+=6*u; ctx.fillStyle=TEAL; ctx.font=`600 ${3.6*u}px Oswald`; ctx.letterSpacing=`${.04*3.6*u}px`; ctx.fillText("SIGN UP FREE AT THE LINK IN OUR BIO",m,y);
    ctx.textAlign="right"; ctx.fillStyle=NAVY; ctx.font=`400 ${2.3*u}px "Special Elite"`; ctx.letterSpacing="0px";
    ctx.fillText("@ww2dispatches",W-m,H-(H/W>1.1?3:6)*u);
    return cv.toDataURL("image/jpeg",.9);
  })();
}

(async () => {
  const browser = await chromium.launch({ executablePath: fs.existsSync(CHROME) ? CHROME : undefined });
  const page = await browser.newPage();
  await page.goto("file://" + path.join(__dirname, "card.html"));
  await page.addScriptTag({ content: "window.drawLaunch=" + drawLaunch.toString() });
  const photo = "data:image/jpeg;base64," + fs.readFileSync(path.join(ROOT, "site/img/bg-dday.jpg")).toString("base64");
  for (const [kind, W, H] of [["x", 1600, 1440], ["instagram", 1080, 1350]]) {
    const out = await page.evaluate(([p, w, h]) => window.drawLaunch(p, w, h), [photo, W, H]);
    const file = path.join(ROOT, "cards", `newsletter-launch-${kind}-teal.jpg`);
    fs.writeFileSync(file, Buffer.from(out.split(",")[1], "base64"));
    console.log("wrote", path.relative(ROOT, file));
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
