# Anti-Cheating System Guide

## Overview
The TVET Quiz System now includes a comprehensive anti-cheating mechanism that prevents students from cheating during quizzes through multiple security layers.

## Security Features

### 1. **Fullscreen Lock Mode**
- Quiz automatically enters fullscreen when started
- Students cannot exit fullscreen without triggering warnings
- System attempts to re-enter fullscreen after exit attempts

### 2. **Tab/Window Switch Detection**
- Detects when students switch to another browser tab
- Detects when students switch to another application (Alt+Tab)
- Monitors window focus and visibility changes

### 3. **Three-Strike Warning System**
- **Warning #1**: First violation - Student receives warning message
- **Warning #2**: Second violation - Final warning with termination threat
- **Warning #3**: Third violation - Quiz auto-submitted + Teacher notified

### 4. **Copy/Paste Prevention**
- Right-click context menu disabled
- Copy (Ctrl+C) blocked
- Cut (Ctrl+X) blocked
- Paste (Ctrl+V) blocked

### 5. **Developer Tools Prevention**
- F12 key blocked
- Ctrl+Shift+I (Inspect) blocked
- Ctrl+Shift+J (Console) blocked
- Ctrl+U (View Source) blocked

### 6. **Teacher Notifications**
- Teachers receive instant notification when student violates rules 3 times
- Notification includes: Student name, quiz title, violation count, reason
- Appears in teacher's notification panel with ⚠️ icon

## How It Works

### For Students

1. **Starting Quiz**
   - Click "Start Quiz" button
   - Browser automatically enters fullscreen mode
   - Anti-cheating protections activate

2. **During Quiz**
   - Stay in fullscreen mode
   - Don't switch tabs or applications
   - Don't try to copy questions or answers
   - Focus only on the quiz

3. **Warning System**
   - **1st Violation**: Yellow warning modal appears
     - "⚠️ WARNING #1: [Reason]. This is your first warning..."
     - Click "I Understand - Continue Quiz" to proceed
   
   - **2nd Violation**: Yellow warning modal appears
     - "⚠️ FINAL WARNING #2: [Reason]. One more violation..."
     - Last chance to complete quiz properly
   
   - **3rd Violation**: Red termination modal appears
     - "❌ QUIZ TERMINATED: [Reason]. Your quiz has been automatically submitted..."
     - Quiz auto-submits after 3 seconds
     - Teacher receives cheating alert notification

4. **Completing Quiz**
   - Submit quiz normally when finished
   - Fullscreen mode exits automatically
   - Anti-cheating protections deactivate

### For Teachers

1. **Monitoring**
   - Check notification panel regularly
   - Look for ⚠️ cheating alert notifications
   - Review flagged student submissions carefully

2. **Cheating Alerts Include**
   - Student name and username
   - Quiz title
   - Number of violations (always 3 when reported)
   - Specific reason (e.g., "switched to another tab")
   - Timestamp of incident

3. **Actions to Take**
   - Review the student's quiz submission
   - Consider the violation severity
   - Adjust grades during manual review if needed
   - Discuss with student if necessary
   - Document repeated offenders

## Violation Types Detected

| Violation | Description | Detection Method |
|-----------|-------------|------------------|
| **Tab Switch** | Student switches to another browser tab | `visibilitychange` event |
| **Window Switch** | Student uses Alt+Tab to switch applications | `blur` event |
| **Fullscreen Exit** | Student presses Esc or exits fullscreen | `fullscreenchange` event |
| **Right Click** | Student tries to open context menu | `contextmenu` event |
| **Copy/Paste** | Student tries to copy or paste content | `copy`/`paste` events |
| **Dev Tools** | Student tries to open browser developer tools | `keydown` event (F12, Ctrl+Shift+I) |

## Technical Implementation

### Frontend (Quiz Page)
```javascript
// Anti-cheating functions activated on quiz start:
- enableAntiCheat()      // Activates all protections
- enterFullscreen()      // Forces fullscreen mode
- preventRightClick()    // Blocks context menu
- preventCopy()          // Blocks copy/cut
- preventPaste()         // Blocks paste
- preventDevTools()      // Blocks F12, Ctrl+Shift+I, etc.
- handleVisibilityChange() // Detects tab switches
- handleWindowBlur()     // Detects window switches
- handleFullscreenChange() // Detects fullscreen exit
- recordCheatingAttempt() // Logs violations and triggers warnings
```

### Backend (Notification System)
```python
@app.post("/report-cheating")
def report_cheating(data: Dict, ...):
    # Creates notification for teacher
    # Includes: student name, quiz title, violations, reason
    # Type: "cheating_alert"
```

