/**
 * Codevertex - Sourcing & Traceability Platform (Processa Integration)
 * PDF generator (landscape, one slide per page) - flow/BPMN-style walkthrough deck.
 *
 * Reuses the SAME logo/browser/markdown helpers as build-pdf.cjs (see shared.cjs) so there is
 * ONE pipeline, not a duplicated one - only the layout/CSS differs (slide deck vs flowing report).
 * Mirrors finance-service/treasury-api/docs/architecture/build/build-presentation.cjs.
 *
 * Source: ../processa-integration-demo-presentation.md - each "## " heading becomes one landscape slide.
 * Run:  cd build && npm install && node build-presentation.cjs
 */
'use strict';

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');
const { ARCH, BUILD, pickLogo, findChrome, makeMarkdown, mermaidLib } = require('./shared.cjs');

const MD   = path.join(ARCH, 'processa-integration-demo-presentation.md');
const OUT  = path.join(ARCH, 'Codevertex-Sourcing-Traceability-Flows.pdf');
const HTML = path.join(BUILD, 'presentation-output.html');

const CV_LOGO = pickLogo('codevertex-logo');
const md = makeMarkdown();

const DATE = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'long', year: 'numeric' });

// palette - same plum brand as the architecture doc, tuned for slide-scale type
const PLUM = '#6d2c6d', PLUMD = '#3f1a3f', INK = '#241f2c', MUT = '#786d78';
const CREAM = '#faf6ee', CREAM2 = '#f3ece0', FISCAL = '#12805f';

