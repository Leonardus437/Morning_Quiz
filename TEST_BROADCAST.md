# Test Broadcast Fix

## Current Status
- Quiz ID 1 is created with `Computer System and Architecture - Level 3`
- Students exist with matching `Computer System and Architecture - Level 3`
- Quiz is currently `is_active = false`

## The Problem
The broadcast endpoint (`PUT /quizzes/{quiz_id}/broadcast`) is not being called or is not updating the database.

## Solution Applied
1. Enhanced the broadcast endpoint with better logging and database flushing
2. Added explicit `db.flush()` after setting `is_active = True`
3. Added verification after commit

## How to Test

### Step 1: Verify Quiz is Inactive
```bash
docker exec tvet_quiz-db-1 psql -U quiz_user -d morning_quiz -c "SELECT id, title, is_active FROM quizzes WHERE id = 1;"
```
Expected: `is_active = f` (false)

### Step 2: Get Teacher Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"teacher001","password":"teacher123"}'
```
Copy the `access_token` from response

### Step 3: Call Broadcast Endpoint
```bash
curl -X PUT http://localhost:8000/quizzes/1/broadcast \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Step 4: Check Backend Logs
```bash
docker-compose logs backend --tail=20
```
Look for:
- `🎯 BROADCASTING QUIZ 1`
- `Found X students to notify`
- `✅ Quiz 1 is now ACTIVE and BROADCASTING`

### Step 5: Verify Quiz is Active
```bash
docker exec tvet_quiz-db-1 psql -U quiz_user -d morning_quiz -c "SELECT id, title, is_active FROM quizzes WHERE id = 1;"
```
Expected: `is_active = t` (true)

### Step 6: Verify Student Can See Quiz
Get student token:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"agasaro1","password":"student123"}'
```

Get quizzes for student:
```bash
curl -X GET http://localhost:8000/quizzes \
  -H "Authorization: Bearer STUDENT_TOKEN_HERE"
```

Expected: Quiz 1 should appear in the response

## If It Still Doesn't Work

### Check 1: Verify Students Exist
```bash
docker exec tvet_quiz-db-1 psql -U quiz_user -d morning_quiz -c "SELECT id, username, department, level FROM users WHERE role='student' LIMIT 5;"
```

### Check 2: Verify Department/Level Match
```bash
docker exec tvet_quiz-db-1 psql -U quiz_user -d morning_quiz -c "SELECT id, title, department, level FROM quizzes WHERE id = 1;"
```

### Check 3: Check Backend Logs for Errors
```bash
docker-compose logs backend --tail=50 | grep -i "error\|broadcast"
```

### Check 4: Restart Backend
```bash
docker-compose restart backend
```

## Expected Flow

1. Teacher clicks "📡 Broadcast Now" button
2. Frontend calls `PUT /quizzes/1/broadcast` with teacher token
3. Backend:
   - Finds quiz with ID 1
   - Sets `is_active = True`
   - Flushes to database
   - Finds all students with matching dept/level
   - Creates notifications for each student
   - Commits changes
4. Frontend receives response with `students_notified` count
5. Teacher sees alert: "Quiz broadcasted to all students immediately! Students notified: X"
6. Students refresh their dashboard
7. Students see quiz in "AVAILABLE QUIZZES" section
8. Students can click and start quiz

## Success Indicators

✅ Quiz `is_active` changes from `false` to `true`
✅ Backend logs show broadcast confirmation
✅ Students receive notifications
✅ Students see quiz in their dashboard
✅ Students can access and start quiz
