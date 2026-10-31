// Renders the Sunday share card for a Weekly Dispatch issue (a promotion, not a dispatch: no dispatch number,
// never in the Declass catalog, which reads only dispatches/ and namethis/).
// Usage: node renderer/newsletter_share.js NNN   -> cards/newsletter-NNN-x.jpg and cards/newsletter-NNN-instagram.jpg
// Title and lead photo come from newsletter/issue-NNN.md (the H1 and the first image). Same look as the launch card.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const CHROME = process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
const num = String(process.argv[2] || "").padStart(3, "0");
if (!/^\d{3}$/.test(num)) { console.error("usage: node renderer/newsletter_share.js NNN"); process.exit(1); }

function drawShare(photoUrl, W, H, title, issue) {
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
    ctx.textBaseline="alphabetic"; ctx.textAlign="left"; ctx.fillStyle=INK;
    ctx.font=`700 ${4.2*u}px Oswald`; ctx.letterSpacing=`${.02*4.2*u}px`; ctx.fillText("THE WEEKLY DISPATCH",m,8*u);
    ctx.fillStyle=NAVY; ctx.font=`400 ${2.5*u}px "Special Elite"`; ctx.letterSpacing="0px"; ctx.fillText(`WW2 Dispatches · Issue ${issue}`,m,11.6*u);
    stamp(ctx,u,"NEW ISSUE",TEAL,W-m,8*u);
    // headline: wrap to at most two lines, shrinking if needed
    let fs=7*u, lines;
    const wrap=(size)=>{ctx.font=`700 ${size}px Oswald`; ctx.letterSpacing=`${.01*size}px`;
      const words=title.toUpperCase().split(" "), out=[""];
      for(const w of words){const t=out[out.length-1]?out[out.length-1]+" "+w:w; if(ctx.measureText(t).width<=W-2*m||!out[out.length-1]) out[out.length-1]=t; else out.push(w);} return out;};
    for(;;){lines=wrap(fs); if(lines.length<=2||fs<4.5*u) break; fs-=.3*u;}
    const headH=lines.length*fs*1.02;
    const top=15*u, bottomBand=headH+(H/W>1.1?22:19)*u, ph=H-top-bottomBand, pw=W-2*m;
    const s=Math.max(pw/img.naturalWidth,ph/img.naturalHeight), dw=img.naturalWidth*s, dh=img.naturalHeight*s;
    ctx.save(); ctx.beginPath(); ctx.rect(m,top,pw,ph); ctx.clip();
    ctx.filter="sepia(.15) contrast(1.05)"; ctx.drawImage(img,m+(pw-dw)/2,top+(ph-dh)*.45,dw,dh); ctx.filter="none"; ctx.restore();
    ctx.strokeStyle=INK; ctx.lineWidth=.35*u; ctx.strokeRect(m,top,pw,ph);
    let y=top+ph+fs*1.05+2*u;
    ctx.fillStyle=INK; ctx.font=`700 ${fs}px Oswald`; ctx.letterSpacing=`${.01*fs}px`;
    for(const l of lines){ctx.fillText(l,m,y); y+=fs*1.02;}
    y+=2.6*u-fs*1.02+3*u; ctx.fillStyle=NAVY; ctx.font=`400 ${2.9*u}px "Special Elite"`; ctx.letterSpacing="0px";
    ctx.fillText("One story from the war, told in full. Free every Sunday.",m,y);
    y+=6*u; ctx.fillStyle=TEAL; ctx.font=`600 ${3.4*u}px Oswald`; ctx.letterSpacing=`${.04*3.4*u}px`;
    ctx.fillText("READ IT FREE: WW2DISPATCHES.SUBSTACK.COM",m,y);
    return cv.toDataURL("image/jpeg",.9);
  })();
}

(async () => {
  const md = fs.readFileSync(path.join(ROOT, "newsletter", `issue-${num}.md`), "utf-8");
  const title = (md.match(/^# (.+)$/m) || [])[1];
  const imgUrl = (md.match(/!\[[^\]]*\]\(([^)]+)\)/) || [])[1];
  if (!title || !imgUrl) throw new Error("issue file needs an H1 title and a lead image");
  const local = imgUrl.replace(/^https:\/\/raw\.githubusercontent\.com\/ww2dispatches\/ww2dispatches-cards\/main\//, "");
  const p = path.join(ROOT, local);
  if (!fs.existsSync(p)) throw new Error("lead photo not in repo: " + local);
  const photo = "data:image/jpeg;base64," + fs.readFileSync(p).toString("base64");
  const browser = await chromium.launch({ executablePath: fs.existsSync(CHROME) ? CHROME : undefined });
  const page = await browser.newPage();
  await page.goto("file://" + path.join(__dirname, "card.html"));
  await page.addScriptTag({ content: "window.drawShare=" + drawShare.toString() });
  for (const [kind, W, H] of [["x", 1600, 1440], ["instagram", 1080, 1350]]) {
    const out = await page.evaluate(([ph, w, h, t, n]) => window.drawShare(ph, w, h, t, n), [photo, W, H, title, num]);
    const file = path.join(ROOT, "cards", `newsletter-${num}-${kind}.jpg`);
    fs.writeFileSync(file, Buffer.from(out.split(",")[1], "base64"));
    console.log("wrote", path.relative(ROOT, file));
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
