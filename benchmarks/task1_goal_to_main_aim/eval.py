import json

with open("data/aim2lang_dataset.jsonl", "r", encoding="utf-8") as f:
    data = [json.loads(line) for line in f]