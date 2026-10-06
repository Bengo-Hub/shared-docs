// Renders one HTML page to PDF. Usage: node render.js <dir> <html> <pdf> <body|cover>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [dir, htmlName, pdfName, kind] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(dir, htmlName), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  const opts = { path: path.join(dir, pdfName), format: 'A4', printBackground: true, tagged: true, outline: true };
  if (kind === 'cover') {
    Object.assign(opts, { margin: { top: '0', bottom: '0', left: '0', right: '0' }, outline: false });
  } else {
    const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(dir, 'logo.png')).toString('base64');
    const font = "font-family:'TeX Gyre Heros',sans-serif;font-size:7.2px;color:#5B6270;";
    Object.assign(opts, {
      displayHeaderFooter: true,
      margin: { top: '22mm', bottom: '18mm', left: '18mm', right: '18mm' },
      headerTemplate: `<div style="${font}width:100%;margin:0 18mm;padding-bottom:5px;border-bottom:0.6px solid #D9DCE3;display:flex;align-items:flex-end;justify-content:space-between">
        <img src="${logo}" style="height:22px">
        <span>Codevertex Boma &nbsp;|&nbsp; SRDD and Shaba Village Launch &nbsp;|&nbsp; v1.0</span></div>`,
      footerTemplate: `<div style="${font}width:100%;margin:0 18mm;padding-top:5px;border-top:0.6px solid #D9DCE3;display:flex;justify-content:space-between">
        <span>Confidential</span><span>Codevertex Africa Limited &nbsp;|&nbsp; www.codevertexafrica.com</span>
        <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>`,
    });
  }
  await page.pdf(opts);
  await browser.close();
})();
