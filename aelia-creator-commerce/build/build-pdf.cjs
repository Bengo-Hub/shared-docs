/**
 * AELIA Creator Commerce - System Requirements & Design Document (SRDD) PDF generator.
 *
 * markdown  --markdown-it-->  HTML body  -->  branded HTML shell
 * (cream cover + clickable TOC with Part groupings + flowing sections, inline CSS,
 *  base64 logo, mermaid rendered in-page, inline-SVG charts)  --puppeteer/Chrome-->  A4 PDF.
 *
 * Two passes: pass 1 prints the PDF, pdfjs-dist reads back the real page of every
 * section heading, pass 2 re-prints with exact TOC page numbers.
 *
 * Adapted from processa-integration/architecture/build/build-pdf.cjs (same house style).
 * Run:  npm install && node build-pdf.cjs
 */
'use strict';

const fs   = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');
const { ARCH, BUILD, pickLogo, findChrome, makeMarkdown, mermaidLib } = require('./shared.cjs');

// ── document metadata ─────────────────────────────────────────────────────────
const DOC = {
  md:      'AELIA-Creator-Commerce-System-Requirements-and-Design.md',
  pdf:     'AELIA-Creator-Commerce-System-Requirements-and-Design.pdf',
  title:   'AELIA Creator Commerce System Requirements &amp; Design',
  version: '1.0',
  date:    '28 September 2026',
  contact: 'codevertexitsolutions@gmail.com',
};

const MD   = path.join(ARCH, DOC.md);
const OUT  = path.join(ARCH, DOC.pdf);
const HTML = path.join(BUILD, 'output.html');

const CV_LOGO = pickLogo('codevertex-logo');
const md = makeMarkdown();

// ── palette: warm cream paper + plum brand (house style) ────────────────────
const CREAM = '#faf6ee', CREAM2 = '#f3ece0', PLUM = '#6d2c6d', PLUMD = '#3f1a3f', INK = '#2c2530', MUT = '#7c6f7c';

