# EXPORT FIX - IMMEDIATE ACTIONS NEEDED

## Issues
1. **PDF Export**: 404 error - endpoint `/quizzes/28/export/pdf` not found
2. **Excel Export**: File downloads but is corrupted

## Root Cause
The deployed frontend (on Cloudflare Pages) is using OLD cached JavaScript that calls `/export/pdf` instead of `/export`.

## IMMEDIATE FIX

### Step 1: Clear Browser Cache
Tell users to:
1. Press `Ctrl + Shift + Delete` (Windows) or `Cmd + Shift + Delete` (Mac)
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh the page with `Ctrl + F5`

### Step 2: Redeploy Frontend
The frontend code is correct but Cloudflare Pages needs to rebuild:

```bash
cd frontend
npm run build
# Push to trigger Cloudflare Pages rebuild
git add .
git commit -m "Fix export endpoints"
git push
```

### Step 3: Backend Changes Applied
✅ Added Excel export endpoint: `/quizzes/{quiz_id}/export/excel`
✅ Fixed token access in API client
✅ Added XlsxWriter to requirements.txt

## Testing After Fix

### Test PDF Export:
```
GET https://tvet-quiz-backend.onrender.com/quizzes/28/export
Authorization: Bearer {token}
```
Should return PDF file

### Test Excel Export:
```
GET https://tvet-quiz-backend.onrender.com/quizzes/28/export/excel
Authorization: Bearer {token}
```
Should return Excel file

## Files Changed
1. `backend/main.py` - Added `/export/excel` endpoint
2. `frontend/src/lib/api.js` - Fixed token access and Excel endpoint
3. `backend/requirements.txt` - Added XlsxWriter

## Deploy Backend
```bash
cd backend
# If using Render, it will auto-deploy on git push
# Or restart the service manually
```

## Why Excel Was Corrupted
The old code was trying to download PDF from the Excel button, resulting in a PDF file with .xlsx extension, which Excel couldn't open.
