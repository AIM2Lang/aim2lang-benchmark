#!/usr/bin/env python3
"""
pdfs_to_lessons.py
------------------
Convert a folder of PDFs into lessons.jsonl and lessons.ttl with simple heuristics.

Heuristic:
- Each PDF -> multiple lessons based on detected big headings OR fixed page windows.
- Heading detection: lines with ALL CAPS or TitleCase and length in [5,80].
- If no headings found, chunk every N pages (default 5) -> one lesson per chunk.
- Each lesson gets a synthetic lesson_id, collects resource hints (pdf:<file>#pX-Y).

Usage:
  python pdfs_to_lessons.py --pdf_dir ./pdfs --out_json data/lessons.jsonl --out_ttl data/ontology/lessons.ttl --pages_per_chunk 5

Requires: PyPDF2
"""

import argparse, re, os, json
from pathlib import Path
from PyPDF2 import PdfReader

def is_heading(line):
    s = line.strip()
    if len(s) < 5 or len(s) > 80:
        return False
    # Heuristics: all caps or Title Case with few punctuation
    if s.isupper():
        return True
    if re.match(r'^[A-Z][A-Za-z0-9 ]+$', s) and sum(ch in s for ch in "-:()") <= 2:
        return True
    return False

def extract_text_by_page(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []
    for i in range(len(reader.pages)):
        try:
            txt = reader.pages[i].extract_text() or ""
        except Exception:
            txt = ""
        pages.append(txt)
    return pages

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf_dir", required=True)
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--out_ttl", required=True)
    ap.add_argument("--pages_per_chunk", type=int, default=5)
    args = ap.parse_args()

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_ttl).parent.mkdir(parents=True, exist_ok=True)

    lessons = []
    ttl_lines = ['@prefix : <http://example.org/lesson#> .','@prefix l: <http://example.org/lessonprops#> .']

    pdf_dir = Path(args.pdf_dir)
    idx = 1
    for pdf_file in sorted(pdf_dir.glob("*.pdf")):
        pages = extract_text_by_page(pdf_file)
        # detect headings
        headings = []
        for p, txt in enumerate(pages, start=1):
            for line in txt.splitlines():
                if is_heading(line):
                    headings.append((p, line.strip()))
        # build lessons
        pdf_tag = pdf_file.stem.replace(" ", "_")
        if headings:
            # one lesson per heading; page span until next heading
            for h_i, (p_start, title) in enumerate(headings):
                p_end = headings[h_i+1][0]-1 if h_i+1 < len(headings) else len(pages)
                lesson_id = f"LESSON.AUTO.{idx:04d}"
                idx += 1
                lessons.append({
                    "lesson_id": lesson_id,
                    "title": f"{title}",
                    "resources": [f"pdf:{pdf_tag}.pdf#p{p_start}-{p_end}"],
                    "aims_included": []  # can be filled later by mapping script
                })
                ttl_lines.append(f':{lesson_id} l:title "{title}" .')
        else:
            # chunk by pages_per_chunk
            n = len(pages)
            for p_start in range(1, n+1, args.pages_per_chunk):
                p_end = min(n, p_start + args.pages_per_chunk - 1)
                lesson_id = f"LESSON.AUTO.{idx:04d}"
                idx += 1
                title = f"{pdf_tag} p{p_start}-{p_end}"
                lessons.append({
                    "lesson_id": lesson_id,
                    "title": title,
                    "resources": [f"pdf:{pdf_tag}.pdf#p{p_start}-{p_end}"],
                    "aims_included": []
                })
                ttl_lines.append(f':{lesson_id} l:title "{title}" .')

    with open(args.out_json, "w", encoding="utf-8") as fout:
        for l in lessons:
            fout.write(json.dumps(l, ensure_ascii=False)+"\n")
    with open(args.out_ttl, "w", encoding="utf-8") as fout:
        fout.write("\n".join(ttl_lines))

    print(f"[OK] Wrote {len(lessons)} lessons → {args.out_json} and TTL → {args.out_ttl}")

if __name__ == "__main__":
    main()
