// node render.js <repoRoot> <slides.json> <outDir>
const path = require("path"), fs = require("fs");
const { chromium } = require("playwright");
(async () => {
  const [root, spec, out, mode] = process.argv.slice(2); const IG = mode==="ig"; const H = IG?1350:1920;
  const S = JSON.parse(fs.readFileSync(spec, "utf8"));
  fs.mkdirSync(out, { recursive: true });
  const html = fs.readFileSync(path.join(__dirname, "slide.html"), "utf8").replaceAll("FONTS/", "file://" + path.join(root, "renderer/fonts") + "/");
  const tmp = path.join(__dirname, "_slide.html"); fs.writeFileSync(tmp, html);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: H } });
  await p.goto("file://" + tmp); if (IG) await p.evaluate(()=>{window.IG=true});
  const n = S.slides.length;
  for (let i = 0; i < n; i++) {
    const s = S.slides[i];
    const img = "data:image/jpeg;base64," + fs.readFileSync(path.join(root, s.photo)).toString("base64");
    const r = await p.evaluate(([s, img, i, n]) => render(s, img, i, n), [s, img, i + 1, n]);
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(150);
    const f = path.join(out, `part-01-${IG?"ig":"tiktok"}-${String(i + 1).padStart(2, "0")}.jpg`);
    await p.screenshot({ path: f, type: "jpeg", quality: 90 });
    console.log(f, "panel bottom", Math.round(r.bottom), r.bottom > (IG?1300:1560) ? "PROBLEM: panel runs into the caption zone" : "");
  }
  await b.close();
})();
