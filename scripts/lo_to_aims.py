#!/usr/bin/env python3
"""
lo_to_aims.py
-------------
Convert LO.xlsx (wide template) -> aims.jsonl and aims.ttl.

Template (sheet 'LO'):
- lo_id, level, skills, topic
- For up to 3 variants per LO: label_a, description_a, rubric_pos_a, rubric_neg_a
                             label_b, description_b, rubric_pos_b, rubric_neg_b
                             label_c, description_c, rubric_pos_c, rubric_neg_c

Usage:
  python lo_to_aims.py --excel LO.xlsx --sheet LO --out_json data/aims.jsonl --out_ttl data/ontology/aims.ttl --domain English

Notes:
- skills: "listening;viewing" (semicolon-separated)
- rubric_pos_* / rubric_neg_*: "item1|item2|..."
- Bloom mapping (simple heuristic) from label/description verbs, can be overridden with --default_bloom.
"""

import argparse, json, re, sys
import pandas as pd
from pathlib import Path

VERB2BLOOM = {
    # very coarse mapping
    "recognize":"remember","identify":"remember","list":"remember","recall":"remember",
    "follow":"understand","classify":"understand","summarize":"understand","explain":"understand",
    "use":"apply","apply":"apply","solve":"apply",
    "analyze":"analyze","compare":"analyze",
    "evaluate":"evaluate","critique":"evaluate",
    "create":"create","compose":"create","write":"create"
}

def guess_bloom(text, default="remember"):
    if not text: return default
    t = text.lower()
    for v, b in VERB2BLOOM.items():
        if re.search(r"\b"+re.escape(v)+r"\b", t):
            return b
    return default

def norm_list(cell, sep=';'):
    if pd.isna(cell) or str(cell).strip() == '':
        return []
    s = str(cell).replace(',', sep)
    return [x.strip() for x in s.split(sep) if x.strip()]

def norm_rubrics(cell):
    if pd.isna(cell) or str(cell).strip() == '':
        return []
    return [x.strip() for x in str(cell).split('|') if x.strip()]

def build_id(domain, level, group_idx, suffix):
    dom2 = (domain or "EN")[:2].upper()
    lvl = (level or "A1").upper()
    return f"AIM.{dom2}.{lvl}.{group_idx:03d}{suffix}"

def to_curie(aim_id):
    return ":" + aim_id.replace(".","_")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--excel", required=True)
    ap.add_argument("--sheet", default="LO")
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--out_ttl", required=True)
    ap.add_argument("--domain", default="English")
    ap.add_argument("--default_bloom", default="remember")
    args = ap.parse_args()

    df = pd.read_excel(args.excel, sheet_name=args.sheet)
    required = ["lo_id","level","skills","topic",
                "label_a","description_a","rubric_pos_a","rubric_neg_a",
                "label_b","description_b","rubric_pos_b","rubric_neg_b",
                "label_c","description_c","rubric_pos_c","rubric_neg_c"]
    for col in required:
        if col not in df.columns:
            print(f"[ERROR] Missing column: {col}", file=sys.stderr); sys.exit(2)

    # assign group index per unique LO id in order of appearance
    unique_los = {lo: i+1 for i, lo in enumerate(pd.unique(df["lo_id"].astype(str)))}

    jsonl_lines = []
    ttl_lines = ['@prefix : <http://example.org/aim#> .',
                 '@prefix aim: <http://example.org/props#> .']

    total = 0
    for _, row in df.iterrows():
        lo_id = str(row["lo_id"]).strip()
        level = str(row["level"]).strip().upper()
        skills = norm_list(row["skills"])
        topic  = "" if pd.isna(row["topic"]) else str(row["topic"]).strip()

        variants = []
        for suf in ["a","b","c"]:
            label = row.get(f"label_{suf}")
            descr = row.get(f"description_{suf}")
            pos   = row.get(f"rubric_pos_{suf}")
            neg   = row.get(f"rubric_neg_{suf}")
            if pd.isna(label) and pd.isna(descr):
                continue
            label = "" if pd.isna(label) else str(label).strip()
            descr = "" if pd.isna(descr) else str(descr).strip()
            pos_l = norm_rubrics(pos)
            neg_l = norm_rubrics(neg)
            variants.append((suf, label, descr, pos_l, neg_l))

        if not variants:
            continue

        group_idx = unique_los[lo_id]
        variant_ids = [build_id(args.domain, level, group_idx, suf) for (suf, *_rest) in variants]

        # chain prereqs within the LO row
        prereq_map = {}
        for i, vid in enumerate(variant_ids):
            prereq_map[vid] = [] if i == 0 else [variant_ids[i-1]]

        for i, (suf, label, descr, pos_l, neg_l) in enumerate(variants):
            vid = variant_ids[i]
            bloom = guess_bloom(label or descr, default=args.default_bloom)
            rec = {
                "aim_id": vid,
                "label": label or f"Sub-AIM {suf.upper()} for {lo_id}",
                "description": descr or "",
                "domain": args.domain,
                "skills": skills,
                "level": level,
                "bloom_level": bloom,
                "topic": topic,
                "rubric": {"positive": pos_l, "negative": neg_l},
                "prereq": prereq_map[vid],
                "advanced": [],
                "related": [x for j, x in enumerate(variant_ids) if j != i],
                "derived_from_lo": lo_id
            }
            jsonl_lines.append(json.dumps(rec, ensure_ascii=False))
            # TTL
            curie = to_curie(vid)
            ttl_lines.append(f'{curie} aim:hasBloomLevel "{bloom}" .')
            for sk in skills:
                ttl_lines.append(f'{curie} aim:hasSkill "{sk}" .')
            for p in prereq_map[vid]:
                ttl_lines.append(f'{curie} aim:hasPrerequisite {to_curie(p)} .')
            for r in rec["related"]:
                ttl_lines.append(f'{curie} aim:hasRelated {to_curie(r)} .')
            ttl_lines.append(f'{curie} aim:derivedFromLO "{lo_id}" .')
            total += 1

    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w", encoding="utf-8") as fout:
        fout.write("\n".join(jsonl_lines))

    Path(args.out_ttl).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_ttl, "w", encoding="utf-8") as fout:
        fout.write("\n".join(ttl_lines))

    print(f"[OK] Wrote {total} AIMs to {args.out_json} and TTL to {args.out_ttl}")

if __name__ == "__main__":
    main()
