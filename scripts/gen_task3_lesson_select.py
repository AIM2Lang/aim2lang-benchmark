#!/usr/bin/env python3
"""
gen_task4_lesson_select.py
--------------------------
Generate benchmark/task4_lesson_select.jsonl given lessons.jsonl with aims_included.

For each lesson, produce one query with candidate_aim_ids = union of this lesson's aims + a few distractors,
and gold_lesson_ids = [this lesson_id].

Usage:
  python gen_task4_lesson_select.py --lessons data/lessons.jsonl --aims data/aims.jsonl --out benchmark/task4_lesson_select.jsonl --k 3
"""
import argparse, json, random

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lessons", required=True)
    ap.add_argument("--aims", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=3, help="add up to k distractor AIMs")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)

    aims = []
    with open(args.aims, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                aims.append(json.loads(line))
    all_ids = [a["aim_id"] for a in aims]

    lessons = []
    with open(args.lessons, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                lessons.append(json.loads(line))

    items = []
    qid = 1
    for l in lessons:
        gold_aims = l.get("aims_included", [])
        cand = set(gold_aims)
        # distractors
        others = [x for x in all_ids if x not in cand]
        random.shuffle(others)
        cand.update(others[:args.k])
        items.append({
            "qid": f"t4_{qid:04d}",
            "candidate_aim_ids": sorted(cand),
            "gold_lesson_ids": [l["lesson_id"]]
        })
        qid += 1

    with open(args.out, "w", encoding="utf-8") as fout:
        for it in items:
            fout.write(json.dumps(it, ensure_ascii=False)+"\n")
    print(f"[OK] Wrote Task4 with {len(items)} items → {args.out}")

if __name__ == "__main__":
    main()
