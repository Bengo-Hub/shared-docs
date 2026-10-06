// Renders hadia-srdd.html to PDF with page numbers in the footer.
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const dir = process.argv[2];
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(dir, 'hadia-srdd.html'), { waitUntil: 'load' });
  const footer = `<div style="font-family:'DejaVu Sans',sans-serif;font-size:7px;color:#5B6270;width:100%;padding:0 16mm;display:flex;justify-content:space-between">
    <span>Hadia Gifting Registry SRDD, v1.0. Confidential.</span>
    <span>Codevertex Africa Limited</span>
    <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>`;
  await page.pdf({
    path: path.join(dir, 'Hadia-Gifting-Registry-SRDD-Codevertex.pdf'),
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: footer,
    margin: { top: '16mm', bottom: '18mm', left: '16mm', right: '16mm' },
    tagged: true,
    outline: true,
  });
  await browser.close();
})();