const CSS = `
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
html,body{background:${CREAM}}
body{font-family:'Helvetica Neue',Helvetica,Arial,'Segoe UI',sans-serif;font-size:10.2pt;color:${INK};line-height:1.55}
@page{size:A4;margin:58px 0 46px;background:${CREAM}}

.doc{padding:0 52px}
.doc h1{display:none}
.doc h2{font-size:15pt;font-weight:800;color:${PLUMD};line-height:1.2;margin:24px 0 13px;padding-bottom:8px;border-bottom:2.5px solid ${PLUM};break-after:avoid;break-inside:avoid}
.doc h2:first-child{margin-top:2px}
.doc h2.part{break-before:page;border:none;margin:0 0 18px;padding:26px 26px 22px;border-radius:10px;
  background:linear-gradient(120deg,${PLUMD},${PLUM} 70%,#a24f9c);color:#fff;font-size:19pt;letter-spacing:.2px}
.doc h2.part + p.part-lead{font-size:10.6pt;color:#4a3f4a;margin:-4px 2px 18px;font-style:italic}
.doc h3{font-size:11.3pt;font-weight:700;color:${PLUM};margin:15px 0 6px;padding-left:10px;border-left:3.5px solid ${PLUM};break-after:avoid;break-inside:avoid}
.doc h4{font-size:10pt;font-weight:700;color:${PLUMD};margin:12px 0 5px;break-after:avoid}
.doc p{margin:0 0 8px}
.doc ul,.doc ol{margin:5px 0 10px 20px}
.doc li{margin-bottom:3px}
.doc strong{color:${PLUMD}}
.doc a{color:${PLUM};text-decoration:none}
.doc hr{display:none}
code{background:#efe6ea;border-radius:3px;padding:1px 4px;font-size:8.4pt;font-family:'Courier New',monospace;color:${PLUM}}

.doc table{width:100%;border-collapse:collapse;margin:6px 0 15px;font-size:8.7pt;break-inside:auto}
.doc thead{display:table-header-group}
.doc tr{break-inside:avoid}
.doc thead th{background:${PLUM};color:#fff;padding:6px 8px;text-align:left;font-weight:600;font-size:8.4pt}
.doc tbody tr:nth-child(even){background:${CREAM2}}
.doc tbody td{padding:5px 8px;border-bottom:1px solid #e3d6cf;vertical-align:top}
.doc tbody td:first-child{font-weight:600;color:${PLUMD}}

.doc blockquote{background:#f4ebe0;border-left:4px solid ${PLUM};border-radius:7px;padding:10px 14px;margin:0 0 12px;font-size:9.5pt;color:#3a2f3a;break-inside:avoid}
.doc blockquote p{margin:0 0 4px}
.doc blockquote p:last-child{margin:0}
.doc blockquote strong{color:${PLUM}}
.doc pre{background:#241726;color:#e9d8ec;border-radius:7px;padding:10px 14px;font-size:8.2pt;font-family:'Courier New',monospace;overflow:hidden;margin:0 0 12px;line-height:1.5;break-inside:avoid;white-space:pre-wrap}
.doc pre code{background:none;color:inherit;padding:0}

.mermaid{margin:10px 0 6px;text-align:center;break-inside:avoid}
.mermaid svg{max-width:100%;height:auto}
.mermaid .edgeLabel rect,.mermaid .label rect{fill:#fbf6ef !important;opacity:1 !important}
.mermaid .edgeLabel,.mermaid .edgeLabel span{background:#fbf6ef !important}
.mermaid .nodeLabel,.mermaid .nodeLabel *,.mermaid .label,.mermaid .label *{color:${INK} !important;fill:${INK} !important}
.fig{font-size:8.4pt;color:${MUT};text-align:center;margin:0 0 14px;font-style:italic}

/* release tags */
.t{display:inline-block;border-radius:9px;padding:0 7px;font-size:7.4pt;font-weight:700;letter-spacing:.3px;white-space:nowrap}
.t-mvp{background:#6d2c6d;color:#fff}
.t-v1{background:#12805f;color:#fff}
.t-later{background:#efe3ea;color:${PLUMD};border:1px solid #d8bfd3}

.doc td code{overflow-wrap:anywhere;word-break:break-word}
.tight table{font-size:7.3pt}
.tight thead th{font-size:7.3pt;padding:5px 5px}
.tight tbody td{padding:4px 5px}

/* layered architecture illustration */
.layers{margin:8px 0 6px;break-inside:avoid}
.ly{border:1.5px solid #c9aec9;border-radius:10px;background:#fbf6ef;padding:7px 9px}
.ly-hub{border-color:${PLUM};background:#f5ecf3}
.ly-t{font-weight:800;color:${PLUM};font-size:8.6pt;margin-bottom:5px;text-transform:uppercase;letter-spacing:.6px}
.ly-r{display:flex;gap:6px}
.ly-b{flex:1;background:#fff;border:1px solid #d8bfd3;border-radius:7px;padding:5px 6px;font-size:7.8pt;line-height:1.3;text-align:center;color:${INK}}
.ly-b b{color:${PLUMD}}
.ly-def{border:2px solid #12805f;background:#eef7f3}
.ly-arrow{text-align:center;color:${PLUM};font-size:8pt;font-weight:700;padding:4px 0}

/* state flow chips */
.stflow{display:flex;flex-wrap:wrap;align-items:center;gap:4px 3px;margin:8px 0 4px;break-inside:avoid}
.st{background:#f2e7f0;border:1.3px solid ${PLUM};border-radius:12px;padding:2px 8px;font-family:'Courier New',monospace;font-size:8pt;color:${PLUMD};font-weight:700}
.st-x{background:#fbeee0;border-color:#b5651d;color:#7a3f0c}
.st-a{color:${PLUM};font-weight:800}
.st-note{font-size:8.2pt;color:${MUT};margin-left:6px}
.st-side{margin:3px 0}

/* swimlane grid */
.swim{display:grid;grid-template-columns:78px repeat(6,1fr);gap:5px;margin:8px 0 6px;break-inside:avoid;font-size:7.8pt;line-height:1.3}
.sw-h{font-weight:800;color:${PLUM};text-align:center;padding:3px 2px;border-bottom:2px solid ${PLUM}}
.sw-lane{background:${PLUMD};color:#fff;font-weight:800;border-radius:7px;display:flex;align-items:center;justify-content:center;text-align:center;padding:4px}
.sw-lane.sw-plat{background:#12805f}
.sw-c{background:#fff;border:1px solid #d8bfd3;border-radius:7px;padding:6px 6px;color:${INK}}
.sw-c.sw-plat{background:#eef7f3;border-color:#9fcfbd}
.sw-c b{color:${PLUMD}}

/* use-case columns */
.uc{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:8px 0 6px;break-inside:avoid}
.uc-col{background:#fbf6ef;border:1px solid #e3d6cf;border-radius:9px;padding:8px 7px}
.uc-actor{background:${PLUM};color:#fff;border-radius:14px;text-align:center;font-weight:800;font-size:8.8pt;padding:4px 6px;margin-bottom:7px}
.uc-item{border:1px solid #d8bfd3;background:#fff;border-radius:12px;padding:3px 7px;font-size:7.8pt;line-height:1.3;margin-bottom:5px;text-align:center;color:${PLUMD}}

/* KPI tiles */
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:8px 0 16px;break-inside:avoid}
.kpi{background:#fbf6ef;border:1px solid #e3d6cf;border-radius:9px;padding:10px 12px}
.kpi b{display:block;font-size:17pt;font-weight:800;color:${PLUMD};line-height:1.1}
.kpi span{display:block;font-size:8pt;color:${MUT};margin-top:3px;line-height:1.3}

/* charts (inline SVG) */
.chart{margin:8px 0 4px;break-inside:avoid;text-align:center}
.chart svg{max-width:100%;height:auto}
.chart text{font-family:'Helvetica Neue',Arial,sans-serif}

/* screen mock illustrations */
.mock{border:1.5px solid #c9aec9;border-radius:10px;background:#fff;margin:8px 0 6px;overflow:hidden;break-inside:avoid;font-size:8.4pt}
.mock .bar{background:${PLUMD};color:#fff;padding:5px 10px;font-weight:700;display:flex;justify-content:space-between}
.mock .body{display:flex;min-height:120px}
.mock .nav{width:130px;background:#f3ece0;padding:8px;border-right:1px solid #e3d6cf}
.mock .nav div{padding:3px 6px;border-radius:4px;margin-bottom:2px;color:${PLUMD}}
.mock .nav div.on{background:${PLUM};color:#fff}
.mock .main{flex:1;padding:9px 11px}
.mock .row{display:flex;gap:8px;margin-bottom:7px}
.mock .card{flex:1;border:1px solid #e3d6cf;border-radius:7px;padding:6px 8px;background:#fbf6ef}
.mock .card b{display:block;color:${PLUMD};font-size:8.8pt}
.mock .card i{color:${MUT};font-style:normal;font-size:7.8pt}
.mock .btn{display:inline-block;background:${PLUM};color:#fff;border-radius:5px;padding:2px 9px;font-weight:700;font-size:7.8pt}
.mock .ghost{display:inline-block;border:1px solid ${PLUM};color:${PLUM};border-radius:5px;padding:1px 8px;font-size:7.8pt}
.mock .line{height:6px;background:#e9dde6;border-radius:3px;margin:4px 0}
.mocks{display:grid;grid-template-columns:1fr 1fr;gap:12px;break-inside:avoid}

.pb{break-after:page;height:0}
.avoid{break-inside:avoid}

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
.cover-bar .cv{height:104px;width:auto}
.cover-bar .for{text-align:right;font-size:8.5pt;color:${MUT};letter-spacing:1.2px;text-transform:uppercase;font-weight:700}
.cover-bar .for b{display:block;font-size:17pt;color:${PLUMD};letter-spacing:3px;margin-top:4px}
.cover .rule{height:2px;background:${PLUM};opacity:.25;margin:6px 0 26px}
.cover-tag{display:inline-block;align-self:flex-start;background:${PLUM};border-radius:5px;padding:4px 13px;font-size:8.5pt;letter-spacing:1.4px;text-transform:uppercase;color:#fff;margin-bottom:16px;font-weight:700}
.cover h1{display:block;font-size:28pt;font-weight:800;line-height:1.14;color:${PLUMD};margin-bottom:14px}
.cover .arrow{color:${PLUM}}
.cover .sub{font-size:11pt;color:#4a3f4a;margin-bottom:24px;max-width:610px;line-height:1.55}
.cover .journey{font-size:9pt;font-weight:700;color:${PLUM};letter-spacing:.4px;margin-bottom:22px}
.cover .badges{display:flex;gap:9px;flex-wrap:wrap;margin-bottom:26px}
.badge{display:inline-block;padding:5px 14px;border-radius:20px;font-size:8.5pt;font-weight:700}
.badge-a{background:#12805f;color:#fff}
.badge-b{background:${PLUM};color:#fff}
.badge-c{background:#efe3ea;color:${PLUMD};border:1px solid #d8bfd3}
.cover .divider{height:1.5px;background:#d8c8bd;margin:auto 0 22px}
.cover .meta{display:grid;grid-template-columns:1fr 1fr;gap:14px 40px}
.cover .meta label{display:block;font-size:7.5pt;text-transform:uppercase;letter-spacing:1px;color:${MUT};margin-bottom:3px;font-weight:700}
.cover .meta span{font-size:10.2pt;font-weight:600;color:${PLUMD}}

/* TOC */
.toc-wrap{padding:0 56px;break-after:page}
.toc-title{font-size:15.5pt;font-weight:800;color:${PLUMD};border-bottom:2.5px solid ${PLUM};padding-bottom:8px;margin-bottom:10px}
.toc{list-style:none}
.toc a{display:flex;justify-content:space-between;align-items:baseline;padding:3.2px 0;border-bottom:1px dotted #cdbcc9;font-size:9.4pt;color:${INK};text-decoration:none}
.toc li.tpart a{border-bottom:none;padding:9px 0 3px;font-weight:800;color:${PLUM};font-size:9.6pt;text-transform:uppercase;letter-spacing:.8px}
.toc li.tsec a{padding-left:14px}
.toc .tt{flex:1;padding-right:12px}
.toc .tp{color:${PLUM};font-weight:700;font-variant-numeric:tabular-nums}
`;

