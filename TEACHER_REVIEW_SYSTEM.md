# 📚 TEACHER REVIEW SYSTEM - COMPLETE WORKFLOW

## 🎯 OVERVIEW

This system allows teachers to:
1. ✅ Receive notifications when students submit quizzes
2. ✅ Review all student submissions (including cheaters)
3. ✅ Adjust scores and provide feedback
4. ✅ Release results when ready
5. ✅ Students can download reports ONLY after release

---

## 🔄 COMPLETE WORKFLOW

### STEP 1: Student Submits Quiz
**What Happens:**
- Student completes quiz (even if they cheated)
- Quiz is auto-submitted
- Initial score is calculated
- **Teacher receives notification**: "📝 New Quiz Submission: [Quiz Title]"

**Backend Endpoint:** `POST /quizzes/submit`
```json
{
  "quiz_id": 1,
  "answers": [
    {"question_id": 1, "answer": "Paris"},
    {"question_id": 2, "answer": "Blue"}
  ]
}
```

**Response:**
```json
{
  "score": 8.5,
  "total": 10,
  "needs_review": false
}
```

**Notification Created:**
- Title: "📝 New Quiz Submission: Geography Quiz"
- Message: "John Doe has submitted the quiz. Score: 8.5/10. Click to review."
- Type: "quiz_submission"

---

### STEP 2: Teacher Views Submissions
**What Teacher Sees:**
- List of all students who submitted
- Initial scores
- Review status (reviewed/not reviewed)
- Submission time

**Backend Endpoint:** `GET /teacher/quiz-submissions/{quiz_id}`

**Response:**
```json
{
  "quiz_id": 1,
  "quiz_title": "Geography Quiz",
  "results_released": false,
  "submissions": [
    {
      "attempt_id": 101,
      "student_id": 50,
      "student_name": "John Doe",
      "username": "student001",
      "score": 8.5,
      "total": 10,
      "percentage": 85.0,
      "needs_review": false,
      "reviewed": false,
      "completed_at": "2026-01-22T20:30:00"
    },
    {
      "attempt_id": 102,
      "student_name": "Jane Smith",
      "score": 6.0,
      "total": 10,
      "percentage": 60.0,
      "needs_review": true,
      "reviewed": false,
      "completed_at": "2026-01-22T20:28:00"
    }
  ]
}
```

---

### STEP 3: Teacher Reviews Individual Submission
**What Teacher Sees:**
- All questions and student answers
- Correct answers
- Initial AI grading
- Option to adjust score and add feedback

**Backend Endpoint:** `GET /teacher/review-submission/{attempt_id}`

**Response:**
```json
{
  "attempt_id": 101,
  "quiz_title": "Geography Quiz",
  "student_name": "John Doe",
  "student_username": "student001",
  "initial_score": 8.5,
  "final_score": null,
  "total_questions": 10,
  "completed_at": "2026-01-22T20:30:00",
  "answers": [
    {
      "answer_id": 1001,
      "question_id": 1,
      "question_text": "What is the capital of France?",
      "question_type": "multiple_choice",
      "correct_answer": "Paris",
      "max_points": 1,
      "student_answer": "Paris",
      "is_correct": true,
      "points_earned": 1.0,
      "ai_feedback": "Correct",
      "teacher_score": null,
      "teacher_feedback": null
    },
    {
      "answer_id": 1002,
      "question_id": 2,
      "question_text": "Explain photosynthesis",
      "question_type": "essay",
      "correct_answer": "Process where plants convert light to energy",
      "max_points": 5,
      "student_answer": "Plants use sunlight to make food",
      "is_correct": false,
      "points_earned": 3.0,
      "ai_feedback": "Partially correct",
      "teacher_score": null,
      "teacher_feedback": null
    }
  ]
}
```

---

### STEP 4: Teacher Grades Individual Answer
**What Teacher Does:**
- Adjusts score for specific answer
- Adds personalized feedback
- System recalculates final score

**Backend Endpoint:** `POST /teacher/grade-answer/{answer_id}`

**Request:**
```json
{
  "score": 4.5,
  "feedback": "Good explanation but missing key details about chlorophyll"
}
```

**Response:**
```json
{
  "message": "Answer graded successfully",
  "final_score": 9.5
}
```

**What Happens:**
- `teacher_score` = 4.5 (overrides AI score of 3.0)
- `teacher_feedback` = "Good explanation..."
- Final score recalculated: 1.0 + 4.5 + ... = 9.5
- `attempt.final_score` = 9.5

---

### STEP 5: Teacher Releases Results
**What Teacher Does:**
- Reviews all submissions
- Clicks "Release Results" button
- All students get notified

**Backend Endpoint:** `POST /teacher/release-results/{quiz_id}`

**Response:**
```json
{
  "message": "Results released successfully",
  "students_notified": 25
}
```

**What Happens:**
- `quiz.results_released` = true
- Notification sent to ALL students:
  - Title: "✅ Results Released: Geography Quiz"
  - Message: "Your quiz results are now available. Score: 9.5/10. Download your report now!"
  - Type: "results_released"

---

### STEP 6: Student Downloads Report
**What Student Does:**
- Receives notification
- Clicks "Download Report"
- Gets PDF with detailed results