const CSS = `
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
html,body{background:${CREAM}}
body{font-family:'Helvetica Neue',Helvetica,Arial,'Segoe UI',sans-serif;color:${INK};line-height:1.45}
@page{size:A4 landscape;margin:0}

.slide{width:297mm;height:210mm;padding:20mm 22mm 16mm;display:flex;flex-direction:column;
  break-after:page;position:relative;background:${CREAM};overflow:hidden}
/* :last-of-type (not :last-child) — the trailing <script> tags after the final .slide in
   the DOM mean :last-child never matches a .slide, so every slide (incl. the true last one)
   was forced to break-after:page, printing one genuinely blank page at the end. :last-of-type
   matches by tag name among siblings, so it correctly targets the final <section>. */
.slide:last-of-type{break-after:auto}
.slide .kicker{font-size:9.5pt;letter-spacing:2px;text-transform:uppercase;color:${PLUM};font-weight:700;margin-bottom:8px;flex:none}
.slide h2{font-size:24pt;font-weight:800;color:${PLUMD};line-height:1.14;margin-bottom:14px;padding-bottom:12px;
  border-bottom:3px solid ${PLUM};max-width:92%;flex:none}
.slide .body{flex:1 1 auto;min-height:0;overflow:hidden;font-size:12.5pt;display:flex;flex-direction:column}
.slide .body p{margin:0 0 10px;max-width:145mm}
.slide .body ul,.slide .body ol{margin:6px 0 12px 22px}
.slide .body li{margin-bottom:7px}
.slide .body strong{color:${PLUMD}}
.slide .body code{background:#efe6ea;border-radius:4px;padding:2px 6px;font-size:10.5pt;
  font-family:'Courier New',monospace;color:${PLUM}}

.slide .body table{width:100%;border-collapse:collapse;margin:8px 0 14px;font-size:11pt}
.slide .body thead th{background:${PLUM};color:#fff;padding:9px 12px;text-align:left;font-weight:600;font-size:10.5pt}
.slide .body tbody tr:nth-child(even){background:${CREAM2}}
.slide .body tbody td{padding:8px 12px;border-bottom:1px solid #e3d6cf;vertical-align:top}
.slide .body tbody td:first-child{font-weight:700;color:${PLUMD}}

.slide .body blockquote{background:#f4ebe0;border-left:5px solid ${PLUM};border-radius:8px;
  padding:12px 16px;margin:4px 0 14px;font-size:11.5pt;color:#3a2f3a;flex:none}
.slide .body blockquote p{margin:0}
.slide .body blockquote strong{color:${PLUM}}

/* Diagram slides: the intro paragraph (if any) stays top-aligned and fixed-height; the
   diagram itself gets the flex-grown remainder and is truly centered both axes — the old
   text-align:center did nothing because the mermaid SVG is a block box, not inline, so
   diagrams rendered hugging the left edge with a large dead zone on the right. */
.slide.has-diagram .body{font-size:11pt}
.slide.has-diagram .body>p{flex:none;margin-bottom:8px}
.mermaid{margin:4px 0;flex:1 1 auto;min-height:0;display:flex;align-items:center;justify-content:center}
.mermaid svg{max-height:145mm !important;max-width:250mm !important;width:auto !important;height:auto !important}
/* A slide that mixes body text (before OR after the diagram) with a diagram must leave
   room for that text — the SVG's max-height is a hard ceiling independent of the flex
   item's actually-allocated space, so at full size it visually overlapped the paragraph
   on both "Reuse-First: The Current Ecosystem" (text after) and "Full Farm-to-Shelf
   Swimlane" (text before). :has() lets one rule catch both orderings. */
.slide.has-diagram .body:has(>p) .mermaid svg{max-height:92mm !important}
.mermaid .nodeLabel,.mermaid .nodeLabel *,.mermaid .label,.mermaid .label *{color:${INK} !important;fill:${INK} !important}

.slide .foot{display:flex;align-items:center;justify-content:space-between;padding-top:8px;
  border-top:1px solid #e3d6cf;font-size:8pt;color:${MUT}}
.slide .foot img{height:14px}
.slide .pageno{font-variant-numeric:tabular-nums;color:${PLUM};font-weight:700}

/* cover slide */
.cover{align-items:flex-start}
.cover .top-rule{height:7px;width:100%;background:linear-gradient(90deg,${PLUMD},${PLUM} 60%,#a24f9c);
  border-radius:4px;margin-bottom:22px}
.cover .bar{display:flex;align-items:center;justify-content:space-between;width:100%;margin-bottom:22px}
.cover .bar .cv{height:70px}
.cover .tag{display:inline-block;background:${PLUM};border-radius:6px;padding:6px 16px;font-size:11pt;
  letter-spacing:2px;text-transform:uppercase;color:#fff;margin-bottom:22px;font-weight:700}
.cover h1{font-size:40pt;font-weight:800;line-height:1.1;color:${PLUMD};margin-bottom:18px;max-width:80%}
.cover .arrow{color:${PLUM}}
.cover .sub{font-size:14pt;color:#4a3f4a;max-width:640px;line-height:1.5;margin-bottom:24px}
.cover .badges{display:flex;gap:12px;flex-wrap:wrap;margin-top:auto;margin-bottom:20px}
.cover .badge{display:inline-block;padding:9px 20px;border-radius:22px;font-size:11pt;font-weight:700}
.cover .b-a{background:${FISCAL};color:#fff}
.cover .b-b{background:${PLUM};color:#fff}
.cover .b-c{background:#efe3ea;color:${PLUMD};border:1px solid #d8bfd3}
.cover .meta{display:grid;grid-template-columns:repeat(3,1fr);gap:14px 40px;width:100%;
  padding-top:16px;border-top:1.5px solid #d8c8bd}
.cover .meta label{display:block;font-size:8.5pt;text-transform:uppercase;letter-spacing:1px;color:${MUT};
  margin-bottom:3px;font-weight:700}
.cover .meta span{font-size:12pt;font-weight:600;color:${PLUMD}}
`;