// ── body ──────────────────────────────────────────────────────────────────────
const mdSrc = fs.readFileSync(MD, 'utf8');
let body = md.render(mdSrc);

// id each h2 sequentially; "Part X ..." headings open a new page and group the TOC
const titles = [];
body = body.replace(/<h2>([\s\S]*?)<\/h2>/g, (m, inner) => {
  const id = 'sec-' + titles.length;
  const text = inner.replace(/<[^>]+>/g, '').trim();
  const isPart = /^Part [A-Z]\b/.test(text);
  titles.push({ text, isPart });
  return `<h2 id="${id}"${isPart ? ' class="part"' : ''}>${inner}</h2>`;
});
// release tags: [MVP] [v1] [Later] -> coloured pills
body = body.replace(/\[(MVP|v1|Later)\]/g, (m, t) => `<span class="t t-${t.toLowerCase()}">${t}</span>`);

// a paragraph immediately after a Part heading is its lead-in
body = body.replace(/(<h2 id="sec-\d+" class="part">[\s\S]*?<\/h2>\n)<p>/g, '$1<p class="part-lead">');

function tocHtml(pages) {
  return `
<div class="toc-wrap">
  <div class="toc-title">Table of Contents</div>
  <ul class="toc">
    ${titles.map((t, i) => `<li class="${t.isPart ? 'tpart' : 'tsec'}"><a href="#sec-${i}"><span class="tt">${t.text}</span><span class="tp">${pages && pages[i] ? pages[i] : ''}</span></a></li>`).join('\n    ')}
  </ul>
</div>`;
}

