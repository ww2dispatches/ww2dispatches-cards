// Renders Name This puzzle cards from namethis/*.json.
//   cards/namethis-<id>-x.jpg        the posted card (1600 x 1440). X Communities through Typefully.
//   cards/namethis-<id>-game-q.jpg   Declass puzzle side (1080 x 1350): "Can you name it?" and the clue
//   cards/namethis-<id>-game-a.jpg   Declass answer side (1080 x 1350): "Answer declassified" and the answer
// Name This cards carry no dispatch number.
// Usage: node renderer/namethis.js [--game-only] [id ...]   (no ids = every Name This card;
//        --game-only leaves the posted card alone, for back filling the game images)
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const CHROME = process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";

// "Boeing B-17 Flying Fortress (B-17D)" -> "Boeing B-17 Flying Fortress"
const answerLine = a => "Answer: " + String(a || "").replace(/\s*\([^)]*\)\s*$/, "").trim();

(async () => {
  const args = process.argv.slice(2);
  const gameOnly = args.includes("--game-only");
  const want = args.filter(a => !a.startsWith("--"));
  const files = fs.readdirSync(path.join(ROOT, "namethis")).filter(f => f.endsWith(".json"))
    .filter(f => !want.length || want.includes(path.basename(f, ".json"))).sort();
  if (!files.length) { console.error("No matching Name This cards."); process.exit(1); }
  const browser = await chromium.launch({ executablePath: fs.existsSync(CHROME) ? CHROME : undefined });
  const page = await browser.newPage();
  await page.goto("file://" + path.join(__dirname, "card.html"));
  const write = (name, dataUrl) => {
    const file = path.join(ROOT, "cards", name);
    fs.writeFileSync(file, Buffer.from(dataUrl.split(",")[1], "base64"));
    console.log("wrote", path.relative(ROOT, file));
  };
  for (const f of files) {
    const d = JSON.parse(fs.readFileSync(path.join(ROOT, "namethis", f), "utf8"));
    if (!d.photo || !fs.existsSync(path.join(ROOT, d.photo))) { console.error(`skipped ${d.id}: photo file missing`); continue; }
    const dataUrl = "data:image/jpeg;base64," + fs.readFileSync(path.join(ROOT, d.photo)).toString("base64");
    const q = await page.evaluate(([p, u]) => window.renderCards(p, u), [{ format: "namethis", ...d }, dataUrl]);
    if (!gameOnly) write(`namethis-${d.id}-x.jpg`, q.x);
    write(`namethis-${d.id}-game-q.jpg`, q.instagram);
    const a = await page.evaluate(([p, u]) => window.renderCards(p, u),
      [{ format: "namethis", ...d, subline: "Answer declassified", pull: answerLine(d.answer) }, dataUrl]);
    write(`namethis-${d.id}-game-a.jpg`, a.instagram);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
