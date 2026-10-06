// Renders an SVG to a PNG of the given width. Usage: node render_png.js <in.svg> <out.png> <width>
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const [src, dst, width] = process.argv.slice(2);
  const svg = fs.readFileSync(src, 'utf8');
  const m = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
  const w = Number(width);
  const h = Math.round((w * Number(m[2])) / Number(m[1]));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  const sized = svg.replace(/width="[\d.]+" height="[\d.]+"/, `width="${w}" height="${h}"`);
  await page.setContent(`<html><body style="margin:0;background:transparent">${sized}</body></html>`);
  await page.screenshot({ path: dst, omitBackground: true, clip: { x: 0, y: 0, width: w, height: h } });
  await browser.close();
})();
