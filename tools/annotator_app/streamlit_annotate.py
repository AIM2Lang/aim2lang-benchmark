import streamlit as st
import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "aim2lang_annotated.jsonl")
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)

st.set_page_config(page_title="AIM Annotator", layout="centered")
st.title(" AIM2Lang Annotator (Task 2–3)")
st.markdown("Annotate AIM cho từng Goal đầu vào")

# Load existing
annotated = []
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        annotated = [json.loads(line) for line in f]

# Annotation form
goal = st.text_input(" Goal Text (ngôn ngữ tự nhiên)")
main_aim = st.text_area(" Main AIMs (danh sách, phân cách bằng `;`)", help="VD: aim_vocab_greetings; aim_grammar_be")

prereq_aims = st.text_area(" Prerequisite AIMs", help="Các AIM nền tảng cần có trước")
note = st.text_area(" Ghi chú (optional)")

if st.button(" Lưu annotation"):
    if goal and main_aim:
        new_item = {
            "goal_text": goal,
            "main_aim": [x.strip() for x in main_aim.split(";") if x.strip()],
            "prerequisite_aim": [x.strip() for x in prereq_aims.split(";") if x.strip()],
            "note": note
        }
        with open(DATA_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(new_item, ensure_ascii=False) + "\n")
        st.success(" Đã lưu annotation!")

        # Clear fields
        st.rerun()
    else:
        st.warning(" Goal và Main AIM là bắt buộc.")

