/**
 * Shared helpers for the branded PDF builds (architecture doc + demo/BPMN presentation).
 * Mirrors finance-service/treasury-api/docs/architecture/build/shared.cjs — ONE logo/browser/
 * markdown pipeline, single brand logo (Codevertex only; no second-party logo for this doc).
 */
'use strict';

const fs = require('fs');
const path = require('path');
const MarkdownIt = require('markdown-it');

const BUILD = __dirname;
const ARCH = path.resolve(BUILD, '..');
const MEDIA = path.join(ARCH, 'media');
const MERMAID_JS = path.join(BUILD, 'node_modules', 'mermaid', 'dist', 'mermaid.min.js');

function dataURI(file) {
  const ext = path.extname(file).slice(1).toLowerCase();
  const mime = ext === 'svg' ? 'image/svg+xml'
             : (ext === 'jpg' || ext === 'jpeg') ? 'image/jpeg' : `image/${ext}`;
  return `data:${mime};base64,` + fs.readFileSync(file).toString('base64');
}

function pickLogo(base) {
  for (const ext of ['png', 'svg', 'jpg', 'jpeg']) {
    const p = path.join(MEDIA, `${base}.${ext}`);
    if (fs.existsSync(p)) return dataURI(p);
  }
  throw new Error(`logo not found: ${base}.{png,svg,...} in ${MEDIA}`);
}

function findChrome() {
  const c = [
    process.env.PUPPETEER_EXECUTABLE_PATH,
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
    '/usr/bin/google-chrome', '/usr/bin/chromium',
  ].filter(Boolean);
  for (const x of c) { try { if (fs.existsSync(x)) return x; } catch (_) {} }
  throw new Error('No Chrome/Edge found. Set PUPPETEER_EXECUTABLE_PATH.');
}

/** markdown-it instance with ```mermaid fences rendered as <div class="mermaid">. */
function makeMarkdown() {
  const md = new MarkdownIt({ html: true, linkify: true, typographer: true });
  const defFence = md.renderer.rules.fence.bind(md.renderer.rules);
  md.renderer.rules.fence = (t, i, o, e, s) =>
    t[i].info.trim() === 'mermaid' ? `<div class="mermaid">${t[i].content}</div>\n` : defFence(t, i, o, e, s);
  return md;
}

function mermaidLib() {
  if (!fs.existsSync(MERMAID_JS)) {
    console.warn('WARN: mermaid.min.js missing - run "npm install".');
    return '';
  }
  return fs.readFileSync(MERMAID_JS, 'utf8');
}

module.exports = { BUILD, ARCH, MEDIA, dataURI, pickLogo, findChrome, makeMarkdown, mermaidLib };
