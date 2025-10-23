#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lo_pdf_to_lessons.py
--------------------
Chuyển sách PDF (Destination B1, B2, C1&C2) thành JSONL cấu trúc (lesson.jsonl)
có thể dùng làm Knowledge Base hoặc ontology input.

Hỗ trợ:
- PDF số (PyMuPDF)
- PDF scan (pdf2image + pytesseract)
- Tách Unit / Section / Grammar / Vocabulary / Exercises
- Xuất JSONL theo schema Lesson

Usage:
-------
python lo_pdf_to_lessons.py \
  --pdf "Destination B1.pdf" \
  --book_id "DEST.B1" \
  --cefr "B1" \
  --out_dir ./out
"""

import argparse, json, re, os, sys
from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF
import regex as rex
from rapidfuzz import fuzz
from unidecode import unidecode

# Optional OCR
try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ==================== REGEX RULES ====================

UNIT_PATTERNS = [
    rex.compile(r'^\s*unit\s+(\d+)\b', flags=rex.I),
    rex.compile(r'^\s*review\s+unit\s+(\d+)\b', flags=rex.I),
]
SECTION_HEADS = [
    "vocabulary", "grammar", "reading", "listening", "speaking",
    "writing", "use of english", "exam practice", "progress check"
]
VOCAB_LINE = rex.compile(
    r'^\s*([A-Za-z][A-Za-z\-’\']+)\s*(?:\(([a-z]{1,5})\))?\s*[:\-–—]\s*(.+)$'
)
GRAMMAR_HEAD = rex.compile(r'^\s*(grammar|grammar focus|grammar reference)\s*$', rex.I)
VOCAB_HEAD = rex.compile(r'^\s*(vocabulary|word building|phrasal verbs|prepositions)\s*$', rex.I)
EXERCISE_HEAD = rex.compile(r'^\s*exercise\s+(\d+)\b|^\s*(?:a|b|c)\.\s*$', rex.I)
INSTRUCTION_HINT = rex.compile(r'^(choose|match|fill|complete|underline|rewrite|transform|listen)', rex.I)

# ==================== HELPERS ====================

def norm_text(s: str) -> str:
    s = s.replace("\xa0", " ").strip()
    return rex.sub(r"\s+", " ", s)

def guess_section(title: str) -> str:
    tl = title.lower()
    for sec in SECTION_HEADS:
        if sec in tl:
            return sec
    return "section"

def mk_lesson_id(book_id: str, unit_no: int, section: str) -> str:
    base = f"{book_id}.U{unit_no:02d}"
    if section:
        base += f".{section[:2].upper()}"
    return base

# ==================== TEXT EXTRACTION ====================

def extract_pages_text(pdf_path: Path) -> List[Dict[str, Any]]:
    """Trích text theo trang, tự động OCR nếu phát hiện PDF scan."""
    out = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            blocks = page.get_text("blocks")
            texts = [b[4].strip() for b in sorted(blocks, key=lambda x: (x[1], x[0])) if b[4].strip()]
            joined = "\n".join(texts)
            if not joined.strip() and OCR_AVAILABLE:
                # Fallback OCR
                print(f"[OCR] Page {i+1}: no text layer, using pytesseract...")
                image = page.get_pixmap(dpi=300)
                import io
                from PIL import Image
                img = Image.open(io.BytesIO(image.tobytes("png")))
                joined = pytesseract.image_to_string(img, lang="eng")
            out.append({"page": i + 1, "text": joined})
    return out

def segment_units(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Phát hiện các unit theo tiêu đề 'Unit N'."""
    anchors = []
    for p in pages:
        for line in p["text"].splitlines():
            m = UNIT_PATTERNS[0].match(line)
            if m:
                anchors.append((p["page"], int(m.group(1)), "unit"))
                break
            m2 = UNIT_PATTERNS[1].match(line)
            if m2:
                anchors.append((p["page"], int(m2.group(1)), "review"))
                break
    if not anchors:
        anchors = [(1, 1, "unit")]

    anchors.sort(key=lambda x: x[0])
    units = []
    for i, (pg, no, kind) in enumerate(anchors):
        start = pg
        end = pages[-1]["page"] if i == len(anchors) - 1 else anchors[i + 1][0] - 1
        units.append({"unit_no": no, "kind": kind, "start": start, "end": end})
    return units

