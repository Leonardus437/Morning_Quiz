# 🚀 Advanced Question Types - Beyond Google Forms

## Current Status: ❌ BASIC (Only 4 types)
## Target Status: ✅ ADVANCED (20+ types)

---

## 📊 COMPARISON: Google Forms vs Our System

### Google Forms Has (9 types):
1. ✅ Multiple Choice
2. ✅ Checkboxes (Multiple Select)
3. ✅ Short Answer
4. ✅ Paragraph (Essay)
5. ❌ Dropdown
6. ❌ Linear Scale (1-5, 1-10)
7. ❌ Multiple Choice Grid
8. ❌ Checkbox Grid
9. ❌ Date/Time

### Our System Will Have (25+ types):

#### **BASIC TYPES** (Already Implemented)
1. ✅ Multiple Choice (Single Select)
2. ✅ True/False
3. ✅ Short Answer
4. ✅ Essay/Paragraph

#### **GOOGLE FORMS TYPES** (To Add)
5. ⚡ Checkboxes (Multiple Select)
6. ⚡ Dropdown Select
7. ⚡ Linear Scale (Rating 1-10)
8. ⚡ Multiple Choice Grid
9. ⚡ Checkbox Grid
10. ⚡ Date Picker
11. ⚡ Time Picker

#### **ADVANCED TYPES** (Beyond Google Forms)
12. ⚡ Fill in the Blanks (Multiple blanks in one question)
13. ⚡ Drag and Drop (Match items)
14. ⚡ Drag and Drop Ordering (Sequence)
15. ⚡ Image-Based MCQ (Click on image areas)
16. ⚡ Image Hotspot (Mark specific areas)
17. ⚡ Audio Question (Listen and answer)
18. ⚡ Video Question (Watch and answer)
19. ⚡ Code Writing (With syntax highlighting)
20. ⚡ Code Output Prediction
21. ⚡ SQL Query Writing
22. ⚡ Matching Pairs
23. ⚡ Sorting/Ranking
24. ⚡ Matrix/Table Selection
25. ⚡ File Upload (Student submits file)

#### **TVET/TECHNICAL EDUCATION SPECIFIC**
26. ⚡ Circuit Diagram (Electronics)
27. ⚡ Math Equation Editor
28. ⚡ Drawing Canvas (Technical drawings)
29. ⚡ Flowchart Builder
30. ⚡ Network Diagram

---

## 🎯 IMPLEMENTATION PRIORITY

### Phase 1: Essential (Week 1) ⚡
- Multiple Select (Checkboxes)
- Fill in the Blanks
- Dropdown Select
- Matching Pairs
- Drag and Drop Ordering

### Phase 2: Advanced (Week 2) ⚡
- Image-Based Questions
- Code Writing (Python, Java, C++)
- SQL Query Writing
- Linear Scale
- Grid Questions

### Phase 3: Multimedia (Week 3) ⚡
- Audio Questions
- Video Questions
- File Upload
- Drawing Canvas

### Phase 4: Technical (Week 4) ⚡
- Circuit Diagrams
- Math Equations
- Flowcharts
- Network Diagrams

---

## 📝 DETAILED SPECIFICATIONS

### 1. Multiple Select (Checkboxes)
```json
{
  "question_type": "multiple_select",
  "question_text": "Select all programming languages you know:",
  "options": ["Python", "Java", "C++", "JavaScript", "Ruby"],
  "correct_answers": ["Python", "Java", "C++"],
  "points": 3,
  "partial_credit": true
}
```

### 2. Fill in the Blanks
```json
{
  "question_type": "fill_blanks",
  "question_text": "Python was created by ____ in the year ____.",
  "blanks": [
    {"position": 1, "correct_answer": "Guido van Rossum", "case_sensitive": false},
    {"position": 2, "correct_answer": "1991", "case_sensitive": false}
  ],
  "points": 2
}
```

### 3. Drag and Drop (Matching)
```json
{
  "question_type": "drag_drop_match",
  "question_text": "Match the programming language to its creator:",
  "pairs": [
    {"left": "Python", "right": "Guido van Rossum"},
    {"left": "Java", "right": "James Gosling"},
    {"left": "C++", "right": "Bjarne Stroustrup"}
  ],
  "points": 3
}
```

### 4. Drag and Drop Ordering
```json
{
  "question_type": "drag_drop_order",
  "question_text": "Arrange the SDLC phases in correct order:",
  "items": ["Requirements", "Design", "Implementation", "Testing", "Deployment"],
  "correct_order": [0, 1, 2, 3, 4],
  "points": 5
}
```

