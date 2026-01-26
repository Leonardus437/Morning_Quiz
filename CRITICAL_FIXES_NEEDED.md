# CRITICAL FIXES NEEDED

## Problem 1: Questions Not Visible (401 Errors)
**Root Cause:** Token not being sent with requests or expired
**Solution:** Force token refresh and better error handling

## Problem 2: AI Parser "Please logout and login again"
**Root Cause:** Token check failing in upload function
**Solution:** Remove token check, let API handle it

## Problem 3: Notification Spam
**Root Cause:** Polling every 1 second with 401 errors
**Solution:** Already fixed to 5 seconds, but need to handle 401 gracefully

## Implementation:
1. Fix token synchronization in api.js
2. Remove token check from question-types upload
3. Add better 401 error handling
4. Stop notification polling on 401 errors
