// Renders Name This puzzle cards from namethis/*.json into cards/namethis-<id>-x.jpg.
// Name This cards carry no dispatch number. They go to X Communities through Typefully.
// Usage: node renderer/namethis.js [id ...]   (no ids = render every Name This card)
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const CHROME = process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";

(async () => {
  const want = process.argv.slice(2);
  const files = fs.readdirSync(path.join(ROOT, "namethis")).filter(f => f.endsWith(".json"))
    .filter(f => !want.length || want.includes(path.basename(f, ".json"))).sort();
  if (!files.length) { console.error("No matching Name This cards."); process.exit(1); }
  const browser = await chromium.launch({ executablePath: fs.existsSync(CHROME) ? CHROME : undefined });
  const page = await browser.newPage();
  await page.goto("file://" + path.join(__dirname, "card.html"));
  for (const f of files) {
    const d = JSON.parse(fs.readFileSync(path.join(ROOT, "namethis", f), "utf8"));
    const dataUrl = "data:image/jpeg;base64," + fs.readFileSync(path.join(ROOT, d.photo)).toString("base64");
    const out = await page.evaluate(([p, u]) => window.renderCards(p, u), [{ format: "namethis", ...d }, dataUrl]);
    const file = path.join(ROOT, "cards", `namethis-${d.id}-x.jpg`);
    fs.writeFileSync(file, Buffer.from(out.x.split(",")[1], "base64"));
    console.log("wrote", path.relative(ROOT, file));
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
