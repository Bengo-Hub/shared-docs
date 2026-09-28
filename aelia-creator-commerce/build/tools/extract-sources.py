#!/usr/bin/env python3
"""Regenerate sources/text/*.txt from the source PDFs in sources/ (grep-able text used for drafting).

    pip install pypdf
    python3 build/tools/extract-sources.py

Pages are separated by a line containing =====PAGE=====.
"""
import glob
import os

from pypdf import PdfReader

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'sources')
OUT = os.path.join(SRC, 'text')
os.makedirs(OUT, exist_ok=True)

for pdf in sorted(glob.glob(os.path.join(SRC, '*.pdf'))):
    reader = PdfReader(pdf)
    text = '\n\n=====PAGE=====\n'.join(page.extract_text() or '' for page in reader.pages)
    target = os.path.join(OUT, os.path.splitext(os.path.basename(pdf))[0] + '.txt')
    with open(target, 'w', encoding='utf8') as f:
        f.write(text)
    print(f'{os.path.relpath(target, ROOT)}: {len(reader.pages)} pages, {len(text):,} chars')
