/**
 * Visual QA: screenshot regions of the rendered SRDD (build/output.html) in print media.
 *
 *   node tools/preview.cjs '.cover' '#sec-22' '#sec-37 ~ div.mermaid'
 *
 * Each CSS selector yields one 794x1100 px (A4-width) PNG starting at that element, written to
 * build/shots/shot-N.png. Run `node build-pdf.cjs` first so output.html is current. Section ids
 * are sequential over the `##` headings: list them with
 *   grep -o 'id="sec-[0-9]*"[^>]*>[^<]*' output.html
 */
'use strict';

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');
const { BUILD, findChrome } = require('../shared.cjs');

const HTML = path.join(BUILD, 'output.html');
const OUT = path.join(BUILD, 'shots');

(async () => {
  const selectors = process.argv.slice(2);
  if (!selectors.length) { console.error('usage: node tools/preview.cjs <css-selector>...'); process.exit(2); }
  if (!fs.existsSync(HTML)) { console.error('output.html missing - run: node build-pdf.cjs'); process.exit(1); }
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await puppeteer.launch({ executablePath: findChrome(), headless: 'new', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 794, height: 1100, deviceScaleFactor: 1.3 });
  await page.emulateMediaType('print');
  await page.goto('file://' + HTML.replace(/\\/g, '/'), { waitUntil: 'networkidle0' });
  const r = await page.evaluate(() => window.__render());
  console.log(`mermaid diagrams rendered: ${r.n}` + (r.errors.length ? `, errors: ${r.errors.join('; ')}` : ''));
  await new Promise(res => setTimeout(res, 500));

  for (const [i, sel] of selectors.entries()) {
    const y = await page.evaluate(s => {
      const e = document.querySelector(s);
      return e ? e.getBoundingClientRect().top + window.scrollY : -1;
    }, sel);
    if (y < 0) { console.log(`not found: ${sel}`); continue; }
    const file = path.join(OUT, `shot-${i}.png`);
    await page.screenshot({ path: file, clip: { x: 0, y: Math.max(0, y - 10), width: 794, height: 1100 }, captureBeyondViewport: true });
    console.log(`${sel} -> ${path.relative(process.cwd(), file)}`);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
