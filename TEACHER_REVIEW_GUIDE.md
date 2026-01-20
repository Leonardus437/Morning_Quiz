# 📋 TEACHER REVIEW SYSTEM - HOW TO USE

## For Teachers: How to Review Student Quizzes

### Step 1: Access Pending Reviews
**API Endpoint:** `GET /teacher/pending-reviews`

**In the frontend:** Add a "Pending Reviews" button/link in the teacher dashboard that calls this endpoint.

**Response:**
```json
[
  {
    "attempt_id": 123,
    "quiz_title": "Blockchain Quiz",
    "student_name": "John Doe",
    "score": 2.1,
    "submitted_at": "2026-01-19T18:00:00"
  }
]
```

### Step 2: Review Individual Submission
**API Endpoint:** `GET /teacher/review/{attempt_id}`

Click on a pending review to see details:
```json
{
  "attempt_id": 123,
  "quiz_title": "Blockchain Quiz",
  "student_name": "John Doe",
  "total_score": 2.1,
  "answers": [
    {
      "answer_id": 456,
      "question_text": "What is blockchain?",
      "correct_answer": "A distributed ledger",
      "student_answer": "Decentralized platform",
      "ai_score": 0.5,
      "ai_feedback": "Good! Shows understanding",
      "max_points": 1,
      "teacher_score": null,
      "teacher_feedback": null
    }
  ]
}
```

### Step 3: Adjust Grades (if needed)
**API Endpoint:** `POST /teacher/review/{attempt_id}/grade`

**Request Body:**
```json
{
  "grades": [
    {
      "answer_id": 456,
      "score": 0.8,
      "feedback": "Good answer! Added more points for understanding"
    }
  ]
}
```

### Step 4: Release Results
**API Endpoint:** `POST /teacher/quiz/{quiz_id}/release-results`

After reviewing all submissions, release results so students can see them.

---

## For Students: What They See

### After Submitting Quiz:
```
✅ Quiz Submitted Successfully!

Your answers are under review by your teacher.
Results will be available soon.

Quiz: Blockchain Quiz
```

### Before Results Released:
- No scores visible
- "Pending Review" status
- Can't download report

### After Results Released:
- Final scores visible
- Can download PDF report
- See teacher feedback

---

## Quick Frontend Integration

### Add to Teacher Dashboard:
```javascript
// Fetch pending reviews
const response = await fetch('/teacher/pending-reviews');
const pendingReviews = await response.json();

// Show count badge
<button>Pending Reviews ({pendingReviews.length})</button>
```

### Add Review Page:
```javascript
// Get review details
const review = await fetch(`/teacher/review/${attemptId}`);
const data = await review.json();

// Show each answer with AI score
// Allow teacher to adjust
// Submit adjusted grades
await fetch(`/teacher/review/${attemptId}/grade`, {
  method: 'POST',
  body: JSON.stringify({ grades: adjustedGrades })
});

// Release results
await fetch(`/teacher/quiz/${quizId}/release-results`, {
  method: 'POST'
});
```

---

## Current Status

✅ Backend endpoints ready
✅ Student sees "Under Review" message
✅ Results hidden until released
⏳ Frontend UI needs to be added for teacher review workflow

**All API endpoints are working! Just need to add UI buttons/pages in the frontend.**
