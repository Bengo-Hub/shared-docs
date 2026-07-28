/**
 * Codevertex - Sourcing & Traceability Platform (Processa Integration)
 * Technology Architecture PDF generator. Drives the branded PDF from the markdown source.
 *
 * markdown  --markdown-it-->  HTML body  -->  branded HTML shell
 * (cream cover + clickable TOC + flowing sections, inline CSS, base64 logo,
 *  mermaid rendered in-page)  --puppeteer/Chrome-->  A4 PDF.
 *
 * Mirrors finance-service/treasury-api/docs/architecture/build/build-pdf.cjs (same pipeline,
 * single Codevertex logo, rebranded content).
 * Run:  npm install && node build-pdf.cjs
 */
'use strict';

const fs   = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');
const { ARCH, BUILD, pickLogo, findChrome, makeMarkdown, mermaidLib } = require('./shared.cjs');

const MD   = path.join(ARCH, 'processa-integration-architecture.md');
const OUT  = path.join(ARCH, 'Codevertex-Sourcing-Traceability-Architecture.pdf');
const HTML = path.join(BUILD, 'output.html');

const CV_LOGO = pickLogo('codevertex-logo');

const md = makeMarkdown();

const DATE = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'long', year: 'numeric' });
const CONTACT = 'codevertexitsolutions@gmail.com';

// ── palette: warm cream paper + plum brand (house style) ────────────────────
const CREAM = '#faf6ee', CREAM2 = '#f3ece0', PLUM = '#6d2c6d', PLUMD = '#3f1a3f', INK = '#2c2530', MUT = '#7c6f7c';

const CSS = `
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
html,body{background:${CREAM}}
body{font-family:'Helvetica Neue',Helvetica,Arial,'Segoe UI',sans-serif;font-size:10.5pt;color:${INK};line-height:1.55}
@page{size:A4;margin:58px 0 46px;background:${CREAM}}

.doc{padding:0 56px}
.doc h1{display:none}
.doc h2{font-size:15.5pt;font-weight:800;color:${PLUMD};line-height:1.2;margin:26px 0 14px;padding-bottom:8px;border-bottom:2.5px solid ${PLUM};break-after:avoid;break-inside:avoid}
.doc h2:first-child{margin-top:2px}
.doc h3{font-size:11.5pt;font-weight:700;color:${PLUM};margin:15px 0 6px;padding-left:10px;border-left:3.5px solid ${PLUM};break-after:avoid;break-inside:avoid}
.doc h4{font-size:10pt;font-weight:700;color:${PLUMD};margin:12px 0 5px;break-after:avoid}
.doc p{margin:0 0 8px}
.doc ul,.doc ol{margin:5px 0 10px 20px}
.doc li{margin-bottom:4px}
.doc strong{color:${PLUMD}}
.doc a{color:${PLUM};text-decoration:none}
.doc hr{display:none}
code{background:#efe6ea;border-radius:3px;padding:1px 4px;font-size:8.6pt;font-family:'Courier New',monospace;color:${PLUM}}

.doc table{width:100%;border-collapse:collapse;margin:6px 0 15px;font-size:9pt;break-inside:auto}
.doc thead{display:table-header-group}
.doc thead th{background:${PLUM};color:#fff;padding:7px 9px;text-align:left;font-weight:600;font-size:8.6pt}
.doc tbody tr:nth-child(even){background:${CREAM2}}
.doc tbody td{padding:6px 9px;border-bottom:1px solid #e3d6cf;vertical-align:top}
.doc tbody td:first-child{font-weight:600;color:${PLUMD}}

.doc blockquote{background:#f4ebe0;border-left:4px solid ${PLUM};border-radius:7px;padding:10px 14px;margin:0 0 12px;font-size:9.6pt;color:#3a2f3a;break-inside:avoid}
.doc blockquote p{margin:0}
.doc blockquote strong{color:${PLUM}}
.doc pre{background:#241726;color:#e9d8ec;border-radius:7px;padding:11px 15px;font-size:8.5pt;font-family:'Courier New',monospace;overflow:hidden;margin:0 0 12px;line-height:1.55;break-inside:avoid}
.doc pre code{background:none;color:inherit;padding:0}

.mermaid{margin:10px 0 16px;text-align:center;break-inside:avoid}
.mermaid svg{max-width:100%;height:auto}
.mermaid .nodeLabel,.mermaid .nodeLabel *,.mermaid .label,.mermaid .label *{color:${INK} !important;fill:${INK} !important}

/* sign-off */
.signoff{margin-top:12px}
.signoff .sig{border:1px solid #e0d3cb;background:#fbf6ef;border-radius:9px;padding:14px 18px 8px;margin-bottom:14px;break-inside:avoid}
.signoff .sig-h{font-size:9pt;font-weight:800;text-transform:uppercase;letter-spacing:1px;color:${PLUM};margin-bottom:14px}
.signoff .sig-f{margin-bottom:16px}
.signoff .sig-f span{display:block;border-bottom:1.3px solid #b9a7b6;height:20px}
.signoff .sig-f label{display:block;font-size:7.6pt;text-transform:uppercase;letter-spacing:.6px;color:${MUT};margin-top:3px}
.signoff .sig-cols{display:flex;gap:26px}
.signoff .sig-cols .sig-f{flex:1}
.signoff .sig-cols .sig-date{flex:0 0 150px}

/* cover (cream) */
.cover{min-height:calc(297mm - 58px - 46px);background:${CREAM};padding:6px 56px 40px;display:flex;flex-direction:column;position:relative;break-after:page}
.cover .top-rule{height:6px;background:linear-gradient(90deg,${PLUMD},${PLUM} 60%,#a24f9c);border-radius:3px;margin-bottom:26px}
.cover-bar{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.cover-bar .cv{height:112px;width:auto}
.cover .rule{height:2px;background:${PLUM};opacity:.25;margin:6px 0 28px}
.cover-tag{display:inline-block;align-self:flex-start;background:${PLUM};border-radius:5px;padding:4px 13px;font-size:8.5pt;letter-spacing:1.4px;text-transform:uppercase;color:#fff;margin-bottom:16px;font-weight:700}
.cover h1{display:block;font-size:29pt;font-weight:800;line-height:1.14;color:${PLUMD};margin-bottom:16px}
.cover .arrow{color:${PLUM}}
.cover .sub{font-size:11.5pt;color:#4a3f4a;margin-bottom:30px;max-width:600px;line-height:1.55}
.cover .badges{display:flex;gap:9px;flex-wrap:wrap;margin-bottom:30px}
.badge{display:inline-block;padding:5px 14px;border-radius:20px;font-size:8.5pt;font-weight:700}
.badge-a{background:#12805f;color:#fff}
.badge-b{background:${PLUM};color:#fff}
.badge-c{background:#efe3ea;color:${PLUMD};border:1px solid #d8bfd3}
.cover .divider{height:1.5px;background:#d8c8bd;margin:auto 0 22px}
.cover .meta{display:grid;grid-template-columns:1fr 1fr;gap:15px 40px}
.cover .meta label{display:block;font-size:7.5pt;text-transform:uppercase;letter-spacing:1px;color:${MUT};margin-bottom:3px;font-weight:700}
.cover .meta span{font-size:10.5pt;font-weight:600;color:${PLUMD}}

/* TOC */
.toc-wrap{padding:0 56px;break-after:page}
.toc-title{font-size:15.5pt;font-weight:800;color:${PLUMD};border-bottom:2.5px solid ${PLUM};padding-bottom:8px;margin-bottom:14px}
.toc{list-style:none}
.toc a{display:flex;justify-content:space-between;align-items:baseline;padding:7px 0;border-bottom:1px dotted #cdbcc9;font-size:10.5pt;color:${INK};text-decoration:none}
.toc a:hover .tt{color:${PLUM}}
.toc .tt{flex:1;padding-right:12px}
.toc .tp{color:${PLUM};font-weight:700;font-variant-numeric:tabular-nums}
`;

