#!/usr/bin/env python3
"""
gen_task2_goal2aim.py
---------------------
Generate benchmark/task2_goal2aim.jsonl from aims.jsonl by synthesizing goal_texts.

Heuristic templates per AIM:
- "I want to {label_lower}."
- "Help me to {label_lower}."
- "I need to {label_lower}."

Usage:
  python gen_task2_goal2aim.py --aims data/aims.jsonl --out benchmark/task2_goal2aim.jsonl --per_aim 2
"""
import argparse, json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aims", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--per_aim", type=int, default=2)
    args = ap.parse_args()

    aims = []
    with open(args.aims, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                aims.append(json.loads(line))

    qid = 1
    with open(args.out, "w", encoding="utf-8") as fout:
        for a in aims:
            label = a.get("label","").rstrip(".")
            lower = label[0].lower()+label[1:] if label else ""
            texts = [
                f"I want to {lower}.",
                f"Help me to {lower}.",
                f"I need to {lower}."
            ][:args.per_aim]
            for t in texts:
                obj = {"qid": f"t2_{qid:04d}", "goal_text": t, "gold_aim_ids": [a["aim_id"]]}
                fout.write(json.dumps(obj, ensure_ascii=False)+"\n")
                qid += 1
    print(f"[OK] Wrote Task2 with {qid-1} items → {args.out}")

if __name__ == "__main__":
    main()
