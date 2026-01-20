# 🚀 DEPLOYMENT QUICK REFERENCE

## 📋 Your URLs (After Deployment)

```
Frontend:  https://tvet-quiz.pages.dev
Backend:   https://tvet-quiz-backend.onrender.com
API Docs:  https://tvet-quiz-backend.onrender.com/docs
Admin:     https://tvet-quiz.pages.dev/admin
Teacher:   https://tvet-quiz.pages.dev/teacher
Student:   https://tvet-quiz.pages.dev
```

## 🔑 Default Credentials

```
Admin:
  Username: admin
  Password: pass123

Teacher:
  Username: teacher001
  Password: teacher123
```

## ⚡ Quick Commands

### Prepare for Deployment
```bash
prepare-deployment.bat
```

### Push to GitHub
```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

### Check Deployment Status
```bash
# GitHub Actions
https://github.com/Leonardus437/Morning_Quiz/actions

# Render Dashboard
https://dashboard.render.com

# Cloudflare Dashboard
https://dash.cloudflare.com
```

## 🔧 Environment Variables

### Render (Backend)
```
DATABASE_URL = [From Render PostgreSQL]
SECRET_KEY = [Generate: openssl rand -hex 32]
OFFLINE_MODE = false
PYTHON_VERSION = 3.11.0
```

### Cloudflare Pages (Frontend)
```
NODE_VERSION = 18
VITE_API_BASE = https://tvet-quiz-backend.onrender.com
```

### GitHub Secrets
```
RENDER_API_KEY
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
VITE_API_BASE
```

## 📊 Deployment Timeline

```
Step 1: Prepare Repository        (5 min)
Step 2: Deploy Backend (Render)    (10 min)
Step 3: Deploy Frontend (CF)       (5 min)
Step 4: Configure GitHub Secrets   (5 min)
Step 5: Test Everything           (5 min)
----------------------------------------
TOTAL:                            30 min
```

## 🎯 Testing Checklist

- [ ] Backend API responds: `/docs`
- [ ] Frontend loads
- [ ] Admin login works
- [ ] Teacher login works
- [ ] Student login works
- [ ] Create quiz works
- [ ] Take quiz works
- [ ] View results works

## 💡 Pro Tips

1. **Cold Start:** First request takes ~30s (Render free tier)
2. **Keep Alive:** Use UptimeRobot to ping every 14 min
3. **Logs:** Check Render logs for backend issues
4. **Build Logs:** Check Cloudflare for frontend issues
5. **CORS:** Ensure backend allows your frontend domain

## 🆘 Quick Fixes

### Backend not responding
```bash
# Check Render logs
# Restart service in Render dashboard
```

### Frontend not loading
```bash
# Check Cloudflare Pages build logs
# Retry deployment
```

### Database connection error
```bash
# Verify DATABASE_URL in Render env vars
# Check PostgreSQL is running
```

### API calls failing
```bash
# Check CORS settings in backend/main.py
# Verify VITE_API_BASE in frontend
```

## 📱 Share with Students

```
Quiz System: https://tvet-quiz.pages.dev

Instructions:
1. Connect to EdNet WiFi
2. Open browser
3. Go to link above
4. Login with your credentials
5. Take quiz!

Data usage: ~20 KB per quiz (very low!)
```

## 🎉 Success Indicators

✅ GitHub Actions: All green checks
✅ Render: Service "Live"
✅ Cloudflare: Deployment "Success"
✅ Frontend: Loads without errors
✅ Backend: API docs accessible
✅ Login: Works for all roles

---

**Read full guide:** DEPLOYMENT_GUIDE.md
