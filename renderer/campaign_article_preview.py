"""Builds a preview of a Campaign Series Substack part, styled like the WW2 Dispatches Substack post page
(night background, brass gold accent, Anton titles, Libre Baskerville body), so the part can be checked
before it is pasted into Substack. The same markdown is what the site's Campaign Shelf reads.

Usage: python3 renderer/campaign_article_preview.py <series> <part>
Writes campaign-series/<series>/articles/preview/part-NN.html (open it, or screenshot it with
node renderer/campaign_article.js --shot <html> <png>).

Markdown conventions in part-NN.md:
  fenced code block with one line  -> a teletype bulletin break, e.g. BULLETIN · 26 NOV 1941 · HITOKAPPU BAY
  ![caption](photo path)           -> a captioned photo or map
  > **PRIMARY DOCUMENT · ...**     -> a set off primary document (also FROM THE RECORD, IN THEIR WORDS)
"""
import json, os, re, sys, html
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
series, part = sys.argv[1], int(sys.argv[2])
adir = os.path.join(ROOT, "campaign-series", series, "articles")
stem = f"part-{part:02d}"
meta = json.load(open(os.path.join(adir, stem + ".json")))
md = open(os.path.join(adir, stem + ".md")).read()
out_dir = os.path.join(adir, "preview")
os.makedirs(out_dir, exist_ok=True)
rel = lambda p: os.path.relpath(os.path.join(ROOT, p), out_dir)

# images with captions
def img(m):
    cap, src = m.group(1), m.group(2)
    return f'\n<figure><img src="{rel(src)}"><figcaption>{html.escape(cap)}</figcaption></figure>\n'
md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", img, md)
body = markdown.markdown(md, extensions=["fenced_code"])

# quote attribution lines (not the label, not the quoted words) get the small grey style
def bq(m):
    inner = re.sub(r"<p>(?![\"“]|<strong>)", '<p class="attr">', m.group(0))
    return inner
body = re.sub(r"<blockquote>.*?</blockquote>", bq, body, flags=re.S)

# day by day strip from the day records
d1, d2 = meta["days"]
strip = "".join(
    f'<img src="{rel(f"campaign-series/{series}/images/day-{d:02d}-instagram.jpg")}">' for d in range(d1, d2 + 1))
strip_html = (f'<div class="strip"><pre><code>ON OUR FEEDS · DAYS {d1} TO {d2}</code></pre>'
              f'<div class="grid">{strip}</div>'
              f'<p class="cap">The daily posts behind this part, as they ran at dawn on X, Instagram, Threads and Facebook.</p></div>')
# put the strip just before the sources
body = body.replace("<h3>Sources</h3>", strip_html + "<h3>Sources</h3>", 1)

fonts = os.path.relpath(os.path.join(ROOT, "renderer", "fonts"), out_dir)
page = f"""<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(meta['substackTitle'])}</title>
<style>
@font-face{{font-family:Anton;src:url({fonts}/anton-latin-400-normal.woff2)}}
@font-face{{font-family:LB;font-weight:400;src:url({fonts}/libre-baskerville-latin-400-normal.woff2)}}
@font-face{{font-family:LB;font-weight:700;src:url({fonts}/libre-baskerville-latin-700-normal.woff2)}}
@font-face{{font-family:LB;font-style:italic;src:url({fonts}/libre-baskerville-latin-400-italic.woff2)}}
body{{margin:0;background:#120F0C;color:#E9E1D0;font-family:LB,Georgia,serif}}
.top{{border-bottom:1px solid #2a241e;padding:18px 0;text-align:center}}
.wm{{font-family:Anton,sans-serif;font-size:26px;letter-spacing:.06em;color:#F3ECDD}}
.sec{{text-align:center;margin:26px 0 0;font:13px/1 ui-monospace,Menlo,monospace;letter-spacing:.18em;color:#B8862B}}
main{{max-width:728px;margin:0 auto;padding:0 24px 80px}}
h1{{font-family:Anton,Impact,sans-serif;font-weight:400;font-size:44px;line-height:1.1;margin:14px 0 10px;color:#F3ECDD}}
.sub{{font-size:19px;line-height:1.5;color:#B9AF9C;margin:0 0 18px}}
.by{{font-size:14px;color:#9b917f;border-top:1px solid #2a241e;border-bottom:1px solid #2a241e;padding:12px 0;margin-bottom:28px}}
.by b{{color:#E9E1D0}}
.cover{{width:100%;display:block}}
.cover+p.cap{{margin-top:8px}}
main p{{font-size:19px;line-height:1.75;margin:0 0 22px}}
main .body>p:first-of-type::first-letter{{font-family:Anton,sans-serif;float:left;font-size:78px;line-height:.9;padding:6px 10px 0 0;color:#B8862B}}
figure{{margin:34px 0}} figure img{{width:100%;display:block}}
figcaption,.cap{{font-size:14px;line-height:1.5;color:#9b917f;text-align:center;margin-top:8px}}
pre{{background:#1d1915;border-radius:4px;padding:14px 18px;margin:44px 0 26px;overflow:auto}}
pre code{{font:15px/1.3 ui-monospace,Menlo,Consolas,monospace;color:#E9E1D0;letter-spacing:.06em}}
blockquote{{border-left:4px solid #B8862B;margin:30px 0;padding:2px 0 2px 22px;color:#E2D8C4}}
blockquote p{{font-style:italic}} blockquote p strong{{font-style:normal;font-family:ui-monospace,Menlo,monospace;font-size:13px;letter-spacing:.12em;color:#B8862B;font-weight:400}}
blockquote p.attr{{font-style:normal;font-size:15px;color:#9b917f}}
h3{{font-family:Anton,sans-serif;font-weight:400;font-size:24px;margin:48px 0 12px;color:#F3ECDD}}
ul{{padding-left:20px}} li{{font-size:15px;line-height:1.6;color:#B9AF9C;margin-bottom:6px}}
a{{color:#E9E1D0}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}} .grid img{{width:100%;display:block}}
.foot{{border-top:1px solid #2a241e;margin-top:40px;padding-top:20px;font-size:15px;color:#9b917f;line-height:1.6}}
</style></head><body>
<div class="top"><span class="wm">WW2 DISPATCHES</span></div>
<main>
<div class="sec">CAMPAIGN SERIES</div>
<h1>{html.escape(meta['substackTitle'])}</h1>
<p class="sub">{html.escape(meta['subtitle'])}</p>
<div class="by"><b>WW2 Dispatches</b> &nbsp;·&nbsp; Preview for {meta['publish'][:10]}</div>
<img class="cover" src="../images/{stem}-cover.jpg" style="margin-bottom:6px">
<p class="cap" style="font-size:14px">{html.escape(meta['coverCredit'])}</p>
<div class="body">{body}</div>
<div class="foot">WW2 Dispatches brings you World War II, one day at a time, with new dispatches and archival film every day.</div>
</main></body></html>"""
dest = os.path.join(out_dir, stem + ".html")
open(dest, "w").write(page)
print("wrote", os.path.relpath(dest, ROOT))