const mermaidSrc = mermaidLib();

const cover = `
<div class="cover">
  <div class="top-rule"></div>
  <div class="cover-bar">
    <img class="cv" src="${CV_LOGO}" alt="Codevertex Africa Limited"/>
    <div class="for">Prepared for<b>AELIA</b>Aelia Holdings Limited</div>
  </div>
  <div class="rule"></div>
  <span class="cover-tag">Confidential &middot; System Requirements &amp; Design Document</span>
  <h1>AELIA Creator Commerce Platform<br/><span class="arrow">&#8594;</span> System Requirements<br/>&amp; Design Document</h1>
  <p class="sub">The single consolidated specification for the AELIA Creator Commerce Platform. It covers
  requirements, delivery methodology, technical architecture, the pluggable integration framework, API,
  data model, UI/UX, security and data protection, payment integration, test and UAT, and the deployment
  and support runbook. The platform is built on the Codevertex ecosystem, and every integration can be
  reconfigured from within AELIA.</p>
  <div class="journey">Marketing Objective &#8594; Creator Match &#8594; Campaign &#8594; Content &#8594; Commerce &#8594; Measurement &#8594; Relationship</div>
  <div class="badges">
    <span class="badge badge-a">MVP Pilot &middot; Month 3</span>
    <span class="badge badge-b">Version 1 &middot; Month 6</span>
    <span class="badge badge-c">Go &middot; Next.js PWA &middot; PostgreSQL &middot; Redis &middot; NATS</span>
    <span class="badge badge-c">Pluggable Integrations</span>
  </div>
  <div class="divider"></div>
  <div class="meta">
    <div><label>Prepared By</label><span>Codevertex Africa Limited &middot; Technical Lead</span></div>
    <div><label>Prepared For</label><span>Aelia Holdings Limited &middot; Product Owner</span></div>
    <div><label>Document Version</label><span>${DOC.version} (Baseline for Development)</span></div>
    <div><label>Date</label><span>${DOC.date}</span></div>
    <div><label>Contact</label><span>${DOC.contact}</span></div>
    <div><label>Classification</label><span>Confidential</span></div>
  </div>
</div>`;

