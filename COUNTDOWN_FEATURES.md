# Quiz Countdown Timer Features

## Implementation Summary

### Backend Changes (main.py)
1. **Enhanced Quiz Model**: Already has `question_time_seconds` and `countdown_started_at` fields
2. **Broadcast Quiz**: Now starts countdown immediately when teacher broadcasts
3. **Quiz Questions Endpoint**: Checks if quiz time has expired and shows appropriate messages
4. **Quiz List Endpoint**: Adds timing information for students

### Frontend Changes

#### Teacher Interface (teacher/+page.svelte)
1. **Quiz Creation**: Added "Time per Question" field (30-300 seconds)
2. **Quiz Display**: Shows per-question timing in quiz list
3. **Broadcast**: Enhanced messaging for countdown start

#### Student Interface (+page.svelte)
1. **Quiz Cards**: Show per-question timing and countdown status
2. **Real-time Updates**: Display remaining time with color coding
3. **Status Messages**: "Hurry Up!" and "Quiz Time Over" alerts

#### Quiz Taking Interface (quiz/[id]/+page.svelte)
1. **Dual Timers**: Total quiz time + per-question time
2. **Auto-submission**: Questions auto-submit when time expires
3. **No Going Back**: Can't return to expired questions
4. **Visual Indicators**: Color-coded timers and completion status

## Key Features

### 1. Countdown Start on Broadcast
- When teacher clicks "Broadcast Now", countdown starts immediately
- `countdown_started_at` timestamp is set to current time
- All students get notification with timing info

### 2. Per-Question Timing
- Teachers set time per question (default 60 seconds)
- Each question has its own countdown timer
- Auto-submission when question time expires
- Visual feedback for expired questions

### 3. Late Student Handling
- Students joining late see "Time is going up, hurry up!" message
- If quiz time is over, shows "Quiz time is over!" message
- Real-time countdown on student dashboard

### 4. Auto-submission Logic
- Questions auto-submit when individual timer expires
- Students cannot go back to expired questions
- Empty answers are submitted if no response given
- Quiz auto-submits when total time expires

### 5. Visual Feedback
- Red pulsing timers when time is low
- Disabled inputs for expired questions
- Color-coded question navigation buttons
- Status indicators for completed/expired questions

## Usage Instructions

### For Teachers:
1. Create quiz with desired "Time per Question" setting
2. Click "Broadcast Now" to start countdown immediately
3. Students will see real-time countdown and timing warnings

### For Students:
1. Join quiz as soon as notification appears
2. Answer questions within the time limit
3. Questions auto-submit when time expires
4. Cannot return to expired questions

## Technical Details

### Timer Synchronization
- Server-side countdown using `countdown_started_at` timestamp
- Client-side timers sync with server time
- Prevents client-side manipulation

### Database Fields Used
- `Quiz.question_time_seconds`: Time allowed per question
- `Quiz.countdown_started_at`: When countdown started
- `Quiz.duration_minutes`: Total quiz duration

### Error Handling
- Graceful handling of expired quizzes
- Clear error messages for timing issues
- Automatic cleanup of expired quiz states