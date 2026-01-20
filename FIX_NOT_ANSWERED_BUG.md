# BUG FIX: "Not Answered" Showing for All Questions

## Problem
Students see "Not answered" for ALL questions even when they provided answers.

## Root Cause
In `backend/main.py` line 485-486, when checking for empty answers:
```python
if not user_answer or not str(user_answer).strip():
    points_earned = 0
    feedback = "No answer provided"
```

The code sets the feedback but **NEVER adds it to grading_details**. It just continues to the next section, which then processes the answer as if it exists, but the `user_answer` variable is empty/None.

## The Fix
The empty answer check needs to append to grading_details and continue to next question:

```python
if not user_answer or not str(user_answer).strip():
    points_earned = 0
    feedback = "No answer provided"
    grading_details.append({
        "question_id": question.id,
        "points_earned": 0.0,
        "max_points": int(question.points or 1),
        "feedback": feedback
    })
    continue  # Skip to next question
```

## Location
File: `backend/main.py`
Line: ~485-487
Function: `submit_quiz()`