function fullHTML(pages) {
  return `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>
<title>${DOC.title}</title>
<style>${CSS}</style></head><body>
${cover}
${tocHtml(pages)}
<main class="doc">
${body}
</main>
<script>${mermaidSrc}</script>
<script>
// stop mermaid's own on-load pass so the house theme below applies to every diagram
if (window.mermaid) mermaid.initialize({ startOnLoad: false });
window.__render = async function(){
  var errors = [];
  try{
    mermaid.initialize({startOnLoad:false, theme:'base', securityLevel:'loose',
      themeVariables:{ fontFamily:"'Helvetica Neue',Arial,sans-serif", fontSize:'14px',
        primaryColor:'#f2e7f0', primaryBorderColor:'${PLUM}', primaryTextColor:'#2a1a2a',
        lineColor:'#9a6f9a', secondaryColor:'#efe1ec', tertiaryColor:'#fbf6ef',
        mainBkg:'#f2e7f0', clusterBkg:'#fbf6ef', clusterBorder:'#c9aec9',
        actorBkg:'#f2e7f0', actorBorder:'${PLUM}', signalColor:'${PLUMD}', labelBoxBkgColor:'#efe1ec', edgeLabelBackground:'#fbf6ef', transitionLabelColor:'#3f1a3f',
        pie1:'#6d2c6d', pie2:'#12805f', pie3:'#b5651d', pie4:'#9a4a9a', pie5:'#3f7fa6', pie6:'#c9aec9',
        taskBkgColor:'#9a4a9a', taskBorderColor:'${PLUMD}', activeTaskBkgColor:'#12805f', activeTaskBorderColor:'#0b5a43',
        critBkgColor:'#b5651d', critBorderColor:'#8a4a12', doneTaskBkgColor:'#c9aec9', sectionBkgColor:'#f3ece0',
        altSectionBkgColor:'#fbf6ef', gridColor:'#e3d6cf', todayLineColor:'transparent' },
      flowchart:{useMaxWidth:true, htmlLabels:true, curve:'linear'},
      sequence:{useMaxWidth:true, mirrorActors:false},
      gantt:{useMaxWidth:true, barHeight:18, fontSize:11, sectionFontSize:11, leftPadding:150} });
  }catch(e){ return {n:0, errors:['init: '+(e&&e.message||e)]}; }
  // render one diagram at a time so a single bad diagram is reported, not silently fatal
  var nodes = [].slice.call(document.querySelectorAll('.mermaid'));
  for (var i = 0; i < nodes.length; i++){
    try{ await mermaid.init(undefined, nodes[i]); }
    catch(e){ errors.push('#'+i+': '+String(e&&e.message||e).slice(0,160)); }
  }
  // keep every diagram within one printed page: scale down anything taller than MAXH px
  var MAXH = 820;
  [].slice.call(document.querySelectorAll('.mermaid svg')).forEach(function(svg){
    var r = svg.getBoundingClientRect();
    if (r.height > MAXH) { svg.style.maxWidth = Math.floor(r.width * MAXH / r.height) + 'px'; }
  });
  return {n: document.querySelectorAll('.mermaid svg').length, errors: errors};
};
</script>
</body></html>`;
}

