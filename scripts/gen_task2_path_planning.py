#!/usr/bin/env python3
"""
gen_task3_path_planning.py
--------------------------
Generate benchmark/task3_path_planning.jsonl from aims.jsonl by unfolding prereq chains.

- For each AIM that has prereq chain (linear within LO row), output main_aim and its gold_path.

Usage:
  python gen_task3_path_planning.py --aims data/aims.jsonl --out benchmark/task3_path_planning.jsonl
"""
import argparse, json, collections

def topo_path(aim_id, prereq_map):
    # follow single-chain prereqs backward to roots
    path = []
    cur = aim_id
    seen = set()
    while cur and cur not in seen:
        seen.add(cur)
        pres = prereq_map.get(cur, [])
        if pres:
            cur = pres[0]
        else:
            break
    # cur is root
    # rebuild forward
    forward = [cur] if cur else []
    while forward[-1] != aim_id:
        nxt = [k for k,v in prereq_map.items() if v and v[0]==forward[-1]]
        if not nxt: break
        forward.append(nxt[0])
    return forward

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

    prereq_map = {a["aim_id"]: a.get("prereq",[]) for a in aims}
    items = []
    qid = 1
    for a in aims:
        if a.get("prereq"):
            path = topo_path(a["aim_id"], prereq_map)
            if len(path)>=2:
                items.append({"qid": f"t3_{qid:04d}", "main_aims":[a["aim_id"]], "gold_path": path})
                qid += 1

    with open(args.out, "w", encoding="utf-8") as fout:
        for it in items:
            fout.write(json.dumps(it, ensure_ascii=False)+"\n")
    print(f"[OK] Wrote Task3 with {len(items)} items → {args.out}")

if __name__ == "__main__":
    main()
