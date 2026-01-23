# Chat Widget Debug Guide

## Quick Diagnosis

The chat widget should appear in the **bottom-right corner** of your screen when you're logged in. If you don't see it, follow these steps:

### Step 1: Check if you're logged in
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Type: `localStorage.getItem('user')`
4. Press Enter

**Expected result:** Should show user data like `{"id":1,"username":"student001","role":"student"}`
**If null:** You're not logged in - log in first

### Step 2: Check if the component is loaded
1. In Console, type: `document.querySelector('button[title="Open Knowledge Hub Chat"]')`
2. Press Enter

**Expected result:** Should return a button element
**If null:** Component not rendering

### Step 3: Force show the button (temporary test)
1. In Console, type:
```javascript
// Create a test button to verify positioning
const testBtn = document.createElement('button');
testBtn.innerHTML = '💬 TEST CHAT';
testBtn.style.cssText = 'position: fixed; bottom: 24px; right: 24px; z-index: 9999; background: blue; color: white; padding: 16px; border-radius: 50%; border: none; cursor: pointer;';
document.body.appendChild(testBtn);
testBtn.onclick = () => alert('Chat button position test - this should be visible!');
```

**Expected result:** Blue test button appears in bottom-right corner
**If not visible:** CSS or positioning issue

### Step 4: Check for JavaScript errors
1. Look at Console tab for any red error messages
2. Common issues:
   - Import errors
   - Store subscription errors
   - API connection errors

### Step 5: Verify user store state
1. In Console, type:
```javascript
// Check if user store has data
import { user } from '/src/lib/stores.js';
user.subscribe(u => console.log('User state:', u));
```

## Quick Fix Options

### Option 1: Hard Refresh
1. Press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. This clears cache and reloads everything

### Option 2: Clear Browser Data
1. Press `Ctrl + Shift + Delete`
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh page

### Option 3: Check Network Tab
1. Open Developer Tools (F12)
2. Go to Network tab
3. Refresh page
4. Look for failed requests (red entries)
5. Check if API calls are working

## Manual Chat Button Test

If the automatic button doesn't work, you can manually add one for testing:

```html
<!-- Add this to any page for testing -->
<button 
  style="position: fixed; bottom: 24px; right: 24px; z-index: 9999; background: linear-gradient(45deg, #2563eb, #9333ea); color: white; padding: 16px; border-radius: 50%; border: none; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.3);"
  onclick="alert('Chat system would open here')"
>
  💬
</button>
```

## Backend Chat API Test

Test if the chat backend is working:

```javascript
// Test chat rooms endpoint
fetch('http://localhost:8000/chat/rooms', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
})
.then(r => r.json())
.then(data => console.log('Chat rooms:', data))
.catch(err => console.error('Chat API error:', err));
```

## Expected Chat Features

When working correctly, you should see:
- 🔵 Floating button in bottom-right corner
- 💬 Chat bubble icon
- 🎯 Tooltip "Knowledge Hub 💬" on hover
- 📱 Responsive design (works on mobile)
- 🔴 Red notification dot when you have unread messages

## Common Issues & Solutions

### Issue: Button not visible
**Solution:** Check if `$user` store has data. Button only shows when logged in.

### Issue: Button visible but click doesn't work
**Solution:** Check browser console for JavaScript errors.

### Issue: Chat modal opens but no rooms
**Solution:** Check if backend chat API is running and accessible.

### Issue: Can't send messages
**Solution:** Verify authentication token and API connectivity.

## Contact Support

If none of these steps work:
1. Take a screenshot of the browser console (F12 → Console tab)
2. Note your browser type and version
3. Describe what you see vs. what you expect
4. Check if you're accessing the correct URL (localhost:3000)

## Quick Success Test

Run this in browser console to verify everything:

```javascript
console.log('=== CHAT WIDGET DEBUG ===');
console.log('1. User logged in:', !!localStorage.getItem('user'));
console.log('2. Token exists:', !!localStorage.getItem('token'));
console.log('3. Chat button exists:', !!document.querySelector('button[title*="Chat"]'));
console.log('4. Current URL:', window.location.href);
console.log('5. User agent:', navigator.userAgent);
console.log('========================');
```

This will show you exactly what's working and what isn't.