// header/footer: cream, natural-colour logo, NO border lines
const HDR = (logo) => `<div style="box-sizing:border-box;width:100%;padding:6px 52px 4px;display:flex;align-items:center;justify-content:space-between;background:${CREAM};font-family:'Helvetica Neue',Arial,sans-serif">
  <img src="${logo}" style="height:22px"/>
  <span style="font-size:7.2pt;color:${MUT};text-align:center;flex:1;padding:0 12px">CONFIDENTIAL &nbsp;&middot;&nbsp; AELIA Creator Commerce &nbsp;&middot;&nbsp; System Requirements &amp; Design Document v${DOC.version}</span>
</div>`;
const FTR = `<div style="box-sizing:border-box;width:100%;padding:4px 52px 6px;display:flex;align-items:center;justify-content:space-between;background:${CREAM};font-family:'Helvetica Neue',Arial,sans-serif">
  <span style="font-size:7.2pt;color:${MUT}">Codevertex Africa Limited for Aelia Holdings Limited</span>
  <span style="font-size:7.2pt;color:${MUT}">${DOC.date}</span>
  <span style="font-size:7.2pt;color:${MUT}">Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
</div>`;

/** Rasterise the (large) SVG logo once to a small PNG for the per-page header; keeps the PDF small. */
async function headerLogo(browser) {
  const page = await browser.newPage();
  await page.setViewport({ width: 400, height: 120, deviceScaleFactor: 3 });
  await page.setContent(`<html><body style="margin:0;background:transparent"><img id="l" src="${CV_LOGO}" style="height:66px"/></body></html>`);
  const el = await page.$('#l');
  const png = await el.screenshot({ omitBackground: true, encoding: 'base64' });
  await page.close();
  return 'data:image/png;base64,' + png;
}

async function print(browser, pages, hdrLogo) {
  fs.writeFileSync(HTML, fullHTML(pages));
  const page = await browser.newPage();
  await page.goto('file://' + HTML.replace(/\\/g, '/'), { waitUntil: 'networkidle0' });
  const r = await page.evaluate(() => window.__render());
  console.log(`mermaid diagrams rendered: ${r.n} of ${(mdSrc.match(/```mermaid/g) || []).length}`);
  if (r.errors.length) console.warn('MERMAID ERRORS:\n  ' + r.errors.join('\n  '));
  await new Promise(r => setTimeout(r, 400));
  await page.pdf({
    path: OUT, format: 'A4', printBackground: true,
    displayHeaderFooter: true, headerTemplate: HDR(hdrLogo), footerTemplate: FTR,
    margin: { top: '44px', right: '0', bottom: '34px', left: '0' },
  });
  await page.close();
}

/** Read back the real page of each h2 title from the printed PDF. */
async function locateSections() {
  const pdfjs = await import('pdfjs-dist/legacy/build/pdf.mjs');
  const doc = await pdfjs.getDocument({ data: new Uint8Array(fs.readFileSync(OUT)), verbosity: 0 }).promise;
  const norm = s => s.replace(/[^A-Za-z0-9]+/g, '').toLowerCase();
  const texts = [];
  for (let p = 1; p <= doc.numPages; p++) {
    const tc = await (await doc.getPage(p)).getTextContent();
    texts.push(norm(tc.items.map(i => i.str).join(' ')));
  }
  // body starts after the TOC; scan forward so repeated titles resolve in order
  let from = texts.findIndex((t, i) => i > 0 && !t.includes('tableofcontents') && texts[i - 1].includes('tableofcontents'));
  if (from < 0) from = 2;
  // TOC may span several pages: skip every page that still carries TOC text
  while (from < texts.length && texts[from].includes('tableofcontents')) from++;
  const pages = [];
  let cursor = from;
  for (const t of titles) {
    const key = norm(t.text.replace(/&amp;/g, '&').replace(/&#?\w+;/g, ' ')).slice(0, 60);
    let found = -1;
    for (let p = cursor; p < texts.length; p++) if (texts[p].includes(key)) { found = p; break; }
    if (found >= 0) { pages.push(found + 1); cursor = found; } else pages.push('');
  }
  return { pages, total: doc.numPages };
}

(async () => {
  const executablePath = findChrome();
  console.log('Chrome:', executablePath);
  const browser = await puppeteer.launch({ executablePath, headless: 'new', args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const hdrLogo = await headerLogo(browser);
  await print(browser, null, hdrLogo);
  const { pages } = await locateSections();
  await print(browser, pages, hdrLogo);
  const check = await locateSections();
  const missing = titles.filter((t, i) => !check.pages[i]).map(t => t.text);
  if (missing.length) console.warn('WARN: sections not located in PDF:', missing);
  await browser.close();
  console.log(`PDF written: ${OUT} (${check.total} pages, ${(fs.statSync(OUT).size / 1024).toFixed(0)} KB)`);
})().catch(e => { console.error(e); process.exit(1); });
