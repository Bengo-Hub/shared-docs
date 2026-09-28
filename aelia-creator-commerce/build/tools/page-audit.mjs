/**
 * Layout QA: one line per PDF page with its body-text length and opening words, so near-empty
 * pages (orphaned headings, diagrams pushed to the next page) stand out.
 *
 *   node tools/page-audit.mjs            # audit the SRDD PDF
 *   node tools/page-audit.mjs 700        # only pages with fewer than 700 characters
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const BUILD = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PDF = path.resolve(BUILD, '..', 'AELIA-Creator-Commerce-System-Requirements-and-Design.pdf');
const below = Number(process.argv[2] || Infinity);

const pdfjs = await import('pdfjs-dist/legacy/build/pdf.mjs');
const doc = await pdfjs.getDocument({ data: new Uint8Array(fs.readFileSync(PDF)), verbosity: 0 }).promise;
for (let p = 1; p <= doc.numPages; p++) {
  const text = (await (await doc.getPage(p)).getTextContent()).items.map(i => i.str).join(' ').replace(/\s+/g, ' ');
  // strip the running header and footer so only body text is measured
  const bodyText = text.replace(/CONFIDENTIAL.*?v\d+\.\d+/, '').replace(/Codevertex Africa Limited for Aelia.*$/, '').trim();
  if (bodyText.length < below) console.log(String(p).padStart(3), String(bodyText.length).padStart(5), bodyText.slice(0, 90));
}
console.log(`${doc.numPages} pages`);
