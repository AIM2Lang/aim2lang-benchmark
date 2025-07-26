# AIM2Lang System Architecture

This document describes the high-level reasoning pipeline of AIM2Lang.  
The system integrates structured ontology, RAG, and LLM reasoning to map learner goals into atomic instructional paths and personalized content.

---

## Reasoning Pipeline Overview

goal_text
↓
[ Module 1: Goal Analyzer ]
↓
parsed_goal → main_aims
↓
[ Module 2: AIM Planner ]
↓
aim_path (with prerequisite logic)
↓
[ Module 3: Lesson Generator ]
↓
lesson_plan (lesson blocks mapped to AIMs)
↓
[ Module 4: Student Tracker ]
↓
progress_memory → next AIMs → loop


## Module Breakdown

### Module 1: Goal Analyzer
- Input: free-text learning goal
- Output: structured metadata + candidate AIMs
- Uses: LLM + ontology-based filtering

---

### Module 2: AIM Planner
- Input: Main AIMs
- Output: Ordered AIM path (with prerequisites)
- Uses: Ontology (OWL) traversal, graph logic

---

### Module 3: Lesson Generator
- Input: AIM path
- Output: lesson blocks (text + rubric)
- Uses: RAG + LLM + Bloom-aware prompt generation

---

### Module 4: Student Tracker
- Input: AIM memory, quiz log, rubric score
- Output: updated path + feedback summary
- Uses: progress tracking + reasoning loop

---

## Diagram 
[AIM2Lang Pipeline](./architecture_diagram.png)
Note: This architecture describes the reasoning flow.
The AI core (LLM prompts, evaluator logic, ontology traversal, memory update) are kept private in the commercial AIM2Lang engine.

See task_definition.md for formal task descriptions.

---

## Footer 

© 2025 AIM2Lang Contributors.  
Benchmark data, schema, and task definitions are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).  
The full AIM2Lang AI pipeline and reasoning engine remain proprietary and are not included in this public benchmark release.