// Renders a WW2 Dispatches story video: archival photos and typed cards in the living card frame,
// with narration and captions. No music.
// Usage: node renderer/story.js <story-id> [voice]
// Needs stories/<id>.json and narration from renderer/story_tts.py (stories/audio/<id>/<voice>/).
// Output: videos/dispatch-NNN-story-<voice>.mp4 (1080 x 1920, 30 fps) for TikTok and YouTube Shorts.
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const CHROME = process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
const TONE = "colorchannelmixer=.927:.092:.023:0:.042:.962:.020:0:.033:.064:.896,eq=contrast=1.04";
const FPS = 30, LEAD = 0.3, GAP = 0.45, TAIL = 1.2;

// Drawn inside card.html so fonts, grain, and the stamp match the cards exactly.
const PAGE_CODE = String.raw`
window.storyFrame = function(p, caption){
  const W=1080,H=1920,cv=document.createElement("canvas"); cv.width=W; cv.height=H;
  const ctx=cv.getContext("2d"),u=W/100,m=3.2*u;
  const [sName,accent]=SERIES[SKEY[(p.series||"").toLowerCase()]||"battle"];
  ctx.fillStyle=PAPER; ctx.fillRect(0,0,W,H);
  if(!grainTile) grainTile=makeGrain();
  ctx.fillStyle=ctx.createPattern(grainTile,"repeat"); ctx.fillRect(0,0,W,H);
  const vg=ctx.createRadialGradient(W/2,H/2,Math.min(W,H)*.35,W/2,H/2,Math.max(W,H)*.72);
  vg.addColorStop(0,"rgba(120,88,48,0)"); vg.addColorStop(1,"rgba(120,88,48,.24)"); ctx.fillStyle=vg; ctx.fillRect(0,0,W,H);
  const py=Math.round(36*u), ph=Math.round(68*u), px=Math.round(m), pw=Math.round(W-2*m);
  ctx.clearRect(px,py,pw,ph);
  ctx.lineWidth=.35*u; ctx.strokeStyle=INK; ctx.strokeRect(px+.175*u,py+.175*u,pw-.35*u,ph-.35*u);
  ctx.textAlign="left"; ctx.textBaseline="alphabetic";
  ctx.fillStyle=INK; ctx.font="700 "+(6.6*u)+"px Oswald"; ctx.letterSpacing=(.02*6.6*u)+"px";
  ctx.fillText("WW2 DISPATCHES",m,py-10.5*u);
  ctx.fillStyle=NAVY; ctx.font='400 '+(3.2*u)+'px "Special Elite"'; ctx.letterSpacing=(.04*3.2*u)+"px";
  ctx.fillText("Dispatch "+pad(p.num)+" · The Story",m,py-5*u);
  stamp(ctx,u,sName.toUpperCase(),accent,W-m-.4*u,py-8.2*u);
  ctx.textAlign="right"; ctx.fillStyle=NAVY; ctx.font='400 '+(3*u)+'px "Special Elite"'; ctx.letterSpacing=(.02*3*u)+"px";
  ctx.fillText("@ww2dispatches",W-m,py-16.5*u);
  const dateBase=py+ph+9.5*u, placeBase=dateBase+4.4*u;
  ctx.textAlign="left"; ctx.fillStyle=INK; ctx.font="700 "+(7.4*u)+"px Oswald"; ctx.letterSpacing=(.01*7.4*u)+"px";
  ctx.fillText(shortDate(p.date),m,dateBase);
  ctx.fillStyle=NAVY; ctx.font='400 '+(3.1*u)+'px "Special Elite"'; ctx.letterSpacing=(.04*3.1*u)+"px";
  ctx.fillText(p.place||"",m,placeBase);
  ctx.fillStyle=accent; ctx.fillRect(m,placeBase+3*u,10*u,.5*u);
  if(caption){
    ctx.fillStyle=INK; ctx.font='400 '+(4.8*u)+'px "Special Elite"'; ctx.letterSpacing="0px";
    wrap(ctx,caption,W-2*m-12*u,5).forEach((ln,i)=>ctx.fillText(ln,m,placeBase+10.5*u+i*6.2*u));
  }
  return {png:cv.toDataURL("image/png"),win:[px,py,pw,ph]};
};
window.storyCard = async function(p, v, w, h){
  const cv=document.createElement("canvas"); cv.width=w; cv.height=h; const ctx=cv.getContext("2d"),u=w/100;
  const [sName,accent]=SERIES[SKEY[(p.series||"").toLowerCase()]||"battle"];
  const DARK="#221D17", LIGHT="#EDE4CF";
  ctx.fillStyle=DARK; ctx.fillRect(0,0,w,h);
  if(!grainTile) grainTile=makeGrain();
  ctx.globalAlpha=.55; ctx.fillStyle=ctx.createPattern(grainTile,"repeat"); ctx.fillRect(0,0,w,h); ctx.globalAlpha=1;
  const vg=ctx.createRadialGradient(w/2,h/2,h*.2,w/2,h/2,w*.75); vg.addColorStop(0,"rgba(0,0,0,0)"); vg.addColorStop(1,"rgba(0,0,0,.45)");
  ctx.fillStyle=vg; ctx.fillRect(0,0,w,h);
  ctx.textBaseline="alphabetic"; ctx.textAlign="left";
  if(v.type==="end"){
    ctx.textAlign="center";
    ctx.fillStyle=LIGHT; ctx.font="700 "+(10*u)+"px Oswald"; ctx.letterSpacing=(.02*10*u)+"px";
    ctx.fillText("WW2 DISPATCHES",w/2,h*.44);
    ctx.fillStyle=accent; ctx.fillRect(w/2-9*u,h*.44+4*u,18*u,.6*u);
    ctx.fillStyle=LIGHT; ctx.font='400 '+(4.6*u)+'px "Special Elite"'; ctx.letterSpacing=(.04*4.6*u)+"px";
    ctx.fillText("The war, on the day it happened.",w/2,h*.44+13*u);
    ctx.fillStyle="#C9B98F"; ctx.font='400 '+(4*u)+'px "Special Elite"';
    ctx.fillText("Follow @ww2dispatches",w/2,h*.44+21*u);
    return cv.toDataURL("image/png");
  }
  let x=8*u, top=h*.2;
  if(v.inset){
    const img=new Image(); img.src=v.inset; await img.decode();
    const iw=30*u, ih=iw*img.height/img.width, ix=w-8*u-iw, iy=h*.2;
    ctx.save(); ctx.translate(ix+iw/2,iy+ih/2); ctx.rotate(2.2*Math.PI/180);
    ctx.fillStyle=LIGHT; ctx.fillRect(-iw/2-1.4*u,-ih/2-1.4*u,iw+2.8*u,ih+7*u);
    ctx.filter="grayscale(1) sepia(.15) contrast(1.05)"; ctx.drawImage(img,-iw/2,-ih/2,iw,ih); ctx.filter="none";
    ctx.fillStyle=INK; ctx.font='400 '+(2.6*u)+'px "Special Elite"'; ctx.textAlign="center"; ctx.fillText(v.insetName||"",0,ih/2+4.3*u);
    ctx.restore(); ctx.textAlign="left";
  }
  ctx.fillStyle=accent; ctx.font="600 "+(3.2*u)+"px Oswald"; ctx.letterSpacing=(.18*3.2*u)+"px";
  ctx.fillText((v.kicker||"").toUpperCase(),x,top);
  ctx.fillRect(x,top+2.4*u,8*u,.45*u);
  let y=top+12*u;
  v.lines.forEach((ln,i)=>{
    const head=(i===0);
    if(head){ctx.fillStyle=LIGHT; ctx.font="700 "+(8*u)+"px Oswald"; ctx.letterSpacing=(.015*8*u)+"px";}
    else {ctx.fillStyle=(v.inset&&i%2===0)?"#C9B98F":LIGHT; ctx.font='400 '+(4.8*u)+'px "Special Elite"'; ctx.letterSpacing=(.03*4.8*u)+"px";}
    const maxW=v.inset?(w-50*u):(w-16*u);
    const parts=wrap(ctx,ln,maxW,3);
    parts.forEach(pt=>{ctx.fillText(pt,x,y); y+=head?9.5*u:6.6*u;});
    if(head) y+=2.5*u; else if(v.inset&&i%2===0) y+=3*u;
  });
  return cv.toDataURL("image/png");
};`;