**Backend Endpoint:** `GET /student-report/{quiz_id}`

**Authorization Check:**
```python
if not quiz.results_released:
    raise HTTPException(
        status_code=403,
        detail="Results not yet released by teacher. Please wait for teacher to review and release results."
    )
```

**PDF Report Includes:**
- Student name, department, level
- Final score (teacher-reviewed if available)
- Percentage and grade
- All questions with:
  - Student's answer
  - Correct answer
  - Points earned (teacher score if available)
  - Feedback (teacher feedback if available)

---

## 🎓 SPECIAL CASE: CHEATING STUDENTS

### Scenario: Student Cheats and Gets Terminated

**What Happens:**
1. Student triggers 3 violations
2. Quiz auto-submits with whatever they answered
3. **TWO notifications sent to teacher:**
   - ⚠️ "Cheating Alert: [Quiz Title]" - Student caught cheating
   - 📝 "New Quiz Submission: [Quiz Title]" - Quiz was submitted

4. Teacher can still review the submission
5. Teacher can adjust score based on what student actually answered correctly
6. Teacher releases results
7. Student gets their score (even though they cheated)

**Example:**
- Student answers 5/10 questions correctly before cheating
- Initial score: 5/10
- Teacher reviews: "Student cheated but answered 5 correctly"
- Teacher keeps score at 5/10 or adjusts as needed
- Teacher releases results
- Student downloads report showing 5/10 with note about cheating

---

## 📊 API ENDPOINTS SUMMARY

### Teacher Endpoints:
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/teacher/quiz-submissions/{quiz_id}` | GET | View all submissions for a quiz |
| `/teacher/review-submission/{attempt_id}` | GET | View detailed submission |
| `/teacher/grade-answer/{answer_id}` | POST | Grade individual answer |
| `/teacher/release-results/{quiz_id}` | POST | Release results to students |

### Student Endpoints:
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/student-report/{quiz_id}` | GET | Download PDF report (only if released) |
| `/student/progress` | GET | View progress (only released quizzes) |

### Notification Endpoints:
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/notifications` | GET | Get all notifications for current user |

---

## 🔔 NOTIFICATION TYPES

### For Teachers:
1. **quiz_submission** - Student submitted quiz
   - Title: "📝 New Quiz Submission: [Quiz Title]"
   - Message: "[Student Name] has submitted the quiz. Score: X/Y. Click to review."

2. **cheating_alert** - Student caught cheating
   - Title: "⚠️ Cheating Alert: [Quiz Title]"
   - Message: "[Student Name] was caught attempting to cheat (3 violations). Reason: [Reason]. Quiz was auto-submitted."

### For Students:
1. **quiz_available** - New quiz broadcasted
   - Title: "New Quiz Available: [Quiz Title]"
   - Message: "A new quiz '[Quiz Title]' is now available. Duration: X minutes. Start now!"

2. **results_released** - Results are ready
   - Title: "✅ Results Released: [Quiz Title]"
   - Message: "Your quiz results are now available. Score: X/Y. Download your report now!"

---

## 🎯 KEY FEATURES

### 1. Score Calculation Priority:
```python
# Display score logic:
display_score = attempt.final_score if attempt.final_score is not None else attempt.score

# If teacher reviewed: use final_score
# If not reviewed: use initial score
```

### 2. Results Release Control:
```python
# Students can only see results if:
if quiz.results_released:
    # Show score, allow download
else:
    # Hide score, block download
```

### 3. Automatic Notifications:
- Quiz submission → Teacher notified
- Cheating detected → Teacher notified
- Results released → All students notified

### 4. Fair Grading for Cheaters:
- Cheaters still get credit for correct answers
- Teacher can review and adjust
- System doesn't automatically fail cheaters
- Teacher has final say on score

---

## 🚀 TESTING WORKFLOW

### Test 1: Normal Submission
1. Student completes quiz normally
2. Check teacher receives "📝 New Quiz Submission" notification
3. Teacher reviews submission
4. Teacher releases results
5. Check student receives "✅ Results Released" notification
6. Student downloads report

### Test 2: Cheating Submission
1. Student triggers 3 violations
2. Quiz auto-submits
3. Check teacher receives TWO notifications:
   - "⚠️ Cheating Alert"
   - "📝 New Quiz Submission"
4. Teacher reviews submission (can see answers)
5. Teacher adjusts score if needed
6. Teacher releases results
7. Student downloads report

### Test 3: Teacher Grading
1. Teacher views submission
2. Teacher adjusts score for essay question
3. Check final_score is recalculated
4. Release results
5. Student report shows teacher's score and feedback

---

## ✅ SUCCESS CRITERIA

- [x] Teacher receives notification on every quiz submission
- [x] Teacher can view all submissions (including cheaters)
- [x] Teacher can adjust individual answer scores
- [x] Teacher can add personalized feedback
- [x] Final score recalculates automatically
- [x] Results are hidden until teacher releases
- [x] Students get notified when results are released
- [x] Students can download PDF report after release
- [x] Cheaters get fair grading for correct answers

---

**System Status:** ✅ FULLY IMPLEMENTED  
**Backend Version:** 2.0-ANTI-CHEAT  
**Date:** January 22, 2026