### 5. Code Writing
```json
{
  "question_type": "code_writing",
  "question_text": "Write a Python function to calculate factorial:",
  "language": "python",
  "starter_code": "def factorial(n):\n    # Your code here\n    pass",
  "test_cases": [
    {"input": "5", "expected_output": "120"},
    {"input": "0", "expected_output": "1"}
  ],
  "points": 10
}
```

### 6. Image-Based MCQ
```json
{
  "question_type": "image_mcq",
  "question_text": "Identify the component marked as 'A' in the circuit:",
  "image_url": "/uploads/circuit_diagram.png",
  "options": ["Resistor", "Capacitor", "Transistor", "Diode"],
  "correct_answer": "Transistor",
  "points": 2
}
```

### 7. SQL Query Writing
```json
{
  "question_type": "sql_query",
  "question_text": "Write a query to select all students with GPA > 3.5:",
  "database_schema": "students(id, name, gpa, department)",
  "correct_query": "SELECT * FROM students WHERE gpa > 3.5",
  "points": 5
}
```

### 8. Linear Scale
```json
{
  "question_type": "linear_scale",
  "question_text": "Rate your understanding of OOP concepts:",
  "min_value": 1,
  "max_value": 10,
  "min_label": "No understanding",
  "max_label": "Expert level",
  "points": 1
}
```

### 9. Grid Question (Multiple Choice Grid)
```json
{
  "question_type": "mcq_grid",
  "question_text": "Rate your proficiency in each language:",
  "rows": ["Python", "Java", "C++", "JavaScript"],
  "columns": ["Beginner", "Intermediate", "Advanced", "Expert"],
  "correct_answers": {
    "Python": "Advanced",
    "Java": "Intermediate"
  },
  "points": 4
}
```

### 10. File Upload
```json
{
  "question_type": "file_upload",
  "question_text": "Upload your completed project source code (ZIP file):",
  "allowed_extensions": [".zip", ".rar", ".7z"],
  "max_file_size_mb": 50,
  "points": 20,
  "requires_manual_grading": true
}
```

---

## 🔧 DATABASE SCHEMA CHANGES NEEDED

```sql
-- Add new columns to questions table
ALTER TABLE questions ADD COLUMN question_config JSON;
ALTER TABLE questions ADD COLUMN media_url VARCHAR(500);
ALTER TABLE questions ADD COLUMN test_cases JSON;
ALTER TABLE questions ADD COLUMN partial_credit BOOLEAN DEFAULT FALSE;

-- Add new table for file submissions
CREATE TABLE file_submissions (
    id INTEGER PRIMARY KEY,
    attempt_id INTEGER,
    question_id INTEGER,
    file_url VARCHAR(500),
    file_name VARCHAR(255),
    file_size INTEGER,
    uploaded_at DATETIME
);
```

---

## 🎨 FRONTEND COMPONENTS NEEDED

1. **MultipleSelectQuestion.svelte** - Checkboxes
2. **FillBlanksQuestion.svelte** - Input fields in text
3. **DragDropMatch.svelte** - Draggable matching
4. **DragDropOrder.svelte** - Sortable list
5. **CodeEditor.svelte** - Monaco/CodeMirror
6. **ImageQuestion.svelte** - Image with hotspots
7. **GridQuestion.svelte** - Table-based selection
8. **FileUploadQuestion.svelte** - File picker
9. **LinearScaleQuestion.svelte** - Slider/buttons
10. **DrawingCanvas.svelte** - Canvas for drawings

---

## 📦 LIBRARIES NEEDED

### Frontend:
- `@monaco-editor/react` - Code editor
- `react-dnd` or `@dnd-kit/core` - Drag and drop
- `fabric.js` - Drawing canvas
- `katex` - Math equations
- `prism.js` - Code syntax highlighting

### Backend:
- `Pillow` - Image processing
- `code-executor` - Safe code execution
- `sqlparse` - SQL validation

---

## 🚀 NEXT STEPS

1. ✅ Review this document
2. ⚡ Implement Phase 1 (Essential types)
3. ⚡ Update database schema
4. ⚡ Create frontend components
5. ⚡ Add grading logic for each type
6. ⚡ Test with real questions

---

**This system will be THE MOST ADVANCED quiz system for TVET education in Rwanda! 🇷🇼**
