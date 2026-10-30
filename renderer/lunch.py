#!/usr/bin/env python3
"""Build the Lunch Drop page: one phone friendly page with each day's X Community post.

Usage: python3 renderer/lunch.py [lunch/YYYY-MM-DD.json]
With no argument it uses the newest file in lunch/. Writes lunch/lunch-page.html,
a single self contained HTML file (card previews embedded) ready to publish to the
Lunch Drop artifact. Rules for the content are in docs/WW2 Dispatches Lunch Drop.md.
"""
import base64, glob, html, io, json, os, sys
from datetime import date

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CARDS = "https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-cards/main/"
RAW_VIDEOS = "https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-videos/main/"
COMMUNITIES = {
    "History Hub": "1670486568966946821",
    "Modern History": "1810183095208837171",
    "History": "1691711931751534664",
}
SERIES = {
    "battle": ("Battle Lines", "#B04A3E"),
    "home": ("Home Front", "#5E6B3A"),
    "blue": ("Blueprint", "#3D5884"),
    "state": ("Statecraft", "#B8862B"),
    "flash": ("Flash", "#6E5A8A"),
}
REQUIRED = ["date", "dispatch", "num", "series", "title", "community", "image", "imageCredit", "post", "replies", "facts"]


def preview(path):
    """Card preview as a data URI, 1200 px wide, JPEG quality 84."""
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None
    im = Image.open(full).convert("RGB")
    if im.width > 1200:
        im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=84, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def check(day):
    problems = [f"{day.get('date')}: missing {k}" for k in REQUIRED if not day.get(k)]
    if day.get("community") not in COMMUNITIES:
        problems.append(f"{day.get('date')}: unknown community {day.get('community')!r}")
    texts = [day.get("post", ""), day.get("alt", "")] + list(day.get("replies", [])) + list(day.get("facts", []))
    for t in texts:
        for bad in ("—", "–", " - "):
            if bad in t:
                problems.append(f"{day.get('date')}: dash found in {t[:50]!r}")
    if "http" in day.get("post", ""):
        problems.append(f"{day.get('date')}: link in the main post")
    return problems


