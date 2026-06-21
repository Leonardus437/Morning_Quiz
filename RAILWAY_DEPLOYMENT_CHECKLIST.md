# ✅ Railway Deployment Checklist

## 📋 PRE-DEPLOYMENT (5 min)

### GitHub Repository Ready?
- [ ] Repository pushed to GitHub
- [ ] Backend folder exists at `/backend`
- [ ] Files exist:
  - [ ] `/backend/requirements.txt`
  - [ ] `/backend/start.py`
  - [ ] `/backend/main.py`
  - [ ] `/backend/railway.json`

---

## 🚂 RAILWAY SETUP (10 min)

### Step 1: Create Project
- [ ] Go to https://railway.app
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose: `Morning_Quiz-master`

### Step 2: Add Database
- [ ] Click "+ New" → "Database" → "PostgreSQL"
- [ ] Wait for green status ✅
- [ ] Click PostgreSQL service
- [ ] Go to "Variables" tab
- [ ] Copy full `DATABASE_URL` value

### Step 3: Configure Backend
**Settings Tab:**
- [ ] Root Directory: `/backend`
- [ ] Start Command: `python start.py`
- [ ] Save changes

**Variables Tab:**
- [ ] Add `DATABASE_URL` = `<paste from Step 2>`
- [ ] Add `SECRET_KEY` = `tvet-quiz-2024-production`
- [ ] Add `OFFLINE_MODE` = `false`
- [ ] Add `PORT` = `8000`

**Networking:**
- [ ] Click "Generate Domain"
- [ ] Copy domain (e.g., `morning-quiz.up.railway.app`)

### Step 4: Verify Deployment
- [ ] Backend status shows green ✅
- [ ] Check logs: "Application startup complete"
- [ ] Test URL: `https://your-backend.up.railway.app/health`
- [ ] Response: `{"status":"healthy"}`

---

## ☁️ CLOUDFLARE FRONTEND (5 min)

### Update Environment Variable
- [ ] Go to https://dash.cloudflare.com
- [ ] Pages → Find `tsskwizi` project
- [ ] Settings → Environment variables
- [ ] Update or add: `VITE_API_BASE`
- [ ] Value: `https://your-backend.up.railway.app` (from Railway)
- [ ] NO trailing slash!
- [ ] Save

### Redeploy Frontend
- [ ] Go to "Deployments" tab
- [ ] Click "⋮" on latest deployment
- [ ] Click "Retry deployment"
- [ ] Wait 2-3 minutes
- [ ] Status shows "Success" ✅

---

## 🧪 TESTING (5 min)

### Backend Health Check
```
URL: https://your-backend.up.railway.app/health
Expected: {"status":"healthy","service":"TVET Quiz API","version":"2.0"}
```
- [ ] Health check passes ✅

### Frontend Loads
```
URL: https://tsskwizi.pages.dev
Expected: Login page appears
```
- [ ] Frontend loads ✅

### Authentication Works
```
Login: admin / admin123
Expected: Redirects to dashboard
```
- [ ] Login successful ✅

### Create Test Quiz
```
1. Login as teacher001 / teacher123
2. Go to Questions → Create question
3. Go to Quizzes → Create quiz
4. Broadcast quiz
```
- [ ] Quiz creation works ✅

---

## 📊 MONITORING SETUP (Optional, 5 min)

### Railway Metrics
- [ ] Railway → Backend → "Metrics" tab
- [ ] Check: CPU usage, Memory, Network
- [ ] Set up alerts (Settings → Notifications)

### Error Tracking
- [ ] Railway → Backend → "Deployments"
- [ ] Bookmark logs URL for quick access
- [ ] Check logs daily for errors

---

## 🔐 SECURITY CHECKLIST

### Production Security
- [ ] Change default passwords:
  - [ ] Admin: admin / admin123 → Change in app
  - [ ] Teacher: teacher001 / teacher123 → Change in app
- [ ] Update SECRET_KEY to random value:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
  - [ ] Update in Railway variables
- [ ] Review CORS settings (allow only your domains)
- [ ] Enable HTTPS only (Railway does this automatically)

---

## 💰 COST MANAGEMENT

### Monitor Usage
- [ ] Railway → Profile → "Usage"
- [ ] Check credits remaining
- [ ] Set up billing alerts

### Optimize Costs
- [ ] App sleeps after 30 min (free tier) ✅
- [ ] Database optimized ✅
- [ ] No unnecessary background jobs ✅
- [ ] Expected: $0-5/month for school usage

---

## 📝 DOCUMENTATION

### Save These URLs
```
Backend API: https://_______________________.up.railway.app
Frontend: https://tsskwizi.pages.dev
Railway Dashboard: https://railway.app/dashboard
Cloudflare Dashboard: https://dash.cloudflare.com
```

### Save Credentials
```
Railway Login: _______________________
GitHub Repo: _______________________
Admin User: admin / (change password!)
Teacher User: teacher001 / (change password!)
```

---

## 🆘 TROUBLESHOOTING

### If Backend Doesn't Start:
1. Check logs: Railway → Backend → Deployments → Latest
2. Verify DATABASE_URL is set correctly
3. Verify Root Directory = `/backend`
4. See: RAILWAY_TROUBLESHOOTING.md

### If Frontend Can't Connect:
1. Check VITE_API_BASE matches Railway domain
2. Clear browser cache (Ctrl+Shift+R)
3. Verify Cloudflare redeployed
4. See: RAILWAY_TROUBLESHOOTING.md

### If Login Fails:
1. Check backend logs for "Seeded admin user"
2. Restart backend service
3. Try default credentials again

---

## ✅ FINAL VERIFICATION

Run through this test sequence:

1. **Backend Health:**
   - [ ] `curl https://your-backend.up.railway.app/health`
   - [ ] Returns 200 OK with JSON

2. **Frontend Loads:**
   - [ ] Open `https://tsskwizi.pages.dev`
   - [ ] Login page appears
   - [ ] No console errors (F12)

3. **Admin Login:**
   - [ ] Login: admin / admin123
   - [ ] Dashboard loads
   - [ ] Can see admin menu

4. **Teacher Features:**
   - [ ] Login: teacher001 / teacher123
   - [ ] Can create questions
   - [ ] Can create quizzes
   - [ ] Can broadcast quiz

5. **Student Features:**
   - [ ] Upload test student
   - [ ] Login as student
   - [ ] Can see broadcasted quiz
   - [ ] Can take quiz

---

## 🎉 SUCCESS!

If all checkboxes above are ✅:

**🎊 CONGRATULATIONS! Your system is live!**

### Next Steps:
1. Change all default passwords
2. Upload real student list
3. Create course content
4. Train teachers on system
5. Start using in classroom

### Support:
- **Railway Issues:** https://discord.gg/railway
- **App Issues:** Check RAILWAY_TROUBLESHOOTING.md
- **Questions:** Review documentation in `/docs`

---

## 📅 MAINTENANCE SCHEDULE

### Daily (5 min):
- [ ] Check Railway metrics
- [ ] Review error logs
- [ ] Verify system accessible

### Weekly (15 min):
- [ ] Check remaining credits
- [ ] Review usage patterns
- [ ] Backup important data

### Monthly (30 min):
- [ ] Review security settings
- [ ] Update dependencies if needed
- [ ] Clean up old quiz data
- [ ] Review student performance reports

---

**Deployment Date:** _________________

**Deployed By:** _________________

**Notes:**
_______________________________________
_______________________________________
_______________________________________

---

**System Status: 🟢 LIVE & OPERATIONAL**
