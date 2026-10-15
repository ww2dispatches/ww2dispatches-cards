// Renders WW2 Dispatches post cards from dispatches/*.json into cards/.
// Usage: node renderer/render.js [dispatch-id ...]   (no ids = render every dispatch)
// Each dispatch JSON needs: num, date (YYYY-MM-DD), place, series, pull, photo (path under photos/),
// and optionally focusX, focusY, zoom (same meaning as the Dispatch Press sliders).
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const CHROME = process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";

(async () => {
  const want = process.argv.slice(2);
  const files = fs.readdirSync(path.join(ROOT, "dispatches")).filter(f => f.endsWith(".json"))
    .filter(f => !want.length || want.includes(path.basename(f, ".json"))).sort();
  if (!files.length) { console.error("No matching dispatches."); process.exit(1); }

  const browser = await chromium.launch({ executablePath: fs.existsSync(CHROME) ? CHROME : undefined });
  const page = await browser.newPage();
  await page.goto("file://" + path.join(__dirname, "card.html"));
  fs.mkdirSync(path.join(ROOT, "cards"), { recursive: true });

  for (const f of files) {
    const d = JSON.parse(fs.readFileSync(path.join(ROOT, "dispatches", f), "utf8"));
    const photo = fs.readFileSync(path.join(ROOT, d.photo));
    const dataUrl = "data:image/jpeg;base64," + photo.toString("base64");
    const out = await page.evaluate(([p, u]) => window.renderCards(p, u), [d, dataUrl]);
    const stem = "dispatch-" + String(d.num).padStart(3, "0");
    for (const kind of ["x", "instagram"]) {
      const file = path.join(ROOT, "cards", `${stem}-${kind}.jpg`);
      fs.writeFileSync(file, Buffer.from(out[kind].split(",")[1], "base64"));
      console.log("wrote", path.relative(ROOT, file));
    }
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
