// Renders WW2 Dispatches living cards: the post card bands with archival footage playing in the photo window.
// Usage: node renderer/living.js <dispatch-id> [...]
// The dispatch JSON needs a "video" block: { "footage": "footage/<id>.mp4", "focusX": 50, "focusY": 50, "hook": "..." }
// "hook" is the short line under the pull line on the vertical video (about 45 characters, two lines at most).
// footage/<id>.mp4 is the already trimmed clip (square pixels). Add "sound": true to the video block to keep
// the clip's own audio (period film sound, never music); otherwise a silent track is added. Output goes to videos/:
//   dispatch-NNN-x.mp4 (1600 x 1440), dispatch-NNN-instagram.mp4 (1080 x 1350, Instagram and Facebook),
//   dispatch-NNN-threads.mp4 (1080 x 1350, taller bottom strip for the Threads mute button), dispatch-NNN-vertical.mp4 (1080 x 1920)
// Add --only=x,threads to render just those shapes (the other files are left as they are).
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const CHROME = process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
// Same tone as the still cards: CSS sepia(.12), contrast(1.04)
const TONE = "colorchannelmixer=.927:.092:.023:0:.042:.962:.020:0:.033:.064:.896,eq=contrast=1.04";

(async () => {
  const only = (process.argv.find(a => a.startsWith("--only=")) || "").slice(7).split(",").filter(Boolean);
  const ids = process.argv.slice(2).filter(a => !a.startsWith("--"));
  if (!ids.length) { console.error("Give one or more dispatch ids."); process.exit(1); }
  const browser = await chromium.launch({ executablePath: fs.existsSync(CHROME) ? CHROME : undefined });
  const page = await browser.newPage();
  await page.goto("file://" + path.join(__dirname, "card.html"));
  fs.mkdirSync(path.join(ROOT, "videos"), { recursive: true });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "living-"));

  for (const id of ids) {
    const d = JSON.parse(fs.readFileSync(path.join(ROOT, "dispatches", id + ".json"), "utf8"));
    if (!d.video) { console.error(id, "has no video block"); continue; }
    const src = path.join(ROOT, d.video.footage);
    const fx = (d.video.focusX ?? 50) / 100, fy = (d.video.focusY ?? 50) / 100;
    const out = await page.evaluate(p => window.renderOverlays(p), d);
    const dur = execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]).toString().trim();
    const stem = "dispatch-" + String(d.num).padStart(3, "0");

    const problems = out.vertical.problems;
    if (problems.length) throw new Error(`${id}: ${problems.join("; ")}. Fix the dispatch JSON and render again.`);
    for (const [kind, { png, win }] of Object.entries(out)) {
      if (only.length && !only.includes(kind)) continue;
      const overlay = path.join(tmp, `${stem}-${kind}.png`);
      fs.writeFileSync(overlay, Buffer.from(png.split(",")[1], "base64"));
      const [x, y, w, h] = win;
      const [W, H] = { x: [1600, 1440], instagram: [1080, 1350], threads: [1080, 1350], vertical: [1080, 1920] }[kind];
      const file = path.join(ROOT, "videos", `${stem}-${kind}.mp4`);
      const fc =
        `[0:v]scale=${w}:${h}:force_original_aspect_ratio=increase:flags=lanczos,` +
        `crop=${w}:${h}:(iw-${w})*${fx}:(ih-${h})*${fy},${TONE},setsar=1[ft];` +
        `color=c=black:s=${W}x${H}:r=30[bg];[bg][ft]overlay=${x}:${y}:shortest=1[b];` +
        `[b][1:v]overlay=0:0:shortest=1,format=yuv420p[v]`;
      execFileSync("ffmpeg", ["-v", "error", "-y", "-i", src, "-loop", "1", "-i", overlay,
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-filter_complex", fc, "-map", "[v]", "-map", d.video.sound ? "0:a" : "2:a", "-t", dur,
        "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-profile:v", "high", "-r", "30",
        "-c:a", "aac", "-b:a", d.video.sound ? "160k" : "64k", "-movflags", "+faststart", file]);
      // First frame as a still, for checking the thumbnail
      execFileSync("ffmpeg", ["-v", "error", "-y", "-i", file, "-frames:v", "1", "-q:v", "3", file.replace(/\.mp4$/, "-poster.jpg")]);
      console.log("wrote", path.relative(ROOT, file));
    }
  }
  await browser.close();
  fs.rmSync(tmp, { recursive: true, force: true });
})().catch(e => { console.error(e); process.exit(1); });
