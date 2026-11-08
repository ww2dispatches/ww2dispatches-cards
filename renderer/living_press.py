"""Builds the Living Press page: every dispatch that has a Living Card (archival film) or a Story Card
(narrated archival photos, labelled "The Story"), with its press kit.

Usage: python3 renderer/living_press.py <out_dir>
Writes <out_dir>/living-press.html and copies the videos and posters into <out_dir>/videos/,
ready to publish as a claude.ai artifact (the page plays the videos from its own published files).
Videos and posters come from R2 (media.ww2dispatches.com): a matching local copy in videos/ is used as it is,
anything else is downloaded into ~/.cache/ww2dispatches-media/, so no separate copy step is needed.
"""
import json, re, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import media

ROOT = Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/ww2dispatches/ww2dispatches-cards/main/"
BLOB = "https://github.com/ww2dispatches/ww2dispatches-cards/blob/main/"


def have(rel):
    """Local path of the newest R2 copy of a repo-relative file (downloaded if needed), or None if it isn't on R2."""
    got = media.get(rel, cache=True)  # never overwrites files tracked in this repo
    return Path(got) if got else None


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
        st = d.get("story") or {}
        story_rel = st.get("video", f"videos/{stem}-story-am_onyx.mp4")
        story_mp4 = have(story_rel) if st else None
        if story_mp4:
            dest = out / "videos" / story_mp4.name
            if story_mp4.stat().st_size > 14e6:
                # Artifacts take at most 15 MB per file, so the page gets a lighter review copy; Buffer uses the full file.
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(story_mp4), "-c:v", "libx264", "-crf", "30", "-preset", "slow",
                                "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(dest)], check=True)
            else:
                shutil.copy(story_mp4, dest)
            sk = st.get("kit", {})
            items.append({
                "type": "story", "num": d["num"], "id": d["id"] + "-story", "title": d["title"], "date": d["date"],
                "place": d["place"], "series": d["series"],
                "approved": nice_date(sk.get("approved", "")),
                "scheduled": sk.get("scheduled") or ("Scheduled on all six channels" if len(st.get("buffer", {})) >= 6 else ""),
                "postDay": nice_date(d["date"])[:-5] if not st.get("postDate") else nice_date(st["postDate"]),
                "videos": {"story": {"src": f"videos/{story_mp4.name}", "poster": "", "raw": media.url(story_rel),
                                     "seconds": seconds(story_mp4), "mb": round(story_mp4.stat().st_size / 1e6, 1)}},
                "kit": {"filmCaption": sk.get("caption", ""), "ytTitle": sk.get("youtubeTitle", ""),
                        "ytDesc": sk.get("youtubeDescription", ""), "tiktok": sk.get("tiktokCaption", ""),
                        "schedule": sk.get("schedule", []), "thumbnail": sk.get("thumbnail", "")},
                "source": {"url": "", "note": json.loads((ROOT / st["script"]).read_text()).get("note", "")} if st.get("script") else None,
                "kitUrl": BLOB + st.get("script", ""),
            })
        # The film video, and a second cut of the same film for the 7 p.m. slot (video_b, kit_b, dispatch-NNN-b-*).
        for key in ("", "_b"):
            vstem = stem + ("-b" if key else "")
            if not media.exists(f"videos/{vstem}-x.mp4"):
                continue
            vids = {}
            for kind in ("x", "instagram", "vertical"):
                mp4 = have(f"videos/{vstem}-{kind}.mp4")
                poster = have(f"videos/{vstem}-{kind}-poster.jpg")
                if not mp4:
                    continue
                shutil.copy(mp4, out / "videos" / mp4.name)
                if poster:
                    shutil.copy(poster, out / "videos" / poster.name)
                vids[kind] = {"src": f"videos/{mp4.name}", "poster": f"videos/{poster.name}" if poster else "",
                              "raw": media.url(f"videos/{vstem}-{kind}.mp4"), "seconds": seconds(mp4),
                              "mb": round(mp4.stat().st_size / 1e6, 1)}
            kitmeta = d.get("kit" + key, {})
            kitfile = ROOT / kitmeta.get("file", f"kits/{vstem}-kit.md")
            secs = sections(kitfile.read_text()) if kitfile.exists() else {}
            sched_head, sched = find(secs, "Schedule")
            m = re.search(r"\(([^)]+)\)", sched_head or "")
            _, film = find(secs, "Short caption")
            _, thumb = find(secs, "Thumbnail check")
            items.append({
                "type": "living", "num": d["num"], "id": d["id"] + ("-b" if key else ""),
                "title": d["title"] + (" (second cut, 7 p.m.)" if key else ""), "date": d["date"], "place": d["place"],
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
                "source": {"url": d["video" + key].get("sourceUrl", ""), "note": d["video" + key].get("note", "")} if d.get("video" + key) else None,
                "kitUrl": BLOB + str(kitfile.relative_to(ROOT)),
            })
    items.sort(key=lambda x: x["date"][5:])
    tpl = (Path(__file__).parent / "living_press.html").read_text()
    html = tpl.replace("/*DATA*/[]", json.dumps(items, ensure_ascii=False).replace("</", "<\\/"))
    (out / "living-press.html").write_text(html)
    print(f"{len(items)} video(s) -> {out / 'living-press.html'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "press")