// ── body ──────────────────────────────────────────────────────────────────────
const mdSrc = fs.readFileSync(MD, 'utf8');
let body = md.render(mdSrc);

// id each h2 sequentially + collect titles for the TOC
const titles = [];
body = body.replace(/<h2>([\s\S]*?)<\/h2>/g, (m, inner) => {
  const id = 'sec-' + titles.length;
  titles.push(inner.replace(/<[^>]+>/g, '').trim());
  return `<h2 id="${id}">${inner}</h2>`;
});

const tocHtml = `
<div class="toc-wrap">
  <div class="toc-title">Table of Contents</div>
  <ul class="toc">
    ${titles.map((t, i) => `<li><a href="#sec-${i}"><span class="tt">${t}</span><span class="tp" data-sec="${i}">-</span></a></li>`).join('\n    ')}
  </ul>
</div>`;

const mermaidSrc = mermaidLib();

const cover = `
<div class="cover">
  <div class="top-rule"></div>
  <div class="cover-bar">
    <img class="cv" src="${CV_LOGO}" alt="Codevertex Africa Limited"/>
  </div>
  <div class="rule"></div>
  <span class="cover-tag">Confidential &middot; Ecosystem Integration Architecture</span>
  <h1>Sourcing &amp; Traceability Platform<br/><span class="arrow">&#8596;</span> Codevertex Ecosystem<br/>Technology Architecture</h1>
  <p class="sub">How the agro-processing farm-to-shelf workflow (grower sourcing, intake grading, lot
  traceability, quality assurance, processing, packaging and distribution) integrates into the
  existing Codevertex micro-service fleet — reusing inventory, treasury, logistics, TruLoad, auth,
  erp, subscriptions and notifications, with two new services covering the genuinely new ground.</p>
  <div class="badges">
    <span class="badge badge-a">Reuse-First Architecture</span>
    <span class="badge badge-b">2 New Services</span>
    <span class="badge badge-c">Kubernetes &middot; ArgoCD</span>
    <span class="badge badge-c">Go &middot; Next.js &middot; .NET</span>
  </div>
  <div class="divider"></div>
  <div class="meta">
    <div><label>Prepared By</label><span>Codevertex Africa Limited</span></div>
    <div><label>Submitted To</label><span>Codevertex Engineering</span></div>
    <div><label>Document Version</label><span>1.0</span></div>
    <div><label>Date</label><span>${DATE}</span></div>
    <div><label>Contact</label><span>${CONTACT}</span></div>
    <div><label>Classification</label><span>Confidential</span></div>
  </div>
</div>`;