def split_sections(text: str) -> List[tuple]:
    """Tách section theo tiêu đề chính."""
    lines = [norm_text(x) for x in text.splitlines() if norm_text(x)]
    splits = []
    cur = []
    cur_name = "section"
    for ln in lines:
        if any(ln.lower().startswith(h) for h in SECTION_HEADS) or GRAMMAR_HEAD.match(ln) or VOCAB_HEAD.match(ln):
            if cur:
                splits.append((cur_name, cur))
            cur = [ln]
            cur_name = guess_section(ln)
        else:
            cur.append(ln)
    if cur:
        splits.append((cur_name, cur))
    return splits

def extract_vocab(lines: List[str]) -> List[Dict[str, Any]]:
    vocab = []
    for ln in lines:
        m = VOCAB_LINE.match(ln)
        if m:
            word, pos, rest = m.group(1), m.group(2), m.group(3)
            vocab.append({
                "lemma": word.lower(),
                "pos": pos or None,
                "definition": rest
            })
    return vocab

def extract_grammar(lines: List[str]) -> List[Dict[str, Any]]:
    points = []
    buf, head = [], None
    for ln in lines:
        if GRAMMAR_HEAD.match(ln):
            if buf and head:
                points.append({"title": head, "body": " ".join(buf)})
                buf = []
            head = ln
        else:
            buf.append(ln)
    if buf:
        points.append({"title": head or "grammar", "body": " ".join(buf)})
    return points

def extract_exercises(lines: List[str]) -> List[Dict[str, Any]]:
    items = []
    qbuf, qtitle = [], None
    for ln in lines:
        if EXERCISE_HEAD.match(ln) or INSTRUCTION_HINT.match(ln):
            if qbuf:
                items.append({"instruction": qtitle or "exercise", "body": " ".join(qbuf)})
                qbuf = []
            qtitle = ln
        else:
            qbuf.append(ln)
    if qbuf:
        items.append({"instruction": qtitle or "exercise", "body": " ".join(qbuf)})
    return items

# ==================== CONVERSION ====================

def convert(pdf_path: Path, book_id: str, cefr: str) -> List[Dict[str, Any]]:
    pages = extract_pages_text(pdf_path)
    units = segment_units(pages)

    lessons = []
    for u in units:
        txt = "\n".join(p["text"] for p in pages if u["start"] <= p["page"] <= u["end"])
        sections = split_sections(txt)
        for name, lines in sections:
            lesson = {
                "lessonId": mk_lesson_id(book_id, u["unit_no"], name),
                "title": f"{book_id} – Unit {u['unit_no']} – {name.title()}",
                "source": pdf_path.name,
                "unit": u["unit_no"],
                "pages": f"{u['start']}-{u['end']}",
                "cefr": cefr,
                "skills": [name] if name in SECTION_HEADS else [],
                "objectives": [],
                "vocabulary": extract_vocab(lines),
                "grammarPoints": extract_grammar(lines),
                "exercises": extract_exercises(lines),
                "anchors": {"startPage": u["start"], "endPage": u["end"], "section": name},
                "links": {"aims": [], "concepts": []}
            }
            if name == "vocabulary":
                lesson["objectives"].append(f"learn and practice unit {u['unit_no']} vocabulary")
            elif name == "grammar":
                lesson["objectives"].append(f"understand and apply grammar of unit {u['unit_no']}")
            lessons.append(lesson)
    return lessons

# ==================== MAIN ====================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True, help="Path to PDF (Destination B1/B2/C1&C2)")
    ap.add_argument("--book_id", required=True, help="Book ID, e.g., DEST.B1")
    ap.add_argument("--cefr", required=True, choices=["A1","A2","B1","B2","C1","C2"])
    ap.add_argument("--out_dir", default="./out")
    args = ap.parse_args()

    pdf_path = Path(args.pdf)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    lessons = convert(pdf_path, args.book_id, args.cefr)

    out_file = out_dir / "lesson.jsonl"
    with open(out_file, "w", encoding="utf-8") as f:
        for obj in lessons:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print(f"[OK] Wrote {len(lessons)} lessons → {out_file}")

if __name__ == "__main__":
    main()