function run(args) { execFileSync("ffmpeg", ["-loglevel", "error", "-y", ...args], { stdio: "inherit" }); }
function save(dataUrl, file) { fs.writeFileSync(file, Buffer.from(dataUrl.split(",")[1], "base64")); }

(async () => {
  const [sid, voice = "bm_daniel"] = process.argv.slice(2);
  const story = JSON.parse(fs.readFileSync(path.join(ROOT, "stories", sid + ".json"), "utf8"));
  const p = JSON.parse(fs.readFileSync(path.join(ROOT, "dispatches", story.dispatch + ".json"), "utf8"));
  const adir = path.join(ROOT, "stories", "audio", sid, voice);
  const dur = JSON.parse(fs.readFileSync(path.join(adir, "dur.json"), "utf8"));
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "story-"));
  const browser = await chromium.launch({ executablePath: fs.existsSync(CHROME) ? CHROME : undefined });
  const page = await browser.newPage();
  await page.goto("file://" + path.join(__dirname, "card.html"));
  await page.evaluate(PAGE_CODE);
  await page.evaluate(() => Promise.all(["700 10px Oswald", "600 10px Oswald", '400 10px "Special Elite"'].map(f => document.fonts.load(f))));

  const parts = [];
  const segs = story.segments;
  for (let i = 0; i < segs.length; i++) {
    const s = segs[i], v = s.visual;
    const { png, win } = await page.evaluate(([p, c]) => window.storyFrame(p, c), [p, s.caption]);
    const frame = path.join(tmp, s.id + "-frame.png"); save(png, frame);
    const [wx, wy, ww, wh] = win;
    const len = dur[s.id] + GAP + (i === 0 ? LEAD : 0) + (i === segs.length - 1 ? TAIL : 0);
    const frames = Math.round(len * FPS);
    let src, tone = "";
    if (v.type === "photo") { src = path.join(ROOT, v.src); tone = "," + TONE; }
    else {
      const inset = v.inset ? "data:image/jpeg;base64," + fs.readFileSync(path.join(ROOT, v.inset)).toString("base64") : null;
      const card = await page.evaluate(([p, v, w, h]) => window.storyCard(p, v, w, h), [p, { ...v, inset }, ww, wh]);
      src = path.join(tmp, s.id + "-card.png"); save(card, src);
    }
    // Ken Burns: cover the window at 2x, then a slow push in or pull out around the focus point.
    const S = 2, CW = ww * S, CH = wh * S;
    const fx = (v.focusX ?? 50) / 100, fy = (v.focusY ?? 50) / 100;
    const z0 = v.type === "photo" ? (v.start || 1.0) : 1.0;
    const z1 = v.type === "photo" ? z0 + 0.09 : z0 + 0.035;
    const za = v.zoom === "out" ? z1 : z0, zb = v.zoom === "out" ? z0 : z1;
    const zexpr = `${za}+(${zb - za})*on/${frames}`;
    const cover = `scale=${CW}:${CH}:force_original_aspect_ratio=increase,crop=${CW}:${CH}:(iw-${CW})*${fx}:(ih-${CH})*${fy}`;
    const kb = `zoompan=z='${zexpr}':x='(iw-iw/zoom)*${fx}':y='(ih-ih/zoom)*${fy}':d=${frames}:s=${ww}x${wh}:fps=${FPS}`;
    const fadeIn = i === 0 ? "" : `,fade=t=in:st=0:d=0.25`;
    const out = path.join(tmp, s.id + ".mp4");
    const audioPad = `adelay=${Math.round((i === 0 ? LEAD : 0) * 1000)}:all=1,apad=whole_dur=${len.toFixed(3)},aresample=48000`;
    run(["-loop", "1", "-i", src, "-loop", "1", "-i", frame, "-i", path.join(adir, s.id + ".wav"),
      "-filter_complex",
      `[0:v]${cover},${kb}${tone},format=yuv420p${fadeIn}[w];` +
      `color=c=0x1A1612:s=1080x1920:r=${FPS}:d=${len.toFixed(3)}[bg];[bg][w]overlay=${wx}:${wy}[b];[b][1:v]overlay=0:0:shortest=1,format=yuv420p[v];` +
      `[2:a]${audioPad}[a]`,
      "-map", "[v]", "-map", "[a]", "-t", len.toFixed(3), "-r", String(FPS),
      "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "160k", out]);
    parts.push(out);
    console.log(s.id, len.toFixed(2) + "s");
  }
  await browser.close();
  const list = path.join(tmp, "list.txt");
  fs.writeFileSync(list, parts.map(f => `file '${f}'`).join("\n"));
  fs.mkdirSync(path.join(ROOT, "videos"), { recursive: true });
  const outFile = path.join(ROOT, "videos", `dispatch-${String(p.num).padStart(3, "0")}-story-${voice}.mp4`);
  run(["-f", "concat", "-safe", "0", "-i", list, "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", outFile]);
  console.log("wrote", outFile);
})();
