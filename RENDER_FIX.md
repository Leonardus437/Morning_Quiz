# 🔧 RENDER DEPLOYMENT FIX

## ❌ Problem: "source code string cannot contain null bytes"

This means corrupted files in your backend folder.

## ✅ SOLUTION: Change Root Directory

### STEP 1: Delete Current Service

1. Go to Render Dashboard
2. Click on "tvet-quiz-backend"
3. Click "Settings" (bottom left)
4. Scroll down to "Delete Web Service"
5. Type the service name and delete

### STEP 2: Create New Service with Correct Settings

1. Click "New +" → "Web Service"
2. Connect: `Leonardus437/Morning_Quiz`
3. **IMPORTANT CHANGE:**

```
Name: tvet-quiz-backend
Region: Oregon
Branch: master
Root Directory: (LEAVE EMPTY - DO NOT PUT "backend")
Runtime: Python 3
Build Command: cd backend && pip install -r requirements.txt
Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
Plan: Free
```

### STEP 3: Add Environment Variables (Same as Before)

```
DATABASE_URL = postgresql://quiz_user:FBIgnnj8c6ogdJKu8jv9DUgZGxvZpful@dpg-d5drasbuibrs7395sav0-a/morning_quiz
SECRET_KEY = 811080baa633933b85373037f13aadfa9bf817af3f03ca24190f66a7b324093b
OFFLINE_MODE = false
PYTHON_VERSION = 3.11.0
```

### STEP 4: Create Web Service

Click "Create Web Service"

---

## 🎯 KEY CHANGES:

### Before (WRONG):
```
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### After (CORRECT):
```
Root Directory: (EMPTY)
Build Command: cd backend && pip install -r requirements.txt
Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## ✅ This Will Work Because:

1. Root directory is empty (scans whole repo)
2. Build command navigates to backend folder
3. Start command runs from backend folder
4. Avoids loading corrupted test files

---

## 🚀 AFTER DEPLOYMENT:

Test at: https://tvet-quiz-backend.onrender.com/docs

Should see FastAPI documentation!
