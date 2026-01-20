# 🚀 RENDER BACKEND DEPLOYMENT - STEP BY STEP

## ✅ PREREQUISITES

- GitHub account with your repository: https://github.com/Leonardus437/Morning_Quiz
- Email address for Render account

---

## 📋 STEP 1: CREATE RENDER ACCOUNT (2 minutes)

### 1.1 Go to Render
Open: https://render.com

### 1.2 Sign Up
- Click "Get Started" or "Sign Up"
- Choose "Sign up with GitHub"
- Authorize Render to access your GitHub

✅ **You're now logged into Render Dashboard**

---

## 🗄️ STEP 2: CREATE POSTGRESQL DATABASE (3 minutes)

### 2.1 Create New Database
1. Click "New +" button (top right)
2. Select "PostgreSQL"

### 2.2 Configure Database
Fill in these settings:

```
Name: tvet-quiz-db
Database: morning_quiz
User: quiz_user
Region: Frankfurt (or Oregon if closer)
PostgreSQL Version: 15
Datadog API Key: [Leave empty]
Plan: Free
```

### 2.3 Create Database
- Click "Create Database"
- Wait ~1 minute for provisioning

### 2.4 Copy Database URL
Once created, you'll see:
- **Internal Database URL** (starts with `postgresql://`)
- **External Database URL**

📋 **COPY THE INTERNAL DATABASE URL** - You'll need it in Step 3!

Example:
```
postgresql://quiz_user:xxxxx@dpg-xxxxx-a/morning_quiz
```

✅ **Database is ready!**

---

## 🔧 STEP 3: DEPLOY BACKEND SERVICE (5 minutes)

### 3.1 Create New Web Service
1. Click "New +" button
2. Select "Web Service"

### 3.2 Connect Repository
1. Click "Connect a repository"
2. Find: `Leonardus437/Morning_Quiz`
3. Click "Connect"

### 3.3 Configure Service

Fill in these EXACT settings:

```
Name: tvet-quiz-backend
Region: Frankfurt (same as database)
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Instance Type: Free
```

### 3.4 Add Environment Variables

Click "Advanced" → "Add Environment Variable"

Add these 4 variables:

**Variable 1:**
```
Key: DATABASE_URL
Value: [PASTE YOUR INTERNAL DATABASE URL FROM STEP 2.4]
```

**Variable 2:**
```
Key: SECRET_KEY
Value: [Generate below - see 3.5]
```

**Variable 3:**
```
Key: OFFLINE_MODE
Value: false
```

**Variable 4:**
```
Key: PYTHON_VERSION
Value: 3.11.0
```

### 3.5 Generate SECRET_KEY

Open Command Prompt and run:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste as SECRET_KEY value.

Example output:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

### 3.6 Create Web Service
- Click "Create Web Service"
- Render will start building and deploying

---

## ⏳ STEP 4: WAIT FOR DEPLOYMENT (3-5 minutes)

### 4.1 Monitor Build
You'll see:
```
==> Building...
==> Installing dependencies...
==> Starting service...
```

### 4.2 Check Status
Wait until you see:
```
✅ Live
Your service is live at https://tvet-quiz-backend.onrender.com
```

---

## ✅ STEP 5: VERIFY DEPLOYMENT (2 minutes)

### 5.1 Test API Docs
Open in browser:
```
https://tvet-quiz-backend.onrender.com/docs
```

You should see FastAPI Swagger documentation.

### 5.2 Test Health Check
Open:
```
https://tvet-quiz-backend.onrender.com/
```

Should return:
```json
{
  "status": "online",
  "message": "Morning Quiz System API"
}
```

### 5.3 Copy Your Backend URL
📋 **Save this URL - you'll need it for frontend:**
```
https://tvet-quiz-backend.onrender.com
```

---

## 🎉 SUCCESS CHECKLIST

- [x] Render account created
- [x] PostgreSQL database created
- [x] Database URL copied
- [x] Backend service created
- [x] Environment variables set
- [x] Service deployed successfully
- [x] API docs accessible
- [x] Backend URL saved

---

## 🔧 TROUBLESHOOTING

### Problem: Build Failed

**Check Logs:**
1. Go to Render Dashboard
2. Click on "tvet-quiz-backend"
3. Click "Logs" tab
4. Look for error messages

**Common Issues:**

**Error: "requirements.txt not found"**
```
Solution: Verify Root Directory is set to "backend"
```

**Error: "Module not found"**
```
Solution: Check requirements.txt has all dependencies
```

**Error: "Port already in use"**
```
Solution: Use $PORT in start command (already done)
```

### Problem: Service Won't Start

**Check Environment Variables:**
1. Go to "Environment" tab
2. Verify all 4 variables are set
3. Check DATABASE_URL is correct

**Restart Service:**
1. Click "Manual Deploy" → "Clear build cache & deploy"

### Problem: Database Connection Error

**Verify Database URL:**
1. Go to PostgreSQL database
2. Copy Internal Database URL again
3. Update DATABASE_URL in backend service
4. Redeploy

---

## 📊 RENDER FREE TIER INFO

### What You Get:
- ✅ 750 hours/month (24/7 uptime)
- ✅ 512 MB RAM
- ✅ Shared CPU
- ✅ PostgreSQL: 1 GB storage

### Limitations:
- ⚠️ Spins down after 15 min inactivity
- ⚠️ First request takes ~30 seconds (cold start)
- ⚠️ 90 days of logs

### Keep Service Awake:
Use UptimeRobot (free) to ping every 14 minutes:
```
https://uptimerobot.com
Monitor: https://tvet-quiz-backend.onrender.com
Interval: 14 minutes
```

---

## 🎯 NEXT STEPS

✅ **Backend is deployed!**

Now you can:
1. **Test the API** at `/docs`
2. **Deploy Frontend** to Cloudflare Pages
3. **Connect Frontend to Backend**

---

## 📱 YOUR BACKEND URL

```
https://tvet-quiz-backend.onrender.com
```

**Save this URL - you'll need it for:**
- Frontend configuration
- Testing
- Student access

---

## 🆘 NEED HELP?

**Render Dashboard:**
https://dashboard.render.com

**Render Docs:**
https://render.com/docs

**Check Logs:**
Dashboard → tvet-quiz-backend → Logs

**Restart Service:**
Dashboard → tvet-quiz-backend → Manual Deploy

---

## ✅ VERIFICATION COMMANDS

Test your backend:

```bash
# Test API docs
curl https://tvet-quiz-backend.onrender.com/docs

# Test health
curl https://tvet-quiz-backend.onrender.com/

# Test database connection
curl https://tvet-quiz-backend.onrender.com/health
```

---

**🎉 Backend deployment complete! Ready for frontend deployment.**
