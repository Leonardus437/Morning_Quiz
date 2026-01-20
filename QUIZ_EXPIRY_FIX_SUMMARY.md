# Quiz Expiry Fix - Summary

## Problem
Students were getting an unfriendly HTTP 400 error when trying to start an expired quiz:
- Error: "Quiz time is over! The quiz has ended."
- No way for teachers to easily restart/rebroadcast expired quizzes

## Solution Implemented

### 1. Friendly Student Message ✅
**Changed:** `backend/main.py` line ~961

**Before:**
```python
raise HTTPException(status_code=400, detail="Quiz time is over! The quiz has ended.")
```

**After:**
```python
minutes_ago = int((elapsed_time - total_quiz_time) / 60)
raise HTTPException(
    status_code=410,  # 410 Gone - resource expired
    detail=f"⏰ Time's Up! Quiz '{quiz.title}' ended {minutes_ago} minutes ago. Please wait for your teacher to start a new session."
)
```

**Benefits:**
- HTTP 410 (Gone) instead of 400 (Bad Request) - semantically correct
- Friendly, informative message
- Tells students exactly how long ago the quiz ended
- Instructs students to wait for teacher

### 2. Quiz Status Endpoint for Teachers ✅
**Added:** New endpoint at `backend/main.py` line ~1176

```python
@app.get("/quizzes/{quiz_id}/status")
def get_quiz_status(quiz_id: int, ...):
    """Get quiz status including expiry information"""
```

**Returns:**
```json
{
  "quiz_id": 7,
  "title": "fghjkl",
  "is_active": true,
  "is_expired": true,
  "duration_minutes": 2,
  "time_remaining_seconds": 0,
  "elapsed_minutes": 25,
  "countdown_started_at": "2025-11-25T20:05:19",
  "can_rebroadcast": true,
  "department": "Computer System and Architecture",
  "level": "Level 3"
}
```

**Benefits:**
- Teachers can check if quiz has expired
- Frontend can show "Rebroadcast" button when `can_rebroadcast: true`
- Shows elapsed time and remaining time
- No authentication errors for teachers

### 3. Rebroadcast Feature (Already Working) ✅
Teachers can simply click "Broadcast" again on an expired quiz to restart it:
- Resets the countdown timer
- Sends new notifications to all students
- Students can then start the quiz fresh

## Frontend Integration Needed

The frontend should:

1. **For Students:**
   - Catch HTTP 410 errors
   - Display the friendly message from `detail` field
   - Show a nice UI instead of generic error page

2. **For Teachers:**
   - Call `/quizzes/{quiz_id}/status` endpoint periodically
   - Show "⏰ Expired - Rebroadcast" button when `is_expired: true`
   - Show time remaining when quiz is active
   - Make rebroadcast button prominent and easy to click

## Testing

### Test Expired Quiz Message:
```bash
# As a student trying to access expired quiz 7
curl http://localhost:8000/quizzes/7/questions
# Should return HTTP 410 with friendly message
```

### Test Quiz Status:
```bash
# As a teacher checking quiz status
curl -H "Authorization: Bearer <token>" http://localhost:8000/quizzes/7/status
# Should return quiz status with is_expired: true
```

### Test Rebroadcast:
```bash
# As a teacher rebroadcasting quiz 7
curl -X PUT -H "Authorization: Bearer <token>" http://localhost:8000/quizzes/7/broadcast
# Should restart the quiz and notify 97 students
```

## Files Modified
- `backend/main.py` - Updated get_quiz_questions function (line ~961)
- `backend/main.py` - Added get_quiz_status endpoint (line ~1176)

## Status
✅ Backend changes applied and deployed
✅ Backend container rebuilt and restarted
⏳ Frontend integration pending (to show friendly UI and rebroadcast button)

## Next Steps for Frontend Developer
1. Update student quiz page to handle HTTP 410 gracefully
2. Add quiz status polling for teacher dashboard
3. Show "Rebroadcast Quiz" button when quiz expires
4. Add countdown timer display for active quizzes
