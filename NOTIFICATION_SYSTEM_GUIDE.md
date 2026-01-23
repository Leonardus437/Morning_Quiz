# 🔔 Notification System Guide

## Overview

The system now distinguishes between **manual quiz submissions** and **auto-submissions due to cheating**. Teachers receive different notifications based on how the quiz was submitted.

---

## 📝 Notification Types

### 1. Manual Submission (Student Clicks "Submit")

**What Teacher Sees**:
```
📝 New Quiz Submission: Geography Quiz
Student One has submitted the quiz. Score: 8/10. Click to review.
```

**When This Happens**:
- Student completes quiz normally
- Student clicks "Submit" button
- No cheating violations detected

---

### 2. Auto-Submission (Cheating Detected)

**What Teacher Sees** (TWO notifications):

**Notification 1 - Cheating Alert**:
```
⚠️ Cheating Alert: Geography Quiz
Student One was caught attempting to cheat (3 violations). 
Reason: You switched to another tab. 
Quiz was auto-submitted.
```

**Notification 2 - Auto-Submission Notice**:
```
📝 Auto-Submitted Quiz: Geography Quiz
Student One's quiz was automatically submitted due to cheating violations (3 strikes). 
Reason: You switched to another tab. 
Score: 5/10. 
Click to review.
```

**When This Happens**:
- Student triggers 3 violations (tab switch, F12, ESC, etc.)
- System automatically submits quiz
- System reports to teacher with reason

---

## 🎯 How to Identify Submissions

### In Teacher Dashboard Notifications:

| Notification Title | Meaning | Action |
|-------------------|---------|--------|
| 📝 New Quiz Submission | Normal submission | Review when ready |
| 📝 Auto-Submitted Quiz | Cheating detected | Review immediately |
| ⚠️ Cheating Alert | Violation details | Check student behavior |

### In Review Page:

All submissions appear in the submissions list regardless of how they were submitted. Teachers can:
1. Review all answers
2. Adjust scores fairly
3. Add feedback
4. Release results

---

## 🔍 Common Cheating Reasons

| Reason | What Happened |
|--------|---------------|
| "You switched to another tab" | Student left quiz tab |
| "You switched to another application" | Student clicked outside browser |
| "You pressed a restricted key (F12)" | Student tried to open DevTools |
| "You pressed a restricted key (Escape)" | Student pressed ESC |
| "You tried to open developer tools" | Student pressed Ctrl+Shift+I |
| "You tried to view page source" | Student pressed Ctrl+U |

---

## 👨‍🏫 Teacher Workflow

### When You See "📝 New Quiz Submission":
1. Student submitted normally
2. Review at your convenience
3. Adjust scores if needed
4. Release results when ready

### When You See "⚠️ Cheating Alert" + "📝 Auto-Submitted Quiz":
1. Student was caught cheating
2. Quiz was auto-submitted
3. Review the submission
4. Check what they answered correctly
5. Adjust score fairly (they still get credit for correct answers)
6. Consider discussing with student
7. Release results when ready

---

## 💡 Important Notes

### Fair Grading
- Even if a student cheated, they still get credit for correct answers
- Teachers can adjust scores based on actual performance
- System doesn't automatically fail cheaters
- Teacher has final say on the score

### Privacy
- Only the teacher sees cheating alerts
- Other students don't see who cheated
- Reports show scores but not cheating status

### Review Process
- All submissions can be reviewed the same way
- Cheating doesn't block the review process
- Teachers can add personalized feedback
- Results are only visible after teacher releases them

---

## 🚀 Quick Reference

### Student Submits Normally:
```
Teacher receives: 1 notification
Type: "📝 New Quiz Submission"
Contains: Student name, score, quiz title
```

### Student Cheats (3 violations):
```
Teacher receives: 2 notifications
Type 1: "⚠️ Cheating Alert"
Type 2: "📝 Auto-Submitted Quiz"
Contains: Student name, violation count, reason, score, quiz title
```

---

## 📊 Example Scenarios

### Scenario 1: Honest Student
```
1. Student takes quiz
2. Student answers all questions
3. Student clicks "Submit"
4. Teacher receives: "📝 New Quiz Submission: Math Quiz"
5. Teacher reviews and releases results
```

### Scenario 2: Student Tries to Cheat
```
1. Student takes quiz
2. Student switches tabs (Warning #1)
3. Student presses F12 (Warning #2)
4. Student switches tabs again (Warning #3)
5. System auto-submits quiz
6. Teacher receives:
   - "⚠️ Cheating Alert: Math Quiz"
   - "📝 Auto-Submitted Quiz: Math Quiz"
7. Teacher reviews, adjusts score fairly, releases results
```

---

## ✅ System Benefits

1. **Clear Communication**: Teachers know exactly what happened
2. **Fair Grading**: Cheaters still get credit for correct answers
3. **Transparency**: Reasons are clearly stated
4. **Efficiency**: Auto-submission prevents incomplete quizzes
5. **Accountability**: Students know violations are tracked
6. **Flexibility**: Teachers can adjust scores as needed

---

**Last Updated**: January 22, 2026
**System Version**: 2.0-ANTI-CHEAT
