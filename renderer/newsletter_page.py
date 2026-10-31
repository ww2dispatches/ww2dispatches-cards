#!/usr/bin/env python3
"""Build the Weekly Dispatch review page from a newsletter issue.

Usage: python3 renderer/newsletter_page.py [newsletter/issue-NNN.md] [--send YYYY-MM-DD]
With no file it uses the highest numbered issue in newsletter/. The send date
defaults to the next Sunday after today. Writes newsletter/review-page.html, one
self contained file (card previews embedded) to publish to the Weekly Dispatch
artifact. Rules are in docs/WW2 Dispatches Newsletter.md ("Review page").

The page shows the issue, takes Brian's notes and approval (stored in the
artifact's db: issues/NNN and notes/*), and has the copy buttons and steps
for pasting into Substack. Prints PROBLEM lines to fix before publishing.
"""
import base64, glob, html, io, json, os, re, sys
from datetime import date, timedelta

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-cards/main/"
GH_FILE = "https://github.com/ww2dispatches/ww2dispatches-cards/blob/main/"


def preview(url):
    """Card preview as a data URI, 720 px wide, from the local copy of a raw GitHub URL."""
    if not url.startswith(RAW):
        return None
    full = os.path.join(ROOT, url[len(RAW):])
    if not os.path.exists(full):
        return None
    im = Image.open(full).convert("RGB")
    if im.width > 720:
        im = im.resize((720, round(im.height * 720 / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=78, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def inline(text):
    """Markdown inline (links, bold, italics) to HTML, escaping the rest."""
    out, pos = [], 0
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        out.append(_fmt(text[pos:m.start()]))
        out.append(f'<a href="{html.escape(m.group(2))}">{_fmt(m.group(1))}</a>')
        pos = m.end()
    out.append(_fmt(text[pos:]))
    return "".join(out)


def _fmt(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
    return t


def parse(md):
    lines = md.splitlines()
    subject = preview_line = ""
    blocks = []  # (kind, value)
    para = []

    def flush():
        if para:
            blocks.append(("p", " ".join(para)))
            para.clear()

    for line in lines:
        s = line.strip()
        if s.startswith("# ") and not subject:
            subject = s[2:].strip()
            continue
        m = re.match(r"^\*Preview line:\s*(.+)\*$", s)
        if m and not preview_line:
            preview_line = m.group(1).strip()
            continue
        if not s:
            flush(); continue
        if s == "---":
            flush(); blocks.append(("hr", "")); continue
        if s.startswith("## "):
            flush(); blocks.append(("h2", s[3:].strip())); continue
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", s)
        if m:
            flush(); blocks.append(("img", (m.group(1), m.group(2)))); continue
        # An italic line right after a photo is its caption.
        if not para and blocks and blocks[-1][0] == "img" and re.fullmatch(r"\*[^*].*[^*]\*", s):
            blocks.append(("cap", s[1:-1])); continue
        para.append(s)
    flush()
    return subject, preview_line, blocks


def sections(blocks):
    """Group blocks into review sections: intro, each morning dispatch, evening desk, sign off."""
    secs, cur = [], {"id": "intro", "label": "Intro", "blocks": []}
    for kind, val in blocks:
        if kind == "hr":
            if cur["blocks"]:
                secs.append(cur)
            cur = {"id": f"s{len(secs)}", "label": "", "blocks": [], "hr": True}
            continue
        # In an article each subhead starts a new review section (a story
        # dispatch's heading follows its card image, so that stays together).
        if kind == "h2" and any(k in ("h2", "p") for k, _ in cur["blocks"]):
            secs.append(cur)
            cur = {"id": "", "label": "", "blocks": []}
        if kind == "h2" and not cur["label"]:
            cur["label"] = val
        cur["blocks"].append((kind, val))
    if cur["blocks"]:
        secs.append(cur)
    for i, s in enumerate(secs):
        if not s["label"]:
            s["label"] = "Intro" if i == 0 else ("Sign off" if i == len(secs) - 1 else f"Section {i + 1}")
        m = re.search(r"No\. (\d{3})", s["label"])
        s["id"] = f"n{m.group(1)}" if m else re.sub(r"[^a-z0-9]+", "-", s["label"].lower()).strip("-")
    return secs


def checks(subject, preview_line, blocks):
    problems, warnings = [], []
    if not subject:
        problems.append("no subject line (# heading)")
    if not preview_line:
        problems.append("no preview line")
    text_all = [subject, preview_line] + [v if isinstance(v, str) else v[0] for k, v in blocks]
    for t in text_all:
        for bad in ("—", "–", " - "):
            if bad in t:
                problems.append(f"dash found in {t[:60]!r}")
    for k, v in blocks:
        if k == "img" and preview(v[1]) is None:
            problems.append(f"missing card image {v[1]}")
        if k == "p":
            for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", v):
                if re.fullmatch(r"https://x\.com/ww2dispatches/?", m.group(2)):
                    title = re.search(r"No\. \d{3}[^*]*", v)
                    warnings.append(m.group(2))
    return problems, warnings


def build(src, send):
    num = int(re.search(r"issue-(\d+)\.md$", src).group(1))
    md = open(src, encoding="utf-8").read()
    subject, preview_line, blocks = parse(md)
    problems, _ = checks(subject, preview_line, blocks)
    secs = sections(blocks)

    # Review HTML (embedded previews) and copy HTML (raw GitHub image URLs).
    review, copy_html, copy_text, link_flags = [], [], [], []
    for i, s in enumerate(secs):
        if i and s.get("hr"):
            copy_html.append("<hr>")
            copy_text.append("")
        inner = []
        for kind, val in s["blocks"]:
            if kind == "h2":
                inner.append(f"<h2>{inline(val)}</h2>")
                copy_html.append(f"<h2>{inline(val)}</h2>")
                copy_text.append(val)
            elif kind == "cap":
                inner.append(f'<p class="cap">{inline(val)}</p>')
                copy_html.append(f"<p><em>{inline(val)}</em></p>")
                copy_text.append(re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", val))
            elif kind == "img":
                alt, url = val
                inner.append(
                    f'<figure><img src="{preview(url)}" alt="{html.escape(alt)}" data-raw="{html.escape(url)}">'
                    f'<figcaption><button class="mini" data-copyimg>Copy image</button> '
                    f'<a class="mini" href="{html.escape(url)}">Open full image</a></figcaption></figure>')
                copy_html.append(f'<p><img src="{html.escape(url)}" alt="{html.escape(alt)}"></p>')
            else:
                profile = re.findall(r"\]\((https://x\.com/ww2dispatches/?)\)", val)
                cls = ' class="flag"' if profile else ""
                inner.append(f"<p{cls}>{inline(val)}</p>")
                if profile:
                    link_flags.append({"id": s["id"], "label": s["label"]})
                copy_html.append(f"<p>{inline(val)}</p>")
                copy_text.append(re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", val).replace("**", "").replace("*", ""))
        review.append(
            f'<section class="sec" id="{s["id"]}" data-label="{html.escape(s["label"])}">'
            f'<div class="sechead"><button class="notebtn" data-sec="{s["id"]}">+ Note</button></div>'
            + "".join(inner) + "</section>")
    # The evening desk has several cards in one section; label profile links by card.
    flags = []
    for s in secs:
        for kind, val in s["blocks"]:
            if kind == "p" and re.search(r"\]\(https://x\.com/ww2dispatches/?\)", val):
                m = re.search(r"No\. (\d{3})", val) or re.search(r"No\. (\d{3})", s["label"])
                t = re.search(r"No\. \d{3}(?: · [^·*]+)* · ([^*]+)\*\*", val)
                name = t.group(1).strip() if t else s["label"].split(": ", 1)[-1]
                flags.append({"sec": s["id"], "num": m.group(1) if m else "", "title": name})

    data = {
        "issue": num,
        "issueId": f"{num:03d}",
        "subject": subject,
        "preview": preview_line,
        "send": send.isoformat(),
        "sendLabel": send.strftime("%a %-d %b %Y"),
        "built": date.today().isoformat(),
        "github": GH_FILE + os.path.relpath(src, ROOT),
        "sections": [{"id": s["id"], "label": s["label"]} for s in secs],
        "flags": flags,
        "copyHtml": "".join(copy_html),
        "copyText": "\n\n".join(copy_text).strip(),
    }
    tpl = open(os.path.join(ROOT, "renderer", "newsletter_page.html"), encoding="utf-8").read()
    page = (tpl.replace("{{ISSUE_ID}}", data["issueId"])
               .replace("{{SUBJECT}}", html.escape(subject))
               .replace("{{PREVIEW}}", html.escape(preview_line))
               .replace("{{REVIEW}}", "".join(review))
               .replace("{{DATA}}", json.dumps(data).replace("</", "<\\/")))
    out = os.path.join(ROOT, "newsletter", "review-page.html")
    open(out, "w", encoding="utf-8").write(page)
    for p in problems:
        print("PROBLEM", p)
    for f in flags:
        print(f"NOTE No. {f['num']} links to the X profile, not its post (not posted yet)")
    print(f"Wrote {os.path.relpath(out, ROOT)} ({os.path.getsize(out) // 1024} KB), issue {num:03d}, send {send}")


def main():
    args = sys.argv[1:]
    send = None
    if "--send" in args:
        i = args.index("--send")
        send = date.fromisoformat(args[i + 1])
        del args[i:i + 2]
    if args:
        src = os.path.abspath(args[0])
    else:
        files = sorted(glob.glob(os.path.join(ROOT, "newsletter", "issue-*.md")))
        if not files:
            sys.exit("no newsletter/issue-*.md found")
        src = files[-1]
    if send is None:
        today = date.today()
        send = today + timedelta(days=(6 - today.weekday()) or 7)
    build(src, send)


if __name__ == "__main__":
    main()