## Best Practices

### For Teachers
1. **Before Quiz**
   - Explain anti-cheating rules to students
   - Demonstrate fullscreen mode
   - Show what happens when rules are violated
   - Emphasize the three-strike system

2. **During Quiz**
   - Monitor notification panel
   - Be available for technical issues
   - Distinguish between intentional cheating and technical problems

3. **After Quiz**
   - Review flagged submissions carefully
   - Consider context (network issues, browser crashes, etc.)
   - Apply fair judgment during manual grading

### For Students
1. **Preparation**
   - Close all unnecessary applications
   - Close all browser tabs except quiz
   - Ensure stable internet connection
   - Use a supported browser (Chrome, Firefox, Edge)

2. **During Quiz**
   - Stay focused on quiz window
   - Don't minimize or switch windows
   - Don't try to search for answers online
   - Don't attempt to copy questions

3. **If Technical Issues Occur**
   - Inform teacher immediately
   - Don't panic if you accidentally trigger a warning
   - You have 2 warnings before termination

## Limitations & Considerations

### What the System CAN Detect
✅ Tab/window switching
✅ Fullscreen exit attempts
✅ Copy/paste attempts
✅ Right-click attempts
✅ Developer tools access attempts

### What the System CANNOT Detect
❌ Using a second device (phone, tablet)
❌ Looking at physical notes
❌ Someone else in the room helping
❌ Screen sharing to another person
❌ Taking photos of the screen

### Additional Security Recommendations

1. **Physical Supervision**
   - Conduct quizzes in supervised computer labs when possible
   - Monitor students physically during important exams

2. **Question Randomization**
   - Already enabled in the system
   - Each student gets questions in different order

3. **Time Limits**
   - Set appropriate time limits per question
   - Prevents students from searching for answers

4. **Question Pool**
   - Create large question banks
   - Randomize which questions each student receives

5. **One-Attempt Policy**
   - Already enforced in the system
   - Students cannot retake the same quiz

## Troubleshooting

### Student Issues

**Problem**: "I accidentally pressed Esc and got a warning"
- **Solution**: Click "I Understand - Continue Quiz" and be more careful. You have 2 more chances.

**Problem**: "My browser crashed and I got terminated"
- **Solution**: Contact your teacher immediately. They can review your case and potentially allow a retake.

**Problem**: "I can't enter fullscreen mode"
- **Solution**: 
  - Try a different browser (Chrome recommended)
  - Check browser permissions
  - Disable browser extensions
  - Contact teacher for assistance

**Problem**: "The warning modal won't close"
- **Solution**: Click the "I Understand - Continue Quiz" button. If stuck, refresh the page (you'll lose progress).

### Teacher Issues

**Problem**: "I'm not receiving cheating notifications"
- **Solution**: 
  - Refresh your notification panel
  - Check if notifications are enabled
  - Verify backend is running properly

**Problem**: "Too many false positives"
- **Solution**: 
  - Educate students about the system
  - Consider technical issues (poor internet, old browsers)
  - Use judgment during manual review

## System Configuration

### Adjusting Warning Threshold
To change from 3 strikes to a different number, edit:
```javascript
// File: frontend/src/routes/quiz/[id]/+page.svelte
// Line: ~150

if (cheatingWarnings === 1) {
  // First warning
} else if (cheatingWarnings === 2) {
  // Second warning
} else if (cheatingWarnings >= 3) {  // Change this number
  // Termination
}
```

### Disabling Specific Features
To disable certain anti-cheating features, comment out in `enableAntiCheat()`:
```javascript
function enableAntiCheat() {
  enterFullscreen();  // Comment to disable fullscreen
  // document.addEventListener('contextmenu', preventRightClick);  // Disabled
  // ... etc
}
```

## Privacy & Ethics

### Data Collection
- System only logs violation counts and types
- No screenshots or recordings are taken
- Student privacy is respected

### Fair Use
- System is designed to prevent cheating, not punish mistakes
- Teachers should use judgment when reviewing flagged submissions
- Technical issues should be distinguished from intentional cheating

### Student Rights
- Students should be informed about anti-cheating measures
- Clear rules should be communicated before quizzes
- Appeal process should be available for disputed cases

## Support

For technical issues or questions:
1. Check this guide first
2. Review the main README.md
3. Check NETWORK-TROUBLESHOOTING.md for connectivity issues
4. Contact your system administrator

---

**Last Updated**: January 2025
**System Version**: 1.9-ANTI-CHEAT
