// Builds the Codevertex ERP brochure: cover (full bleed) + body with running heads.
//   NODE_PATH=../../../erp/erp-ui/node_modules node build.cjs && python -I merge.py
// Screenshots are the ERP guide's own (docs/user-guide/erp/assets, written by erp-ui's
// docs-capture suite). The body loads Mermaid from a pinned CDN build, so the build needs internet.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const DIR = __dirname;
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(DIR, 'logo.png')).toString('base64');
const font = "font-family:Helvetica,Arial,sans-serif;font-size:7px;color:#6E5F69;";

// Fill the placeholders from the environment so the client name never lives in a template.
const vars = { DATE: process.env.DOC_DATE || new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' }) };
function render(file) {
  const out = path.join(DIR, '.' + file);
  fs.writeFileSync(out, fs.readFileSync(path.join(DIR, file), 'utf8').replace(/\{\{(\w+)\}\}/g, (m, k) => vars[k] ?? m));
  return out;
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto('file://' + render('cover.html'), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: path.join(DIR, 'cover.pdf'), format: 'A4', printBackground: true, pageRanges: '1', margin: { top: 0, right: 0, bottom: 0, left: 0 } });

  await page.goto('file://' + render('body.html'), { waitUntil: 'load' });
  await page.waitForFunction(() => window.__diagramsDone === true, null, { timeout: 60000 });
  await page.evaluate(() => document.fonts.ready);
  const missing = await page.evaluate(() => [...document.images].filter((i) => !i.complete || i.naturalWidth === 0).map((i) => i.getAttribute('src')));
  if (missing.length) console.warn('missing images:', missing.join(', '));
  await page.pdf({
    path: path.join(DIR, 'body.pdf'), format: 'A4', printBackground: true, tagged: true, outline: true,
    displayHeaderFooter: true,
    margin: { top: '22mm', bottom: '17mm', left: '17mm', right: '17mm' },
    headerTemplate: `<div style="${font}width:100%;margin:0 17mm;padding-bottom:5px;border-bottom:0.6px solid #EADDE6;display:flex;align-items:flex-end;justify-content:space-between">
      <img src="${logo}" style="height:22px"><span>Codevertex ERP &nbsp;|&nbsp; HR, Payroll and Integrated Services</span></div>`,
    footerTemplate: `<div style="${font}width:100%;margin:0 17mm;padding-top:5px;border-top:0.6px solid #EADDE6;display:flex;justify-content:space-between">
      <span>CVX-ERP &nbsp;|&nbsp; ${vars.DATE}</span><span>Codevertex Africa Limited</span>
      <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>`,
  });
  await browser.close();
  for (const f of ['.cover.html', '.body.html']) fs.rmSync(path.join(DIR, f), { force: true });
  console.log('rendered');
})();
