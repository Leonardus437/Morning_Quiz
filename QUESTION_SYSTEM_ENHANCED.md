# Enhanced Question Management System

## 🎯 Overview
Comprehensive question preparation system with support for ALL question types and H5P interactive content.

## 📝 Supported Question Types

### 1. Multiple Choice Questions (MCQ)
- 2-10 options per question
- Single correct answer
- Automatic grading
- Visual feedback

### 2. True/False
- Binary choice questions
- Quick assessment
- Instant feedback

### 3. Short Answer
- Text-based responses
- Keyword matching
- Case-insensitive grading

### 4. Fill in the Blanks
- Multiple blanks per question
- Exact match or keyword matching
- Partial credit support

### 5. Matching Pairs
- Match items from two columns
- Drag-and-drop interface
- Multiple pairs per question

### 6. Ordering/Sequencing
- Arrange items in correct order
- Step-by-step processes
- Timeline questions

### 7. Essay Questions
- Long-form responses
- Manual grading with rubrics
- Rich text support

### 8. H5P Interactive Content
- Import from LUMI editor
- Interactive videos
- Interactive presentations
- Drag-and-drop activities
- Fill in the blanks (H5P)
- Multiple choice (H5P)
- Question sets

## 📤 Upload Formats Supported

### 1. Excel (.xlsx, .xls)
**Format:**
```
| Question | Type | Options | Answer | Points |
|----------|------|---------|--------|--------|
| What is Python? | MCQ | Programming Language|Database|OS | Programming Language | 1 |
| HTML is markup | True/False | | True | 1 |
```

**Template columns:**
- Question: Question text
- Type: MCQ, True/False, Short Answer, Fill Blanks, Matching, Ordering, Essay
- Options: Pipe-separated (|) for MCQ
- Answer: Correct answer
- Points: Score value

### 2. PDF (.pdf)
**Format:**
```
1. What is Object-Oriented Programming?
   a) A programming paradigm
   b) A database
   c) A network protocol
   Answer: a

2. Python is a compiled language.
   True/False
   Answer: False
```

### 3. Word Documents (.doc, .docx)
Same format as PDF with proper formatting

### 4. H5P Files (.h5p)
- Created via LUMI H5P editor (https://lumi.education)
- Supports all H5P content types
- Automatic question extraction
- Preserves interactivity

### 5. JSON (.json)
```json
[
  {
    "question_text": "What is OOP?",
    "type": "mcq",
    "options": ["Paradigm", "Database", "Protocol"],
    "correct_answer": "Paradigm",
    "points": 1
  }
]
```

## 🚀 How to Use

### Creating Questions Manually

1. **Navigate to Question Bank**
   - Go to Teacher Dashboard
   - Click "Question Bank" or visit `/teacher/questions`

2. **Click "Create Question"**
   - Select question type
   - Enter question text
   - Add options (for MCQ, Matching, etc.)
   - Set correct answer
   - Assign points
   - Select department, level, and lesson

3. **Save Question**
   - Questions are immediately available for quiz creation

### Uploading Questions in Bulk

1. **Prepare Your File**
   - Download template (Excel or JSON)
   - Fill in questions following format
   - Save file

2. **Upload Process**
   - Click "Upload Questions"
   - Select file format
   - Choose file
   - Select department and level
   - Select lesson
   - Click "Upload"

3. **Review Results**
   - System shows number of imported questions
   - Any errors are displayed
   - Questions appear in question bank

### Using H5P Content

1. **Create H5P Content**
   - Visit https://lumi.education
   - Download LUMI H5P editor
   - Create interactive content:
     - Question Set
     - Interactive Video with questions
     - Fill in the Blanks
     - Drag and Drop
     - Multiple Choice

2. **Export from LUMI**
   - Save as .h5p file
   - File contains all questions and interactivity

3. **Upload to Quiz System**
   - Select "H5P Interactive" format
   - Upload .h5p file
   - System extracts all questions
   - Maintains interactivity where possible

## 📋 Question Format Examples

### MCQ Example
```
Question: What is the capital of Rwanda?
Type: MCQ
Options:
  A. Kigali
  B. Nairobi
  C. Kampala
  D. Dar es Salaam
Correct Answer: Kigali
Points: 1
```

### Fill in the Blanks Example
```
Question: Python is a _____ programming language that emphasizes _____.
Blanks: ["high-level", "readability"]
Points: 2
```

### Matching Example
```
Question: Match programming languages with their types
Pairs:
  - Python: Interpreted
  - C++: Compiled
  - Java: Bytecode
  - JavaScript: Interpreted
Points: 4
```

### Ordering Example
```
Question: Arrange software development phases in order
Items:
  1. Requirements Analysis
  2. Design
  3. Implementation
  4. Testing
  5. Deployment
Points: 5
```

## 🎨 Best Practices

### Question Writing
1. **Be Clear and Concise**
   - Use simple language
   - Avoid ambiguity
   - One concept per question

2. **Appropriate Difficulty**
   - Match to student level
   - Progressive difficulty
   - Mix question types

3. **Quality Options (MCQ)**
   - All options plausible
   - Avoid "all of the above"
   - Similar length options

4. **Fair Grading**
   - Clear correct answers
   - Appropriate point values
   - Consistent difficulty-to-points ratio

### File Upload Tips
1. **Excel Files**
   - Use provided template
   - Check for special characters
   - Verify pipe separators in options

2. **PDF/Word Files**
   - Clear numbering
   - Consistent formatting
   - Proper answer indication

3. **H5P Files**
   - Test in LUMI first
   - Ensure all questions have answers
   - Check file size (max 50MB)

## 🔧 Technical Details

### Supported File Extensions
- Excel: .xlsx, .xls
- PDF: .pdf
- Word: .doc, .docx
- Text: .txt
- H5P: .h5p
- JSON: .json

### File Size Limits
- Excel/Word/PDF: 10MB
- H5P: 50MB
- JSON: 5MB

### Question Limits
- Per upload: 500 questions
- Per quiz: 100 questions
- Per lesson: Unlimited

### H5P Content Types Supported
- H5P.QuestionSet
- H5P.MultiChoice
- H5P.TrueFalse
- H5P.FillInTheBlanks
- H5P.DragQuestion
- H5P.InteractiveVideo
- H5P.CoursePresentation

## 📊 Question Bank Features

### Organization
- Filter by department
- Filter by level
- Filter by lesson
- Filter by question type
- Search by keyword

### Management
- Edit questions
- Delete questions
- Duplicate questions
- Bulk operations
- Export questions

### Analytics
- Usage statistics
- Difficulty analysis
- Performance metrics
- Student feedback

## 🎓 For Teachers

### Quick Start
1. Download Excel template
2. Fill in 10-20 questions
3. Upload to system
4. Create quiz using uploaded questions
5. Schedule and broadcast

### Advanced Usage
1. Create H5P interactive content
2. Mix question types in quizzes
3. Use question randomization
4. Set time limits per question
5. Enable partial credit

### Tips
- Start with MCQ for quick setup
- Add variety with different types
- Use H5P for engagement
- Regular question bank updates
- Review student performance data

## 🔐 Security & Privacy

- Questions encrypted at rest
- Access control by teacher
- Audit logs for changes
- Backup before bulk operations
- Version control for edits

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review error messages
3. Contact system administrator
4. Submit feedback via teacher panel

## 🚀 Future Enhancements

- AI-powered question generation
- Automatic difficulty assessment
- Question bank sharing between teachers
- Advanced analytics dashboard
- Mobile app for question creation
- Voice-to-text question input
- Image-based questions
- Video questions
- Collaborative question editing