def build(src):
    week = json.load(open(src))
    days, problems = [], []
    for d in sorted(week["days"], key=lambda x: x["date"]):
        problems += check(d)
        name, color = SERIES.get(d.get("series"), ("", "#1A1612"))
        d2 = dict(d)
        d2["seriesName"], d2["seriesColor"] = name, color
        d2["communityUrl"] = "https://x.com/i/communities/" + COMMUNITIES.get(d.get("community"), "")
        d2["imageFull"] = RAW_CARDS + d["image"]
        d2["img"] = preview(d["image"])
        if not d2["img"]:
            problems.append(f"{d['date']}: image file {d['image']} not found")
        if d["image"].startswith("cards/"):
            problems.append(f"{d['date']}: the image is a posted card; use a plain photo of the event (Lunch Drop doc)")
        d2["cardImg"] = preview(d["replyCard"]) if d.get("replyCard") else None
        d2["cardFull"] = (RAW_CARDS + d["replyCard"]) if d.get("replyCard") else None
        if not d.get("replyCard"):
            problems.append(f"{d['date']}: no replyCard (the day's 8 a.m. card goes on Reply 1)")
        elif not d2["cardImg"]:
            problems.append(f"{d['date']}: card file {d['replyCard']} not found")
        d2["weekday"] = date.fromisoformat(d["date"]).strftime("%a %d %b").replace(" 0", " ")
        days.append(d2)
    page = TEMPLATE.replace("__DATA__", json.dumps({"week": week["week"], "days": days}).replace("</", "<\\/"))
    out = os.path.join(ROOT, "lunch", "lunch-page.html")
    open(out, "w").write(page)
    print(f"wrote {out} ({os.path.getsize(out)//1024} KB, {len(days)} days)")
    for p in problems:
        print("PROBLEM:", p)
    return 1 if problems else 0


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lunch Drop</title>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&display=swap" rel="stylesheet">
<style>
:root{--paper:#EDE4CF;--ink:#1A1612;--red:#B04A3E;--navy:#3D5884;--line:#d6cbb2;--card:#fbf8f1}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:640px;margin:0 auto;padding:14px 14px 60px}
h1{font-family:Oswald,Arial Narrow,sans-serif;font-weight:700;letter-spacing:.04em;font-size:26px;margin:4px 0 2px;text-transform:uppercase}
.sub{color:#5b5348;font-size:14px;margin-bottom:12px}
.tabs{display:flex;gap:6px;overflow-x:auto;padding-bottom:6px;margin-bottom:12px}
.tab{flex:0 0 auto;border:1px solid var(--line);background:var(--card);border-radius:18px;padding:6px 12px;font-size:14px;cursor:pointer;color:var(--ink)}
.tab.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.tab .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#3a7d44;margin-left:6px}
.box{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin-bottom:12px}
.head{display:flex;justify-content:space-between;align-items:baseline;gap:8px;flex-wrap:wrap}
.stamp{font-family:Oswald,sans-serif;font-weight:700;text-transform:uppercase;font-size:13px;letter-spacing:.06em;padding:2px 8px;border:2px solid;border-radius:4px}
.title{font-family:Oswald,sans-serif;font-weight:500;font-size:20px;margin:6px 0 0}
.label{font-family:Oswald,sans-serif;font-weight:700;text-transform:uppercase;font-size:13px;letter-spacing:.06em;color:var(--navy);margin:0 0 6px}
.text{white-space:pre-wrap;background:#fff;border:1px solid var(--line);border-radius:8px;padding:10px;font-size:15px}
.row{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
button,.btn{font:inherit;font-size:15px;border-radius:8px;padding:9px 14px;border:1px solid var(--ink);background:var(--ink);color:#fff;cursor:pointer;text-decoration:none;display:inline-block}
.btn.ghost,button.ghost{background:transparent;color:var(--ink)}
button.done{background:#3a7d44;border-color:#3a7d44}
.go{background:var(--red);border-color:var(--red)}
img.card{width:100%;border-radius:8px;display:block;border:1px solid var(--line)}
.count{font-size:13px;color:#6b6357;margin-top:4px}
.warn{background:#f3e3df;border:1px solid #d9b3aa;border-radius:8px;padding:8px 10px;font-size:14px;margin-bottom:10px}
ol.steps{margin:0;padding-left:20px;font-size:15px}
ol.steps li{margin:3px 0}
ul.facts{margin:0;padding-left:18px}
ul.facts li{margin:4px 0}
.toast{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);background:var(--ink);color:#fff;padding:9px 16px;border-radius:20px;font-size:14px;opacity:0;transition:opacity .2s;pointer-events:none;max-width:90%;text-align:center}
.toast.show{opacity:1}
a{color:var(--navy)}
.small{font-size:13px;color:#6b6357}
</style></head><body><div class="wrap">
<h1>Lunch Drop</h1>
<div class="sub" id="sub"></div>
<div class="tabs" id="tabs"></div>
<div id="day"></div>
</div>
<div class="toast" id="toast"></div>
<script>
const DATA = __DATA__;
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function store(k, v){ try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch(e){ return null; } }
function toast(m){ const t=$("#toast"); t.textContent=m; t.classList.add("show"); clearTimeout(t._h); t._h=setTimeout(()=>t.classList.remove("show"),2200); }
function today(){ try { return new Intl.DateTimeFormat("en-CA",{timeZone:"America/Denver"}).format(new Date()); } catch(e){ return new Date().toISOString().slice(0,10); } }

async function copyText(t){
  try { await navigator.clipboard.writeText(t); toast("Copied"); return; } catch(e){}
  const a=document.createElement("textarea"); a.value=t; a.setAttribute("readonly",""); a.style.position="fixed"; a.style.opacity="0";
  document.body.appendChild(a); a.select(); a.setSelectionRange(0,t.length);
  let ok=false; try { ok=document.execCommand("copy"); } catch(e){}
  a.remove(); toast(ok ? "Copied" : "Copy blocked here. Press and hold the text to copy.");
}
async function copyImage(src){
  try {
    const img=new Image(); img.src=src; await img.decode();
    const c=document.createElement("canvas"); c.width=img.naturalWidth; c.height=img.naturalHeight;
    c.getContext("2d").drawImage(img,0,0);
    const blob=await new Promise(r=>c.toBlob(r,"image/png"));
    await navigator.clipboard.write([new ClipboardItem({"image/png":blob})]);
    toast("Image copied. Paste it into X.");
  } catch(e){ toast("Image copy blocked here. Use Open full photo, then press and hold to save."); }
}

let current=null;
function render(){
  const tabs=$("#tabs"); tabs.innerHTML="";
  DATA.days.forEach(d=>{
    const b=document.createElement("button"); b.className="tab"+(d.date===current?" on":"");
    b.innerHTML=esc(d.weekday)+(store("posted-"+d.date)?'<span class="dot"></span>':"");
    b.onclick=()=>{ current=d.date; try{ history.replaceState(null,"","#d"+d.date.replace(/-/g,"")); }catch(e){} render(); window.scrollTo(0,0); };
    tabs.appendChild(b);
  });
  const d=DATA.days.find(x=>x.date===current); if(!d) return;
  const posted=store("posted-"+d.date);
  let h="";
  h+=`<div class="box"><div class="head"><span class="stamp" style="color:${d.seriesColor};border-color:${d.seriesColor}">${esc(d.seriesName)}</span><span class="small">Dispatch No. ${String(d.num).padStart(3,"0")}${d.date===today()?" · today":""}</span></div>
      <div class="title">${esc(d.title)}</div></div>`;
  if(d.somber) h+=`<div class="warn"><b>Somber day.</b> No question, no jokes, keep replies respectful.</div>`;
  h+=`<div class="box"><p class="label">Post to</p>
      <div class="row" style="margin-top:0"><a class="btn go" href="${esc(d.communityUrl)}" target="_blank" rel="noopener">Open ${esc(d.community)} community</a></div>
      <ol class="steps" style="margin-top:10px"><li>Open the community and tap post.</li><li>Copy the photo below and paste it in (or attach the saved photo).</li><li>Copy the post text and paste it.</li><li>Leave "also post to followers" off.</li><li>Post, then reply to your own post with Reply 1 and the card, then reply to Reply 1 with Reply 2.</li></ol></div>`;
  h+=`<div class="box"><p class="label">The photo</p>${d.img?`<img class="card" src="${d.img}" alt="${esc(d.alt||"")}">`:`<div class="warn">Photo preview missing.</div>`}
      <div class="count">${esc(d.imageCredit||"")}</div>
      <div class="row"><button onclick="copyImage(DAY.img)">Copy photo</button><a class="btn ghost" href="${esc(d.imageFull)}" target="_blank" rel="noopener">Open full photo</a></div>
      ${d.alt?`<div class="row"><button class="ghost" onclick="copyText(DAY.alt)">Copy alt text</button></div>`:""}</div>`;
  h+=`<div class="box"><p class="label">Post text</p><div class="text">${esc(d.post)}</div>
      <div class="count">${d.post.length} characters</div>
      <div class="row"><button onclick="copyText(DAY.post)">Copy post text</button></div></div>`;
  d.replies.forEach((r,i)=>{
    h+=`<div class="box"><p class="label">Reply ${i+1}${i===0&&d.cardImg?" (with the card)":""}</p><div class="text">${esc(r)}</div>
        <div class="row"><button onclick="copyText(DAY.replies[${i}])">Copy reply ${i+1}</button></div>
        ${i===0&&d.cardImg?`<img class="card" style="margin-top:10px" src="${d.cardImg}" alt="WW2 Dispatches card">
        <div class="row"><button onclick="copyImage(DAY.cardImg)">Copy card</button><a class="btn ghost" href="${esc(d.cardFull)}" target="_blank" rel="noopener">Open full card</a></div>`:""}</div>`;
  });
  h+=`<div class="box"><p class="label">Quick facts for answering comments</p><ul class="facts">${d.facts.map((f,i)=>`<li>${esc(f)} <a href="#" onclick="copyText(DAY.facts[${i}]);return false" class="small">copy</a></li>`).join("")}</ul>
      ${(d.sources||[]).length?`<p class="small" style="margin:10px 0 0">Sources: ${d.sources.map(s=>`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a>`).join(" · ")}</p>`:""}</div>`;
  h+=`<div class="row" style="justify-content:center">${posted?`<button class="done" onclick="markPosted(false)">Posted ✓ (tap to undo)</button>`:`<button onclick="markPosted(true)">Mark posted</button>`}</div>`;
  window.DAY=d; $("#day").innerHTML=h;
  $("#sub").textContent=`Week of ${DATA.week}. X Communities at lunch.`;
}
function markPosted(on){ store("posted-"+current, on?"1":null); toast(on?"Marked posted":"Unmarked"); render(); }

(function init(){
  const h=(location.hash||"").replace("#d","");
  const fromHash=DATA.days.find(d=>d.date.replace(/-/g,"")===h);
  const t=today();
  current=(fromHash&&fromHash.date)||(DATA.days.find(d=>d.date===t)||DATA.days.find(d=>d.date>t)||DATA.days[DATA.days.length-1]).date;
  render();
})();
</script></body></html>
"""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        src = sys.argv[1]
    else:
        files = sorted(f for f in glob.glob(os.path.join(ROOT, "lunch", "*.json")) if os.path.basename(f)[:4].isdigit())
        if not files:
            sys.exit("no lunch/YYYY-MM-DD.json found")
        src = files[-1]
    sys.exit(build(src))
