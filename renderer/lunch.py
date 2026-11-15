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
MEDIA = "https://media.ww2dispatches.com/"  # videos and posters (R2); see renderer/media.py
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
<style>
:root{
  --bg:#f7f6f2; --card:#ffffff; --ink:#24221f; --soft:#6b665e; --line:#e3dfd6; --line2:#efece5;
  --green:#3f8a4f; --amber:#c98a12; --red:#c0392b; --navy:#3D5884;
  --attnBg:#fff4f2; --attnLine:#f0cfc9; --doneBg:#e3f1e5; --todayBg:#fde3df; --input:#ffffff; --onInk:#ffffff; --textBg:#fbfaf7;
  color-scheme:light;
}
html[data-theme=dark]{
  --bg:#141518; --card:#1d1f23; --ink:#e9e6e0; --soft:#a39f97; --line:#33363c; --line2:#282a2f;
  --green:#4fa461; --amber:#d99a26; --red:#e2604f; --navy:#8aa6d6;
  --attnBg:#3a2321; --attnLine:#5e3530; --doneBg:#21382a; --todayBg:#4a2622; --input:#16181b; --onInk:#141518; --textBg:#17191c;
  color-scheme:dark;
}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;-webkit-text-size-adjust:100%}
button{font:inherit;color:inherit;cursor:pointer}
a{color:var(--navy)}
.top{position:sticky;top:0;z-index:50;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 12px 8px}
.titlebar{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
h1{font-size:18px;margin:0;font-weight:700}
#todayLbl{color:var(--soft);font-size:13px}
.controls{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;align-items:center}
.controls>button{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:6px 10px;min-height:34px}
.controls>button:disabled{opacity:.4;cursor:default}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:auto;max-width:100%;-webkit-overflow-scrolling:touch}
.seg button{border:0;border-right:1px solid var(--line);background:var(--card);padding:6px 9px;min-height:34px;white-space:nowrap;font-size:13px}
.seg button:last-child{border-right:0}
.seg button.on{background:var(--ink);color:var(--onInk)}
.seg button.td:not(.on){color:var(--red);font-weight:700}
.seg .ck{color:var(--green);margin-left:3px;font-weight:700}
.seg button.on .ck{color:inherit}
.status{margin-top:6px;color:var(--soft);font-size:13px;min-height:0}
.status:empty{display:none}
section{margin:12px}
h2{font-size:15px;margin:0 0 8px}
.attn{background:var(--attnBg);border:1px solid var(--attnLine);border-radius:10px;padding:10px 12px;margin:12px}
.attn:empty{display:none}
.attn b{color:var(--red)}
/* week strip */
.weeks{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}
.wk{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 10px;cursor:pointer;text-align:left;width:100%;font-size:13px;display:flex;flex-direction:column;gap:3px}
.wk.on{border-color:var(--ink);box-shadow:inset 0 0 0 1px var(--ink)}
.wk .d{font-weight:700;display:flex;justify-content:space-between;gap:6px}
.wk .t{display:flex;gap:6px;align-items:flex-start}
.wk small{color:var(--soft)}
.dot{width:9px;height:9px;border-radius:3px;margin-top:4px;flex:none;display:inline-block}
.tag{font-size:11px;border-radius:5px;padding:0 5px;white-space:nowrap;font-weight:500}
.tag.done{background:var(--doneBg);color:var(--green)}
.tag.today{background:var(--todayBg);color:var(--red)}
.tag.somber{background:var(--line2);color:var(--soft)}
/* day */
.daygrid{display:grid;grid-template-columns:1fr;gap:10px;margin:12px}
.col{display:flex;flex-direction:column;gap:10px;min-width:0}
.box{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.box h2{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.box h2 span{color:var(--soft);font-weight:400;font-size:12px}
.dhead h3{margin:4px 0 2px;font-size:17px}
.meta{color:var(--soft);font-size:13px;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.text{white-space:pre-wrap;background:var(--textBg);border:1px solid var(--line2);border-radius:8px;padding:9px 10px;font-size:15px;line-height:1.5}
.help{font-size:12px;color:var(--soft);margin:6px 0 0}
img.pic{width:100%;border-radius:8px;display:block;border:1px solid var(--line);background:var(--bg)}
.btns{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.btns button,.btns a{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 12px;min-height:38px;color:var(--ink);text-decoration:none;display:inline-flex;align-items:center;font-size:14px}
.btns .go{background:var(--green);color:#fff;border-color:var(--green)}
.btns .primary{background:var(--ink);color:var(--onInk);border-color:var(--ink)}
.btns .confirm{background:var(--red);color:#fff;border-color:var(--red)}
.btns .posted{background:var(--doneBg);color:var(--green);border-color:var(--green)}
ol.steps{margin:6px 0 0;padding-left:20px;font-size:13px}
ol.steps li{margin:2px 0}
ul.facts{margin:0;padding:0;list-style:none}
ul.facts li{display:flex;gap:8px;align-items:flex-start;padding:5px 0;border-top:1px solid var(--line2);font-size:13px}
ul.facts li:first-child{border-top:0}
ul.facts li span{flex:1}
ul.facts button{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:2px 8px;font-size:12px;color:var(--soft);flex:none}
.srcs{font-size:12px;color:var(--soft);margin:8px 0 0}
/* sheet */
.sheetbg{position:fixed;inset:0;background:rgba(20,18,15,.35);z-index:60;display:flex;align-items:flex-end;justify-content:center}
.sheetbg.hidden{display:none}
.sheet{background:var(--card);width:100%;max-width:560px;max-height:88vh;overflow:auto;border-radius:16px 16px 0 0;padding:16px 16px calc(16px + env(safe-area-inset-bottom))}
@media(min-width:700px){.sheetbg{align-items:center}.sheet{border-radius:14px}}
.sheet h3{margin:0 0 8px;font-size:17px}
.menu{display:flex;flex-direction:column;gap:6px;margin-top:6px}
.menu a{color:var(--ink);text-decoration:none}
.menu button,.menu a{display:flex;align-items:center;gap:12px;width:100%;text-align:left;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;min-height:50px}
.menu .mi{width:22px;text-align:center;font-size:17px}
.menu button .ms2{margin-left:auto;color:var(--soft);font-size:13px}
.menu .sep{height:1px;background:var(--line);margin:4px 0}
@media (min-width:1000px){
  body{display:flex;flex-direction:column}
  .top{order:0} #attn{order:1} #week{order:2} #day{order:3} .foot{order:4}
  .daygrid{grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);align-items:start}
  .weeks{grid-template-columns:repeat(7,minmax(0,1fr))}
}
.foot{color:var(--soft);font-size:12px;margin:16px 14px 30px}
</style></head><body>
<header class="top">
  <div class="titlebar"><h1>Lunch Drop</h1><span id="todayLbl"></span></div>
  <div class="controls">
    <div class="seg" id="daySeg"></div>
    <button id="prevBtn" aria-label="Day before">◀</button>
    <button id="todayBtn">Today</button>
    <button id="nextBtn" aria-label="Day after">▶</button>
    <button id="undoBtn" disabled>↶ Undo</button>
    <button id="menuBtn" aria-label="Menu">☰ Menu</button>
  </div>
  <div id="status" class="status"></div>
</header>

<div id="attn" class="attn"></div>
<div id="day" class="daygrid"></div>
<section id="week"></section>
<p class="foot">This page only helps you post. It never posts for you or changes a card, a caption, or a scheduled task. Posted marks are kept on this device. A new week is built every Sunday morning.</p>

<div id="sheetBg" class="sheetbg hidden"><div id="sheet" class="sheet" role="dialog" aria-modal="true"></div></div>

<script>
(function(){
"use strict";
var DATA = __DATA__;
var $=function(id){return document.getElementById(id)};
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]})}
function store(k,v){try{if(v===undefined)return localStorage.getItem(k);if(v===null)localStorage.removeItem(k);else localStorage.setItem(k,v)}catch(e){return null}}
var MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],WD=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
function parts(s){var p=s.split("-");return new Date(Date.UTC(+p[0],+p[1]-1,+p[2]))}
function fmt(s){var t=parts(s);return WD[t.getUTCDay()]+" "+t.getUTCDate()+" "+MON[t.getUTCMonth()]}
function fmtY(s){return fmt(s)+" "+parts(s).getUTCFullYear()}
function fmtS(s){var t=parts(s);return t.getUTCDate()+" "+MON[t.getUTCMonth()]}
function today(){try{return new Intl.DateTimeFormat("en-CA",{timeZone:"America/Denver"}).format(new Date())}catch(e){return new Date().toISOString().slice(0,10)}}
function denverHour(){try{return +new Intl.DateTimeFormat("en-US",{timeZone:"America/Denver",hour:"numeric",hour12:false}).format(new Date())%24}catch(e){return new Date().getHours()}}
var TODAY=today();

/* theme */
var theme="light";
function applyTheme(t){theme=(t==="dark")?"dark":"light";document.documentElement.setAttribute("data-theme",theme);store("ld_theme",theme)}
applyTheme(store("ld_theme")||"light");

/* status */
var stTimer=null;
function setStatus(t,keep){$("status").textContent=t||"";clearTimeout(stTimer);if(t&&!keep)stTimer=setTimeout(function(){$("status").textContent=""},2600)}

/* posted + undo */
function isPosted(d){return !!store("posted-"+d)}
var undoStack=[];
function pushUndo(label,fn){undoStack.push({label:label,fn:fn});if(undoStack.length>30)undoStack.shift();paintUndo()}
function paintUndo(){var b=$("undoBtn"),u=undoStack[undoStack.length-1];b.disabled=!u;b.title=u?"Undo: "+u.label:"Nothing to undo";b.setAttribute("aria-label",b.title)}
$("undoBtn").addEventListener("click",function(){var u=undoStack.pop();paintUndo();if(!u)return;u.fn();render();setStatus("Undone: "+u.label)});
function setPosted(d,on){var was=isPosted(d);store("posted-"+d,on?"1":null);pushUndo((on?"mark posted ":"unmark ")+fmt(d),function(){store("posted-"+d,was?"1":null)});render();setStatus(on?"Marked posted: "+fmt(d):"Unmarked: "+fmt(d))}

/* copy */
async function copyText(t,btn){
  var ok=false;
  try{await navigator.clipboard.writeText(t);ok=true}catch(e){
    var a=document.createElement("textarea");a.value=t;a.setAttribute("readonly","");a.style.position="fixed";a.style.opacity="0";
    document.body.appendChild(a);a.select();a.setSelectionRange(0,t.length);try{ok=document.execCommand("copy")}catch(err){}a.remove();
  }
  if(ok){setStatus("Copied.");if(btn){var o=btn.textContent;btn.textContent="Copied";setTimeout(function(){if(btn.isConnected)btn.textContent=o},1800)}}
  else setStatus("Copy is blocked here. Press and hold the text to copy it.",true);
}
async function copyImage(src,btn){
  try{
    var img=new Image();img.src=src;await img.decode();
    var c=document.createElement("canvas");c.width=img.naturalWidth;c.height=img.naturalHeight;c.getContext("2d").drawImage(img,0,0);
    var blob=await new Promise(function(r){c.toBlob(r,"image/png")});
    await navigator.clipboard.write([new ClipboardItem({"image/png":blob})]);
    setStatus("Image copied. Paste it into X.");
    if(btn){var o=btn.textContent;btn.textContent="Copied";setTimeout(function(){if(btn.isConnected)btn.textContent=o},1800)}
  }catch(e){setStatus("Image copy is blocked here. Use Open full, then press and hold to save it.",true)}
}

/* navigation */
var current=null;
function idx(){for(var i=0;i<DATA.days.length;i++)if(DATA.days[i].date===current)return i;return 0}
function go(date,smooth){current=date;try{history.replaceState(null,"","#d"+date.replace(/-/g,""))}catch(e){}render();window.scrollTo({top:0,behavior:smooth?"smooth":"auto"})}
function step(n){var i=idx()+n;if(i<0||i>=DATA.days.length)return;go(DATA.days[i].date)}
$("prevBtn").addEventListener("click",function(){step(-1)});
$("nextBtn").addEventListener("click",function(){step(1)});
$("todayBtn").addEventListener("click",function(){var t=DATA.days.find(function(d){return d.date===TODAY});if(t)go(t.date);else setStatus("Today isn't in this week's page. A new one is built Sunday morning.")});
$("daySeg").addEventListener("click",function(e){var b=e.target.closest("button[data-d]");if(b)go(b.dataset.d)});
$("week").addEventListener("click",function(e){var b=e.target.closest("[data-d]");if(b)go(b.dataset.d)});
document.addEventListener("keydown",function(e){
  if(/INPUT|TEXTAREA|SELECT/.test(e.target.tagName||""))return;
  if(e.key==="Escape")closeSheet();
  if(!$("sheetBg").classList.contains("hidden"))return;
  if(e.key==="ArrowLeft")step(-1);if(e.key==="ArrowRight")step(1);
  if((e.ctrlKey||e.metaKey)&&e.key==="z"){e.preventDefault();$("undoBtn").click()}
});

/* render */
function render(){
  var d=DATA.days[idx()];
  $("todayLbl").textContent="Week of "+fmtS(DATA.week)+". Today is "+fmtY(TODAY)+".";
  /* day buttons */
  $("daySeg").innerHTML=DATA.days.map(function(x){var t=parts(x.date);return '<button data-d="'+x.date+'" class="'+(x.date===current?"on":"")+(x.date===TODAY?" td":"")+'">'+WD[t.getUTCDay()]+" "+t.getUTCDate()+(isPosted(x.date)?'<span class="ck">✓</span>':"")+'</button>'}).join("");
  var on=$("daySeg").querySelector(".on");if(on&&on.scrollIntoView)try{on.scrollIntoView({block:"nearest",inline:"nearest"})}catch(e){}
  $("prevBtn").disabled=idx()===0;$("nextBtn").disabled=idx()===DATA.days.length-1;
  /* attention */
  var at=[];
  var td=DATA.days.find(function(x){return x.date===TODAY});
  if(td&&!isPosted(TODAY)&&denverHour()>=13)at.push("<div><b>Not posted yet:</b> today's drop, "+esc(td.title)+", in "+esc(td.community)+".</div>");
  if(!DATA.days.some(function(x){return x.date>=TODAY}))at.push("<div><b>This week is over.</b> The Sunday run builds the next page.</div>");
  $("attn").innerHTML=at.join("");
  /* week strip */
  var w='<h2>This week</h2><div class="weeks">'+DATA.days.map(function(x){var p=isPosted(x.date);
    return '<button class="wk'+(x.date===current?" on":"")+'" data-d="'+x.date+'"><span class="d">'+esc(fmt(x.date))+(p?'<span class="tag done">posted</span>':x.date===TODAY?'<span class="tag today">today</span>':"")+'</span><span class="t"><span class="dot" style="background:'+x.seriesColor+'"></span><span>'+esc(x.title)+'</span></span><small>'+esc(x.community)+(x.somber?" · somber":"")+'</small></button>'}).join("")+'</div>';
  $("week").innerHTML=w;
  /* day detail */
  window.DAY=d;
  var posted=isPosted(d.date), L=[], R=[];
  L.push('<div class="box dhead"><div class="meta"><span class="dot" style="background:'+d.seriesColor+';margin-top:0"></span>'+esc(d.seriesName)+" · Dispatch No. "+String(d.num).padStart(3,"0")+" · "+esc(fmtY(d.date))+(d.date===TODAY?' <span class="tag today">today</span>':"")+(posted?' <span class="tag done">posted</span>':"")+(d.somber?' <span class="tag somber">somber</span>':"")+'</div><h3>'+esc(d.title)+'</h3>'+
    (d.somber?'<div class="attn" style="margin:8px 0 0"><b>Somber day.</b> No question, no jokes, keep replies respectful.</div>':"")+
    '<div class="btns"><a class="primary" href="'+esc(d.communityUrl)+'" target="_blank" rel="noopener">Open '+esc(d.community)+' community</a>'+
    (posted?'<button class="posted" data-act="unpost">Posted ✓</button>':'<button class="go" data-act="post">Mark posted</button>')+'</div>'+
    '<ol class="steps"><li>Open the community and tap post.</li><li>Copy the photo and paste it in, or attach the saved photo.</li><li>Copy the post text and paste it.</li><li>Leave "also post to followers" off.</li><li>Post, reply to it with Reply 1 and the card, then reply to Reply 1 with Reply 2.</li></ol></div>');
  L.push('<div class="box"><h2>The photo</h2>'+(d.img?'<img class="pic" src="'+d.img+'" alt="'+esc(d.alt||"")+'">':'<div class="attn" style="margin:0">Photo preview missing.</div>')+
    '<p class="help">'+esc(d.imageCredit||"")+'</p><div class="btns"><button data-act="cimg">Copy photo</button><a href="'+esc(d.imageFull)+'" target="_blank" rel="noopener">Open full photo</a>'+(d.alt?'<button data-act="calt">Copy alt text</button>':"")+'</div></div>');
  L.push('<div class="box"><h2>Post text<span>'+d.post.length+' characters</span></h2><div class="text">'+esc(d.post)+'</div><div class="btns"><button class="primary" data-act="cpost">Copy post text</button></div></div>');
  d.replies.forEach(function(r,i){
    var card=i===0&&d.cardImg;
    R.push('<div class="box"><h2>Reply '+(i+1)+(card?"<span>with the card</span>":"")+'</h2><div class="text">'+esc(r)+'</div><div class="btns"><button class="primary" data-act="crep" data-i="'+i+'">Copy reply '+(i+1)+'</button></div>'+
      (card?'<img class="pic" style="margin-top:10px" src="'+d.cardImg+'" alt="WW2 Dispatches card"><div class="btns"><button data-act="ccard">Copy card</button><a href="'+esc(d.cardFull)+'" target="_blank" rel="noopener">Open full card</a></div>':"")+'</div>');
  });
  R.push('<div class="box"><h2>Quick facts<span>for answering comments</span></h2><ul class="facts">'+d.facts.map(function(f,i){return '<li><span>'+esc(f)+'</span><button data-act="cfact" data-i="'+i+'">Copy</button></li>'}).join("")+'</ul>'+
    ((d.sources||[]).length?'<p class="srcs">Sources: '+d.sources.map(function(s){return '<a href="'+esc(s.url)+'" target="_blank" rel="noopener">'+esc(s.title)+'</a>'}).join(" · ")+'</p>':"")+'</div>');
  $("day").innerHTML='<div class="col">'+L.join("")+'</div><div class="col">'+R.join("")+'</div>';
}
$("day").addEventListener("click",function(e){
  var b=e.target.closest("button[data-act]");if(!b)return;var d=window.DAY,a=b.dataset.act,i=+b.dataset.i;
  if(a==="post")setPosted(d.date,true);
  else if(a==="unpost"){if(!b.dataset.armed){b.dataset.armed="1";b.className="confirm";b.textContent="Tap again to unmark";setTimeout(function(){if(b.isConnected){delete b.dataset.armed;b.className="posted";b.textContent="Posted ✓"}},4000);return}setPosted(d.date,false)}
  else if(a==="cpost")copyText(d.post,b);
  else if(a==="calt")copyText(d.alt,b);
  else if(a==="crep")copyText(d.replies[i],b);
  else if(a==="cfact")copyText(d.facts[i],b);
  else if(a==="cimg")copyImage(d.img,b);
  else if(a==="ccard")copyImage(d.cardImg,b);
});

/* sheet + menu */
var sheetBg=$("sheetBg"),sheet=$("sheet");
function openSheet(h){sheet.innerHTML=h;sheetBg.classList.remove("hidden");sheet.scrollTop=0}
function closeSheet(){sheetBg.classList.add("hidden");sheet.innerHTML=""}
sheetBg.addEventListener("click",function(e){if(e.target===sheetBg)closeSheet()});
function weekText(){return DATA.days.map(function(x){return fmt(x.date)+": "+x.title+" ("+x.community+")"+(isPosted(x.date)?", posted":"")}).join("\n")}
var MENU=[
  {icon:"↗",label:"Open today's community",href:function(){return (DATA.days.find(function(x){return x.date===TODAY})||window.DAY).communityUrl}},
  {icon:"📋",label:"Copy the whole thread",state:function(){return fmt(window.DAY.date)},run:function(){var d=window.DAY;copyText([d.post].concat(d.replies.map(function(r,i){return "Reply "+(i+1)+":\n"+r})).join("\n\n"));closeSheet()}},
  {icon:"🗓️",label:"Copy the week as text",run:function(){copyText("WW2 Dispatches Lunch Drop, week of "+fmtS(DATA.week)+"\n"+weekText());closeSheet()}},
  {sep:true},
  {icon:"🌙",label:"Dark mode",state:function(){return theme==="dark"?"On":"Off"},run:function(){applyTheme(theme==="dark"?"light":"dark");openMenu()}}
];
function openMenu(){openSheet('<h3>Menu</h3><div class="menu">'+MENU.map(function(m,i){if(m.sep)return '<div class="sep"></div>';if(m.href)return '<a href="'+esc(m.href())+'" target="_blank" rel="noopener"><span class="mi">'+m.icon+'</span><span>'+esc(m.label)+'</span></a>';return '<button data-menu="'+i+'"><span class="mi">'+m.icon+'</span><span>'+esc(m.label)+'</span>'+(m.state?'<span class="ms2">'+esc(m.state())+'</span>':"")+'</button>'}).join("")+'</div><div class="btns"><button data-close="1">Close</button></div>')}
$("menuBtn").addEventListener("click",openMenu);
sheet.addEventListener("click",function(e){var m=e.target.closest("button[data-menu]");if(m){MENU[+m.dataset.menu].run();return}if(e.target.closest("[data-close]"))closeSheet()});

/* start */
var h=(location.hash||"").replace("#d","");
var fromHash=DATA.days.find(function(x){return x.date.replace(/-/g,"")===h});
current=(fromHash||DATA.days.find(function(x){return x.date===TODAY})||DATA.days.find(function(x){return x.date>TODAY})||DATA.days[DATA.days.length-1]).date;
paintUndo();render();
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
