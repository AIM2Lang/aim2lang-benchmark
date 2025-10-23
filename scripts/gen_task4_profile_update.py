#!/usr/bin/env python3
"""
gen_task5_profile_update.py
---------------------------
Generate benchmark/task5_profile_update.jsonl from aims.jsonl by synthesizing answer_text
that either satisfies or violates rubric items.

Heuristic:
- For each AIM, create one "achieved" answer that mentions first positive rubric item.
- And one "not" answer that mentions confusion / failure based on first negative item.

Usage:
  python gen_task5_profile_update.py --aims data/aims.jsonl --out benchmark/task5_profile_update.jsonl
"""
import argparse, json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aims", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    aims = []
    with open(args.aims, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                aims.append(json.loads(line))

    qid = 1
    items = []
    for a in aims:
        pos = (a.get("rubric",{}) or {}).get("positive", [])
        neg = (a.get("rubric",{}) or {}).get("negative", [])
        if pos:
            items.append({
                "qid": f"t5_{qid:04d}",
                "aim_id": a["aim_id"],
                "answer_text": f"I can {pos[0].lower()}",
                "gold_label": "achieved"
            }); qid += 1
        if neg:
            items.append({
                "qid": f"t5_{qid:04d}",
                "aim_id": a["aim_id"],
                "answer_text": f"I still {neg[0].lower()}",
                "gold_label": "not"
            }); qid += 1

    with open(args.out, "w", encoding="utf-8") as fout:
        for it in items:
            fout.write(json.dumps(it, ensure_ascii=False)+"\n")

    print(f"[OK] Wrote Task5 with {len(items)} items → {args.out}")

if __name__ == "__main__":
    main()
