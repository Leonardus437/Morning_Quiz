# 🚀 DEPLOY TO https://tsskwizi.pages.dev/

## ✅ QUICK DEPLOYMENT (15 minutes)

### STEP 1: Deploy Backend (5 min)

**Option A: Render.com (Recommended - FREE)**
1. Go to: https://render.com/
2. Sign up (free)
3. Click "New +" → "Web Service"
4. Connect GitHub OR manual deploy
5. Settings:
   - Name: `tsskwizi-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free**
6. Add Environment Variables:
   ```
   DATABASE_URL=postgresql://user:pass@host/db  (Render provides free DB)
   SECRET_KEY=change-this-to-random-string
   ```
7. Click "Create Web Service"
8. Wait 3-5 minutes
9. Copy your backend URL: `https://tsskwizi-backend.onrender.com`

**Option B: Railway.app (Alternative - FREE)**
1. Go to: https://railway.app/
2. Sign up with GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Add environment variables (same as above)
6. Copy backend URL

---

### STEP 2: Update Frontend Config

**Already done!** ✅
- File: `frontend/.env.production`
- Updated to: `PUBLIC_API_URL=https://tsskwizi-backend.onrender.com`

**IMPORTANT:** Replace `tsskwizi-backend.onrender.com` with YOUR actual backend URL from Step 1!

---

### STEP 3: Deploy Frontend (5 min)

**Option A: Cloudflare Dashboard (Easiest)**
1. Run: `DEPLOY_TO_CLOUDFLARE.bat`
2. Wait for build to complete
3. Go to: https://dash.cloudflare.com/
4. Click "Pages" → "tsskwizi"
5. Click "Create deployment"
6. Drag the `frontend/build` folder
7. Done! Visit: https://tsskwizi.pages.dev/

**Option B: Wrangler CLI**
```bash
cd frontend
npm install
npm run build
npx wrangler pages deploy build --project-name=tsskwizi
```

---

### STEP 4: Configure Backend CORS

After backend is deployed, update `backend/main.py` CORS to allow your domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tsskwizi.pages.dev",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy backend.

---

## 🎯 VERIFICATION

1. **Backend Health Check:**
   - Visit: `https://tsskwizi-backend.onrender.com/health`
   - Should show: `{"status": "healthy", "version": "2.0-ANTI-CHEAT"}`

2. **Frontend:**
   - Visit: `https://tsskwizi.pages.dev/`
   - Should load login page

3. **Test Login:**
   - Teacher: `teacher001` / `teacher123`
   - Student: `student001` / `pass123`

---

## ⚠️ IMPORTANT NOTES

### Free Tier Limitations:
- **Render.com**: Backend sleeps after 15 min inactivity (wakes in 30 sec)
- **Database**: 1GB free PostgreSQL on Render
- **Cloudflare Pages**: Unlimited bandwidth (perfect for frontend)

### Keep Backend Awake (Optional):
Use a free service like UptimeRobot to ping your backend every 5 minutes:
- URL to ping: `https://tsskwizi-backend.onrender.com/health`

---

## 🔧 TROUBLESHOOTING

**Problem: "Failed to fetch" errors**
- Solution: Check backend URL in `frontend/.env.production`
- Verify CORS settings in `backend/main.py`

**Problem: Backend shows "Application failed to respond"**
- Solution: Check Render logs for errors
- Verify `requirements.txt` has all dependencies

**Problem: Database connection errors**
- Solution: Add PostgreSQL database in Render
- Update `DATABASE_URL` environment variable

---

## 📱 SHARE WITH STUDENTS

After deployment, students access:
- **URL**: `https://tsskwizi.pages.dev/`
- **Login**: Use credentials from teacher panel

---

## 🎉 SUCCESS!

Your system is now live at:
- **Frontend**: https://tsskwizi.pages.dev/
- **Backend**: https://tsskwizi-backend.onrender.com/
- **Teacher Panel**: https://tsskwizi.pages.dev/teacher
- **API Docs**: https://tsskwizi-backend.onrender.com/docs

---

## 💡 NEXT STEPS

1. Test all features on production
2. Upload student lists
3. Create quizzes
4. Share URL with students
5. Monitor backend logs on Render dashboard

---

## 🆘 NEED HELP?

If deployment fails:
1. Check Render/Railway logs
2. Verify all environment variables
3. Test backend health endpoint
4. Check browser console for errors