const fullHTML = `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>
<title>Codevertex - Sourcing &amp; Traceability Platform Technology Architecture</title>
<style>${CSS}</style></head><body>
${cover}
${tocHtml}
<main class="doc">
${body}
</main>
<script>${mermaidSrc}</script>
<script>
window.__render = function(){
  var n = 'ERR';
  try{
    mermaid.initialize({startOnLoad:false, theme:'base', securityLevel:'loose',
      themeVariables:{ fontFamily:"'Helvetica Neue',Arial,sans-serif", fontSize:'14px',
        primaryColor:'#f2e7f0', primaryBorderColor:'${PLUM}', primaryTextColor:'#2a1a2a',
        lineColor:'#9a6f9a', secondaryColor:'#efe1ec', tertiaryColor:'#fbf6ef',
        mainBkg:'#f2e7f0', clusterBkg:'#fbf6ef', clusterBorder:'#c9aec9',
        actorBkg:'#f2e7f0', actorBorder:'${PLUM}', signalColor:'${PLUMD}', labelBoxBkgColor:'#efe1ec' },
      flowchart:{useMaxWidth:true, htmlLabels:true, curve:'linear'}, sequence:{useMaxWidth:true, mirrorActors:false} });
    mermaid.init(undefined, document.querySelectorAll('.mermaid'));
    n = document.querySelectorAll('.mermaid svg').length;
  }catch(e){ n = 'ERR:'+(e&&e.message||e); }
  // compute TOC page numbers for the flowing layout: cover=1, toc=2, body flows from page 3.
  try{
    var CONTENT = 980; // ~A4 content px per page
    var main = document.querySelector('main.doc');
    var sy = window.scrollY, mainTop = main.getBoundingClientRect().top + sy;
    var secs = [].slice.call(main.querySelectorAll('h2[id]'));
    for(var i=0;i<secs.length;i++){
      var top = secs[i].getBoundingClientRect().top + sy;
      var pg = 3 + Math.floor((top - mainTop) / CONTENT);
      var el = document.querySelector('.tp[data-sec="'+i+'"]'); if(el) el.textContent = pg;
    }
  }catch(e){}
  return n;
};
</script>
</body></html>`;
fs.writeFileSync(HTML, fullHTML);

// header/footer: cream, natural-colour logo, NO border lines
const HDR = `<div style="box-sizing:border-box;width:100%;padding:6px 56px 4px;display:flex;align-items:center;justify-content:space-between;background:${CREAM};font-family:'Helvetica Neue',Arial,sans-serif">
  <img src="${CV_LOGO}" style="height:22px"/>
  <span style="font-size:7.2pt;color:${MUT};text-align:center;flex:1;padding:0 12px">CONFIDENTIAL &nbsp;&middot;&nbsp; Sourcing &amp; Traceability Platform Technology Architecture &nbsp;&middot;&nbsp; Codevertex Africa Limited</span>
</div>`;
const FTR = `<div style="box-sizing:border-box;width:100%;padding:4px 56px 6px;display:flex;align-items:center;justify-content:space-between;background:${CREAM};font-family:'Helvetica Neue',Arial,sans-serif">
  <span style="font-size:7.2pt;color:${MUT}">Codevertex Africa Limited &nbsp;&middot;&nbsp; ${CONTACT}</span>
  <span style="font-size:7.2pt;color:${MUT}">${DATE}</span>
  <span style="font-size:7.2pt;color:${MUT}">Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
</div>`;

(async () => {
  const executablePath = findChrome();
  console.log('Chrome:', executablePath);
  const browser = await puppeteer.launch({ executablePath, headless: 'new', args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.goto('file://' + HTML.replace(/\\/g, '/'), { waitUntil: 'networkidle0' });
  const n = await page.evaluate(() => window.__render());
  console.log('mermaid diagrams:', n);
  await new Promise(r => setTimeout(r, 400));
  await page.pdf({
    path: OUT, format: 'A4', printBackground: true,
    displayHeaderFooter: true, headerTemplate: HDR, footerTemplate: FTR,
    margin: { top: '44px', right: '0', bottom: '34px', left: '0' },
  });
  await browser.close();
  console.log(`PDF written: ${OUT} (${(fs.statSync(OUT).size / 1024).toFixed(0)} KB)`);
})().catch(e => { console.error(e); process.exit(1); });
