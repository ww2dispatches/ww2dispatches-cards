// Renders a WW2 Dispatches Story Card: archival photos and typed cards in the Living Card frame,
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
  // Same frame as the vertical Living Card (vFrame in card.html), kept inside the phone safe zone.
  const cv=document.createElement("canvas"); cv.width=1080; cv.height=1920;
  const py=Math.round(VSAFE.top*10.8), ph=Math.round(52*10.8);
  const {ctx,u,m,accent,win}=vFrame(cv,p,"Dispatch "+pad(p.num)+" · The Story",py,ph);
  const dateBase=py+ph+7.5*u, base=dateBase+4.2*u;
  ctx.textAlign="left"; ctx.fillStyle=INK; ctx.font="700 "+(6*u)+"px Oswald"; ctx.letterSpacing=(.01*6*u)+"px";
  ctx.fillText(shortDate(p.date),m,dateBase);
  ctx.fillStyle=NAVY; ctx.font='400 '+(3.1*u)+'px "Special Elite"'; ctx.letterSpacing=(.04*3.1*u)+"px";
  wrap(ctx,p.place||"",VSAFE.textRight*u-m,1).forEach(ln=>ctx.fillText(ln,m,base));
  ctx.fillStyle=accent; ctx.fillRect(m,base+2.6*u,10*u,.5*u);
  let lines=0;
  if(caption){
    ctx.fillStyle=INK; ctx.font='400 '+(4.4*u)+'px "Special Elite"'; ctx.letterSpacing="0px";
    const all=wrap(ctx,caption,VSAFE.textRight*u-m,99); lines=all.length;
    all.slice(0,6).forEach((ln,i)=>ctx.fillText(ln,m,base+9*u+i*5.6*u));
  }
  return {png:cv.toDataURL("image/png"),win,lines};
};
const iw0=u=>30*u;
window.storyCard = async function(p, v, w, h){
  const cv=document.createElement("canvas"); cv.width=w; cv.height=h; const ctx=cv.getContext("2d"),u0=w/100;
  // Type scales with the window height (designed for a 734 px window); side margins stay at the safe 12u.
  const u=u0*Math.min(1,h/(68*u0));
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
  let x=12*u0, top=h*.2;
  if(v.inset){
    const img=new Image(); img.src=v.inset; await img.decode();
    const iw=30*u, ih=iw*img.height/img.width, ix=w-12*u0-iw, iy=h*.2;
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
    const maxW=v.inset?(w-24*u0-iw0(u)-4*u):(w-24*u0);
    const parts=wrap(ctx,ln,maxW,3);
    parts.forEach(pt=>{ctx.fillText(pt,x,y); y+=head?9.5*u:6.6*u;});
    if(head) y+=2.5*u; else if(v.inset&&i%2===0) y+=3*u;
  });
  return cv.toDataURL("image/png");
};`;

function run(args) { execFileSync("ffmpeg", ["-loglevel", "error", "-y", ...args], { stdio: "inherit" }); }
function save(dataUrl, file) { fs.writeFileSync(file, Buffer.from(dataUrl.split(",")[1], "base64")); }

(async () => {
  const [sid, voice = "am_onyx"] = process.argv.slice(2);
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
    const { png, win, lines } = await page.evaluate(([p, c]) => window.storyFrame(p, c), [p, s.caption]);
    if (lines > 6) throw new Error(`${s.id}: caption needs ${lines} lines, the frame holds 6. Shorten it.`);
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
