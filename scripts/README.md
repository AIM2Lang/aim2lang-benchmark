# AIM2Lang Script Kit (self-host)

## Install
```bash
pip install -r requirements.txt
```

## 1 LO.xlsx → AIMs.jsonl + aims.ttl
Your Excel must have sheet `LO` with columns:
`lo_id, level, skills, topic,` and for variants `a/b/c`:
`label_*, description_*, rubric_pos_*, rubric_neg_*`

```bash
python lo_to_aims.py --excel LO.xlsx --sheet LO   --out_json data/aims.jsonl   --out_ttl data/ontology/aims.ttl   --domain English
```

## 2 PDFs → lessons.jsonl + lessons.ttl
Put your 3 PDFs in a folder, e.g. `./pdfs`:
```bash
python pdfs_to_lessons.py --pdf_dir ./pdfs   --out_json data/lessons.jsonl   --out_ttl data/ontology/lessons.ttl   --pages_per_chunk 5
```

(Optional) map lessons to AIMs via keyword Jaccard:
```bash
python map_lessons_to_aims.py --aims data/aims.jsonl   --lessons data/lessons.jsonl   --out data/lessons.mapped.jsonl --topk 2
```

## 3 Generate benchmark tasks
```bash
# Task 2: Goal → AIM(s)
python gen_task2_goal2aim.py --aims data/aims.jsonl   --out benchmark/task2_goal2aim.jsonl --per_aim 2

# Task 3: AIM Path Planning
python gen_task3_path_planning.py --aims data/aims.jsonl   --out benchmark/task3_path_planning.jsonl

# Task 4: Lesson Selection
python gen_task4_lesson_select.py --lessons data/lessons.mapped.jsonl   --aims data/aims.jsonl   --out benchmark/task4_lesson_select.jsonl --k 3

# Task 5: Adaptive Progress Tracking
python gen_task5_profile_update.py --aims data/aims.jsonl   --out benchmark/task5_profile_update.jsonl
```

> Task 1 (Goal Understanding) thường là conceptual. Bạn có thể tự gán nhãn `topic/skill/bloom/intent_type` cho một tập nhỏ để làm gold.

## Notes
- Heuristics intentionally simple để bạn dễ đổi logic: Bloom mapping, heading detection, Jaccard.
- TTL namespaces dùng `http://example.org/...`; đổi sang domain riêng khi deploy.
