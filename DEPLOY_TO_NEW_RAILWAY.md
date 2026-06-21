# 🚂 Deploy Backend to NEW Railway Account - Step by Step

## ✅ What You Already Have:
- Frontend on Cloudflare: https://tsskwizi.pages.dev (WORKING)
- Backend was on Railway (trial ended)
- NEW Railway account (fresh 30 days trial)

---

## 📋 STEP 1: Login to Your NEW Railway Account

1. Go to: https://railway.app
2. Login with your NEW account
3. You should see: **$5 free credit + 30 days trial**

---

## 📋 STEP 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Connect your GitHub account (if not connected)
4. Select your repository: `Morning_Quiz-master`
5. Railway will detect your project

---

## 📋 STEP 3: Add PostgreSQL Database

1. In your project dashboard, click **"+ New"**
2. Select **"Database"**
3. Choose **"Add PostgreSQL"**
4. Railway will create a database automatically
5. Click on the database service
6. Go to **"Variables"** tab
7. Copy the **DATABASE_URL** (looks like `postgresql://postgres:...`)

---

## 📋 STEP 4: Configure Backend Service

1. Click on your backend service (the one from GitHub)
2. Go to **"Settings"** tab
3. Set **Root Directory**: `/backend`
4. Set **Start Command**: `python start.py`

---

## 📋 STEP 5: Add Environment Variables

Click on **"Variables"** tab and add these:

```
DATABASE_URL=<paste the PostgreSQL URL from Step 3>
SECRET_KEY=your-secret-key-change-in-production-2024
OFFLINE_MODE=false
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
HUGGINGFACE_API_KEY=hf_your_key_here
PORT=8000
```

**IMPORTANT:** Replace `DATABASE_URL` with the actual URL from your PostgreSQL service!

---

## 📋 STEP 6: Generate Domain

1. Go to **"Settings"** tab
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"**
4. Copy the generated URL (e.g., `https://your-backend.up.railway.app`)

---

## 📋 STEP 7: Update Cloudflare Frontend

1. Go to Cloudflare dashboard
2. Find your `tsskwizi.pages.dev` project
3. Go to **"Settings"** → **"Environment variables"**
4. Update `VITE_API_BASE` to your NEW Railway URL from Step 6
5. Example: `VITE_API_BASE=https://your-backend.up.railway.app`
6. Save and redeploy

---

## 📋 STEP 8: Test Your System

1. Open: `https://tsskwizi.pages.dev`
2. Try to login with: `admin` / `admin123`
3. If login works → SUCCESS! ✅

---

## 🔧 IF IT DOESN'T WORK:

### Check Railway Logs:
1. Go to Railway dashboard
2. Click on backend service
3. Click **"Deployments"** tab
4. Click latest deployment
5. Check logs for errors

### Common Issues:

**Issue 1: DATABASE_URL not set**
- Solution: Make sure you copied the FULL PostgreSQL URL

**Issue 2: Port binding error**
- Solution: Railway auto-sets PORT, don't worry about it

**Issue 3: Import errors**
- Solution: Check that all Python packages are in `requirements.txt`

---

## 📦 Required Files (Already in Your Project):

✅ `/backend/requirements.txt` - Python dependencies
✅ `/backend/main.py` - FastAPI application
✅ `/backend/start.py` - Railway startup script
✅ `/backend/railway.json` - Railway configuration

---

## 💰 Cost Tracking:

Railway NEW account gives:
- $5 free credit
- 30 days trial
- After that: Pay-as-you-go (approx $5-10/month for small usage)

**Monitor usage:**
1. Railway dashboard → Click profile icon
2. Go to **"Usage"**
3. See current spend

---

## 🆘 QUICK FIX COMMANDS:

If deployment fails, try these in Railway dashboard:

1. **Restart deployment:**
   - Go to service → Click "⋮" → "Restart"

2. **Force redeploy:**
   - Go to "Deployments" → Click "Redeploy"

3. **Check environment variables:**
   - Variables tab → Make sure DATABASE_URL is set

---

## ✅ SUCCESS CHECKLIST:

- [ ] Railway project created
- [ ] PostgreSQL database added
- [ ] DATABASE_URL copied
- [ ] Backend service configured (root: `/backend`)
- [ ] Environment variables added
- [ ] Domain generated
- [ ] Cloudflare updated with new Railway URL
- [ ] Login test successful

---

## 📞 NEED HELP?

Tell me which step you're stuck on and I'll guide you through it!

**Common Questions:**

Q: Where do I find DATABASE_URL?
A: Railway dashboard → PostgreSQL service → Variables tab → Copy DATABASE_URL

Q: My backend shows "Application failed to respond"
A: Check logs in Deployments tab, likely DATABASE_URL missing

Q: How do I know it's working?
A: Your Railway URL should show: `{"status":"healthy","service":"TVET Quiz API"}`

---

## 🎯 FINAL TEST:

Once everything is set up, test these URLs:

1. **Backend Health**: `https://your-backend.up.railway.app/health`
   - Should return: `{"status":"healthy"}`

2. **Frontend**: `https://tsskwizi.pages.dev`
   - Should load login page

3. **Full Login**: Login with `admin` / `admin123`
   - Should redirect to dashboard

**If all 3 work → YOU'RE DONE! 🎉**
