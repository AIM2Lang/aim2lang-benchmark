#!/usr/bin/env python3
"""
map_lessons_to_aims.py
----------------------
Populate lessons.jsonl.aims_included by matching lesson titles/resources to AIM labels/descriptions/topics.

Usage:
  python map_lessons_to_aims.py --aims data/aims.jsonl --lessons data/lessons.jsonl --out data/lessons.mapped.jsonl --topk 3

Heuristic:
- Tokenize lowercase words from lesson.title and AIM (label+description+topic).
- Compute Jaccard similarity; keep top-K matches over a threshold.
"""

import argparse, json, re
from collections import defaultdict

def tok(s):
    return {w for w in re.findall(r"[a-zA-Z]+", (s or "").lower()) if len(w) > 2}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aims", required=True)
    ap.add_argument("--lessons", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--topk", type=int, default=2)
    ap.add_argument("--min_jaccard", type=float, default=0.15)
    args = ap.parse_args()

    aims = []
    with open(args.aims, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                aims.append(json.loads(line))

    lessons = []
    with open(args.lessons, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                lessons.append(json.loads(line))

    aim_idx = []
    for a in aims:
        text = " ".join([a.get("label",""), a.get("description",""), a.get("topic","")])
        aim_idx.append((a["aim_id"], tok(text)))

    out_lines = []
    for l in lessons:
        ltoks = tok(l.get("title","") + " " + " ".join(l.get("resources",[])))
        scored = []
        for aid, atoks in aim_idx:
            if not atoks: continue
            inter = ltoks & atoks
            union = ltoks | atoks
            j = len(inter)/len(union) if union else 0.0
            if j >= args.min_jaccard:
                scored.append((j, aid))
        scored.sort(reverse=True)
        l["aims_included"] = [aid for (_j, aid) in scored[:args.topk]]
        out_lines.append(l)

    with open(args.out, "w", encoding="utf-8") as fout:
        for obj in out_lines:
            fout.write(json.dumps(obj, ensure_ascii=False)+"\n")

    print(f"[OK] Updated {len(out_lines)} lessons with aims_included → {args.out}")

if __name__ == "__main__":
    main()
