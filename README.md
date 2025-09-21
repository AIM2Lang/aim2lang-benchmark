# aim2lang-benchmark
AI core pipeline is private; only baseline + data are public
## License

This dataset and benchmark are licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You may use, modify, and redistribute it for any purpose — academic or commercial — **with proper attribution**.

aim2lang-bench/
├─ LICENSE
├─ README.md
├─ CITATION.cff
├─ CHANGELOG.md
│
├─ data/                          # Ontology & dữ liệu gốc (nguồn sự thật)
│  ├─ aims.jsonl                  # danh sách AIMs (id, goal, bloom, prereq, rubric, keywords, lesson_id)
│  ├─ lessons.jsonl               # danh sách lesson (id, title, aims_included, resources)
│  ├─ profiles.jsonl              # ví dụ hồ sơ học viên (student_id, achieved_aims, preferences?)
│  ├─ ontology.ttl                # RDF/OWL (tùy chọn, subset demo)
│  └─ splits/                     # nếu bạn muốn chia theo lĩnh vực/khóa
│     ├─ train_ids.txt
│     ├─ dev_ids.txt
│     └─ test_ids.txt
│
├─ benchmark/                     # Các task (input→output) cho chấm điểm
│  ├─ task1_goal2aim.jsonl        # Goal → AIM (mapping)
│  ├─ task2_path_planning.jsonl   # Profile + Target → AIM path
│  ├─ task3_lesson_select.jsonl   # AIM list → Lesson (retrieval/synthesis target)
│  └─ task4_profile_update.jsonl  # Answer + AIM rubric → {achieved|not}
│
├─ metrics/                       # đánh giá chuẩn (để ai cũng tính được)
│  ├─ compute_retrieval.py        # Accuracy@1, Recall@k, MRR, NDCG
│  ├─ compute_path.py             # Path Accuracy, Edit Distance, Prereq Satisfaction
│  ├─ compute_classify.py         # Accuracy, Precision/Recall/F1, Cohen’s Kappa
│  └─ README.md                   # công thức & hướng dẫn chạy nhanh
│
├─ baselines/                     # (tùy chọn mở hay không) baseline tham chiếu
│  ├─ task1_nlp_bm25.py           # BM25/BERT-sim cho Goal→AIM
│  ├─ task2_greedy_path.py        # Greedy/shortest-path theo prerequisite
│  ├─ task3_rag_vanilla.py        # FAISS + simple prompt
│  └─ task4_keyword_rule.py       # keyword/rule grading theo rubric
│
└─ docs/
   ├─ schema.md                   # mô tả field chi tiết
   ├─ tasks.md                    # định nghĩa 4 task (input/output/metric)
   └─ examples/                   # vài ví dụ minh họa (PNG/MD)
