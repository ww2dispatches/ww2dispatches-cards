// Campaign Series Substack art.
// Usage: node renderer/campaign_article.js <series> <part> [part ...]   writes articles/images/part-NN-cover.jpg
//        node renderer/campaign_article.js --banner                       writes campaign-series/brand/ email banner
//        node renderer/campaign_article.js --shot <file.html> <out.png>   full page screenshot of a preview page
// Part records live in campaign-series/<series>/articles/part-NN.json (title, part, parts, first, last, coverPhoto).
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..");
const CHROME = process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
(async () => {
  const args = process.argv.slice(2);
  const browser = await chromium.launch({ executablePath: fs.existsSync(CHROME) ? CHROME : undefined });
  let bad = 0;
  if (args[0] === "--shot") {
    const page = await browser.newPage({ viewport: { width: 1100, height: 900 }, deviceScaleFactor: 1 });
    await page.goto("file://" + path.resolve(args[1]));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(300);
    await page.screenshot({ path: args[2], fullPage: true });
    console.log("wrote", args[2]);
  } else {
    const page = await browser.newPage();
    await page.goto("file://" + path.join(__dirname, "campaign_article.html"));
    if (args[0] === "--banner") {
      const out = await page.evaluate(() => window.renderBanner());
      const dir = path.join(ROOT, "campaign-series", "brand");
      fs.mkdirSync(dir, { recursive: true });
      for (const [k, name] of [["x1", "campaign-series-email-banner.png"], ["x2", "campaign-series-email-banner@2x.png"]]) {
        fs.writeFileSync(path.join(dir, name), Buffer.from(out[k].split(",")[1], "base64"));
        console.log("wrote", path.join("campaign-series/brand", name));
      }
    } else {
      const [series, ...nums] = args;
      const dir = path.join(ROOT, "campaign-series", series, "articles");
      fs.mkdirSync(path.join(dir, "images"), { recursive: true });
      for (const n of nums) {
        const stem = `part-${String(n).padStart(2, "0")}`;
        const p = JSON.parse(fs.readFileSync(path.join(dir, stem + ".json"), "utf8"));
        const photo = fs.readFileSync(path.join(ROOT, p.coverPhoto));
        const out = await page.evaluate(([p, u]) => window.renderCover(p, u), [p, "data:image/jpeg;base64," + photo.toString("base64")]);
        const file = path.join(dir, "images", `${stem}-cover.jpg`);
        fs.writeFileSync(file, Buffer.from(out.cover.split(",")[1], "base64"));
        console.log("wrote", path.relative(ROOT, file));
        for (const w of out.warn) { console.log("PROBLEM", stem, w); bad++; }
      }
    }
  }
  await browser.close();
  if (bad) process.exitCode = 2;
})().catch(e => { console.error(e); process.exit(1); });
