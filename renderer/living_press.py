"""Builds the Living Press page: every dispatch that has living card videos, with its press kit.

Usage: python3 renderer/living_press.py <out_dir>
Writes <out_dir>/living-press.html and copies the videos and posters into <out_dir>/videos/,
ready to publish as a claude.ai artifact (the page plays the videos from its own published files).
"""
import json, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-cards/main/"
BLOB = "https://github.com/ww2dispatches/ww2dispatches-cards/blob/main/"
# Videos live in the separate ww2dispatches-videos repo since 18 Oct 2026; clone it and copy its videos/ into
# this repo's videos/ (ignored by git) before running this script.
VIDEO_RAW = "https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-videos/main/"


def sections(md):
    out, cur = {}, None
    for line in md.splitlines():
        m = re.match(r"^##\s+(.*)", line)
        if m:
            cur = m.group(1).strip()
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def find(secs, start):
    for k, v in secs.items():
        if k.lower().startswith(start.lower()):
            return k, v
    return None, ""


def nice_date(iso):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})$", iso or "")
    if not m:
        return iso or ""
    mon = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()[int(m.group(2)) - 1]
    return f"{int(m.group(3))} {mon} {m.group(1)}"


def seconds(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return round(float(out), 1) if out else 0


def main(out_dir):
    out = Path(out_dir)
    (out / "videos").mkdir(parents=True, exist_ok=True)
    items = []
    for f in sorted((ROOT / "dispatches").glob("*.json")):
        d = json.loads(f.read_text())
        stem = f"dispatch-{d['num']:03d}"
        if not (ROOT / "videos" / f"{stem}-x.mp4").exists():
            continue
        vids = {}
        for kind in ("x", "instagram", "vertical"):
            mp4 = ROOT / "videos" / f"{stem}-{kind}.mp4"
            poster = ROOT / "videos" / f"{stem}-{kind}-poster.jpg"
            if not mp4.exists():
                continue
            shutil.copy(mp4, out / "videos" / mp4.name)
            if poster.exists():
                shutil.copy(poster, out / "videos" / poster.name)
            vids[kind] = {"src": f"videos/{mp4.name}", "poster": f"videos/{poster.name}" if poster.exists() else "",
                          "raw": VIDEO_RAW + f"videos/{mp4.name}", "seconds": seconds(mp4),
                          "mb": round(mp4.stat().st_size / 1e6, 1)}
        kitmeta = d.get("kit", {})
        kitfile = ROOT / kitmeta.get("file", f"kits/{stem}-kit.md")
        secs = sections(kitfile.read_text()) if kitfile.exists() else {}
        sched_head, sched = find(secs, "Schedule")
        m = re.search(r"\(([^)]+)\)", sched_head or "")
        _, film = find(secs, "Short caption")
        _, thumb = find(secs, "Thumbnail check")
        items.append({
            "num": d["num"], "id": d["id"], "title": d["title"], "date": d["date"], "place": d["place"],
            "series": d["series"],
            "approved": nice_date(kitmeta.get("approved", "")),
            "scheduled": kitmeta.get("scheduled") or "",
            "postDay": m.group(1) if m else d["date"][5:],
            "videos": vids,
            "kit": {
                "filmCaption": film or kitmeta.get("filmCaption", ""),
                "ytTitle": find(secs, "YouTube Shorts title")[1] or kitmeta.get("youtubeTitle", ""),
                "ytDesc": find(secs, "YouTube Shorts description")[1],
                "tiktok": find(secs, "TikTok caption")[1] or kitmeta.get("tiktokCaption", ""),
                "schedule": [re.sub(r"^[*-]\s*", "", l).strip() for l in sched.splitlines() if l.strip()],
                "thumbnail": thumb,
            },
            "source": {"url": d["video"].get("sourceUrl", ""), "note": d["video"].get("note", "")} if d.get("video") else None,
            "kitUrl": BLOB + str(kitfile.relative_to(ROOT)),
        })
    items.sort(key=lambda x: x["date"][5:])
    tpl = (Path(__file__).parent / "living_press.html").read_text()
    html = tpl.replace("/*DATA*/[]", json.dumps(items, ensure_ascii=False).replace("</", "<\\/"))
    (out / "living-press.html").write_text(html)
    print(f"{len(items)} living card(s) -> {out / 'living-press.html'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "press")
