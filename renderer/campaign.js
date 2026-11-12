// Renders Campaign Series posts (not cards) from campaign-series/<series>/day-NN.json.
// Usage: node renderer/campaign.js <series> [day ...]   e.g. node renderer/campaign.js pearl-harbor-1941 1 2
// Each day JSON needs: seriesName, day, date (YYYY-MM-DD), place, subtitle, photo (path under the repo),
// and optionally focusX, focusY, zoom. Writes campaign-series/<series>/images/day-NN-x.jpg and -instagram.jpg.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..");
const CHROME = process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
(async () => {
  const [series, ...days] = process.argv.slice(2);
  if (!series) { console.error("Usage: node renderer/campaign.js <series> [day ...]"); process.exit(1); }
  const dir = path.join(ROOT, "campaign-series", series);
  const files = fs.readdirSync(dir).filter(f => /^day-\d+\.json$/.test(f))
    .filter(f => !days.length || days.map(Number).includes(parseInt(f.slice(4)))).sort();
  if (!files.length) { console.error("No matching days."); process.exit(1); }
  const browser = await chromium.launch({ executablePath: fs.existsSync(CHROME) ? CHROME : undefined });
  const page = await browser.newPage();
  await page.goto("file://" + path.join(__dirname, "campaign.html"));
  fs.mkdirSync(path.join(dir, "images"), { recursive: true });
  let bad = 0;
  for (const f of files) {
    const d = JSON.parse(fs.readFileSync(path.join(dir, f), "utf8"));
    const photo = fs.readFileSync(path.join(ROOT, d.photo));
    const out = await page.evaluate(([p, u]) => window.renderCampaign(p, u), [d, "data:image/jpeg;base64," + photo.toString("base64")]);
    const stem = path.basename(f, ".json");
    for (const kind of ["x", "instagram"]) {
      const file = path.join(dir, "images", `${stem}-${kind}.jpg`);
      fs.writeFileSync(file, Buffer.from(out[kind].split(",")[1], "base64"));
      console.log("wrote", path.relative(ROOT, file));
    }
    for (const w of out.warn) { console.log("PROBLEM", stem, w); bad++; }
  }
  await browser.close();
  if (bad) process.exitCode = 2;
})().catch(e => { console.error(e); process.exit(1); });