// ── slice the markdown into slides on top-level "## " headings ──────────────
const mdSrc = fs.readFileSync(MD, 'utf8');
// drop the leading "# Title" line + its HTML comment note before splitting
const bodySrc = mdSrc.replace(/^#\s+.*\n/, '').replace(/<!--[\s\S]*?-->\n?/, '');
const rawSlides = bodySrc.split(/\n(?=## )/).map(s => s.trim()).filter(Boolean);

const slideHtml = rawSlides.map((chunk, i) => {
  const titleMatch = chunk.match(/^##\s+(.+)$/m);
  const title = titleMatch ? titleMatch[1].trim() : `Slide ${i + 1}`;
  const rest = chunk.replace(/^##\s+.+\n?/, '');
  const rendered = md.render(rest);
  const hasDiagram = /```mermaid/.test(rest);
  return `<section class="slide${hasDiagram ? ' has-diagram' : ''}">
    <div class="kicker">Codevertex &middot; Sourcing &amp; Traceability &middot; Slide ${i + 2} of ${rawSlides.length + 1}</div>
    <h2>${title}</h2>
    <div class="body">${rendered}</div>
    <div class="foot"><img src="${CV_LOGO}"/><span>Confidential &middot; Ecosystem Integration Walkthrough</span></div>
  </section>`;
}).join('\n');

const cover = `<section class="slide cover">
  <div class="top-rule"></div>
  <div class="bar">
    <img class="cv" src="${CV_LOGO}" alt="Codevertex Africa Limited"/>
  </div>
  <span class="tag">Ecosystem Integration &middot; Flow &amp; Data-Flow Walkthrough</span>
  <h1>Sourcing &amp; Traceability<br/><span class="arrow">&#8596;</span> Codevertex Ecosystem</h1>
  <p class="sub">Farm-to-shelf, end to end: how grower intake, weighbridge grading, lot traceability,
  quality assurance, processing, packaging, distribution and grower settlement move through the
  existing Codevertex services plus two new ones — without duplicating a single system of record.</p>
  <div class="badges">
    <span class="badge b-a">Reuse-First</span>
    <span class="badge b-b">2 New Services</span>
    <span class="badge b-c">sourcing-api &middot; traceability-api</span>
  </div>
  <div class="meta">
    <div><label>Prepared By</label><span>Codevertex Africa Limited</span></div>
    <div><label>Submitted To</label><span>Codevertex Engineering</span></div>
    <div><label>Date</label><span>${DATE}</span></div>
  </div>
</section>`;

const mermaidSrc = mermaidLib();

const fullHTML = `<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>
<title>Codevertex - Sourcing &amp; Traceability Flows</title>
<style>${CSS}</style></head><body>
${cover}
${slideHtml}
<script>${mermaidSrc}</script>
<script>
window.__render = function(){
  var n = 'ERR';
  try{
    mermaid.initialize({startOnLoad:false, theme:'base', securityLevel:'loose',
      themeVariables:{ fontFamily:"'Helvetica Neue',Arial,sans-serif", fontSize:'16px',
        primaryColor:'#f2e7f0', primaryBorderColor:'${PLUM}', primaryTextColor:'#2a1a2a',
        lineColor:'#9a6f9a', secondaryColor:'#efe1ec', tertiaryColor:'#fbf6ef',
        mainBkg:'#f2e7f0', clusterBkg:'#fbf6ef', clusterBorder:'#c9aec9',
        actorBkg:'#f2e7f0', actorBorder:'${PLUM}', signalColor:'${PLUMD}', labelBoxBkgColor:'#efe1ec' },
      flowchart:{useMaxWidth:true, htmlLabels:true, curve:'linear'}, sequence:{useMaxWidth:true, mirrorActors:false} });
    mermaid.init(undefined, document.querySelectorAll('.mermaid'));
    n = document.querySelectorAll('.mermaid svg').length;
  }catch(e){ n = 'ERR:'+(e&&e.message||e); }
  return n;
};
</script>
</body></html>`;
fs.writeFileSync(HTML, fullHTML);

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
    path: OUT, landscape: true, format: 'A4', printBackground: true,
    displayHeaderFooter: false, margin: { top: '0', right: '0', bottom: '0', left: '0' },
  });
  await browser.close();
  console.log(`PDF written: ${OUT} (${(fs.statSync(OUT).size / 1024).toFixed(0)} KB)`);
})().catch(e => { console.error(e); process.exit(1); });
