# AIM2Lang Task Definition

AIM2Lang defines a 5-task benchmark pipeline to evaluate goal-based personalized instruction in language learning, centered around the AIM (Atomic Instructional Module) concept.

---

## Task 1 – Goal Understanding

- **Input**: `goal_text` (natural language)
- **Output**: Parsed goal metadata:
  - `topic`: topic of learning (e.g., "email", "travel")
  - `skill`: CEFR-aligned skill type (e.g., writing, speaking)
  - `bloom_level`: Bloom taxonomy level (e.g., apply, analyze)
  - `intent_type`: type of learning goal (e.g., task-based, concept-based)

- **Objective**: Convert free-form learner intent into structured representation  
- **Metric**: *Not benchmarked yet*  
- **Status**: Conceptual only (schema defined, no benchmark yet)

---

## Task 2 – Main AIM Mapping

- **Input**: `goal_text`  
- **Output**: `main_aims` – list of AIM IDs representing primary learning objectives  
- **Objective**: Select the most relevant AIMs that directly fulfill the learner’s goal  
- **Metric**:
  - Exact Match (primary)
  - Precision/Recall (optional)  
- **Status**: *Benchmark available*

---

## Task 3 – AIM Path Planning

- **Input**: `main_aims`  
- **Output**: `aim_path` – graph-ordered list of prerequisite AIMs  
- **Objective**: Plan a structured learning path from prerequisites to main AIMs  
- **Metric**:
  - Jaccard similarity (AIM set)
  - Sequence alignment (optional)
- **Status**: *Benchmark available*

---

## Task 4 – Lesson Generation (Conceptual)

- **Input**: `aim_path`  
- **Output**: `lesson_plan` – list of instructional content blocks  
- **Objective**: Generate a personalized sequence of lessons mapped to each AIM  
- **Metric**: BLEU / ROUGE / rubric-based qualitative analysis  
- **Status**: Conceptual (future work)

---

## Task 5 – Adaptive Progress Tracking (Conceptual)

- **Input**: `student_log`, `aim_history`  
- **Output**: `next_aim_recommendation`, `feedback_summary`  
- **Objective**: Track learner progress and adaptively suggest new AIMs  
- **Metric**: Goal retention, rubric match, adaptation quality (qualitative)  
- **Status**: Conceptual (future work)

---

**Note**: Only Task 2 and Task 3 are benchmarked with data and code.  
The remaining tasks are part of the full AIM2Lang reasoning pipeline (see `architecture.md`).