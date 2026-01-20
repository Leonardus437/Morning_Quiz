# Quiz Broadcast Notification Fix

## Problem
When the second quiz is broadcast, students who are already viewing the first quiz don't receive notifications. They only see "Students notified: 0" because students who are already connected don't make new requests to the server.

## Root Cause
The broadcast endpoint only creates notifications in the database but doesn't have a real-time push mechanism. Students viewing the first quiz don't automatically fetch new quizzes unless they:
1. Refresh the page
2. Make a new API request
3. Have a polling mechanism in place

## Solution Implemented

### 1. Enhanced Broadcast Response
Updated `/quizzes/{quiz_id}/broadcast` endpoint to return:
- `quiz_id`: The ID of the broadcasted quiz
- `timestamp`: ISO format timestamp of when the quiz was broadcasted

This allows the frontend to track when quizzes were broadcasted.

### 2. New Polling Endpoint
Added `/quizzes/check-new-broadcasts` endpoint that:
- Returns all active quizzes for the student's department/level
- Returns unread quiz notifications
- Can be called periodically by the frontend (every 5-10 seconds)
- Provides real-time awareness of new quizzes

## Frontend Implementation Required

Add polling to the student dashboard:

```javascript
// Poll for new quizzes every 5 seconds
setInterval(async () => {
  try {
    const response = await fetch('/quizzes/check-new-broadcasts', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    
    if (data.total_new > 0) {
      // Show notification to student
      showNotification(`${data.total_new} new quiz(zes) available!`);
      
      // Refresh quiz list
      refreshQuizList();
    }
  } catch (error) {
    console.error('Error checking for new quizzes:', error);
  }
}, 5000); // Poll every 5 seconds
```

## How It Works

1. **Teacher broadcasts Quiz 2** → Quiz marked as active, notifications created
2. **Student polling endpoint** → Detects new active quiz
3. **Frontend receives response** → Shows notification to student
4. **Student sees new quiz** → Can immediately start Quiz 2

## Benefits

✅ Students viewing Quiz 1 get notified of Quiz 2  
✅ No page refresh needed  
✅ Real-time awareness of new quizzes  
✅ Minimal server load (polling every 5-10 seconds)  
✅ Works with offline-first architecture  

## Alternative: WebSocket Implementation

For even better real-time updates, consider implementing WebSocket:
- Eliminates polling overhead
- Instant notifications
- Better for large numbers of concurrent users
- More complex to implement

## Testing

1. Start Quiz 1 with students viewing it
2. Broadcast Quiz 2
3. Check that students see the new quiz notification
4. Verify "Students notified" count is correct
5. Confirm students can immediately access Quiz 2

## Files Modified

- `backend/main.py`: Added new endpoint and enhanced broadcast response
