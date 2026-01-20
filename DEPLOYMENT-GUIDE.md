# 🚀 Production Deployment Guide

## Current Setup
- **Frontend**: Cloudflare Pages (tsskwizi.pages.dev)
- **Backend**: Render (tvet-quiz-backend.onrender.com)
- **Database**: PostgreSQL on Render
- **Repository**: https://github.com/Leonardus437/Morning_Quiz

## ✅ What's Already Configured

The system is **already configured** to work in production:

1. **API Client Auto-Detection** (`frontend/src/lib/api.js`):
   - Automatically detects Cloudflare Pages domain
   - Routes to Render backend: `https://tvet-quiz-backend.onrender.com`
   - No manual configuration needed!

2. **Anti-Cheating System**: Fully implemented and ready
   - Fullscreen lock
   - Tab/window switch detection
   - Copy/paste prevention
   - Developer tools blocking
   - Three-strike warning system
   - Auto-submit on 3rd violation
   - Teacher notifications

3. **Environment Files**: Already set up
   - `.env.production` points to Render backend
   - SvelteKit adapter configured for static deployment

## 📋 Deployment Steps

### Step 1: Push to GitHub

```bash
cd d:\Morning_Quiz-master
git add .
git commit -m "Add anti-cheating system with fullscreen lock and teacher notifications"
git push origin main
```

### Step 2: Deploy Frontend to Cloudflare Pages

**Option A: Automatic Deployment (Recommended)**

Cloudflare Pages should auto-deploy when you push to GitHub.

**Option B: Manual Deployment**

1. Go to: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
2. Click **"Create deployment"**
3. Select branch: `main`
4. Build settings:
   - **Build command**: `cd frontend && npm install && npm run build`
   - **Build output directory**: `frontend/build`
   - **Root directory**: `/`
5. Environment variables:
   - `PUBLIC_API_URL` = `https://tvet-quiz-backend.onrender.com`
6. Click **"Save and Deploy"**

### Step 3: Verify Backend on Render

1. Go to: https://dashboard.render.com/
2. Check service: **tvet-quiz-backend**
3. Ensure it's running (Status: "Deployed")
4. Test endpoint: https://tvet-quiz-backend.onrender.com/health

### Step 4: Test Production System

1. Visit: https://tsskwizi.pages.dev
2. Login with default credentials:
   - Teacher: `teacher001` / `teacher123`
   - Student: `student001` / `pass123`
3. Test anti-cheating features:
   - Start a quiz → should enter fullscreen
   - Try pressing Esc → warning modal
   - Try switching tabs → warning modal
   - Try right-click → blocked
   - Try copy/paste → blocked

## 🔧 Build Configuration

### Frontend Build Settings (Cloudflare Pages)

```bash
# Build command
cd frontend && npm install && npm run build

# Build output directory
frontend/build

# Environment variables
PUBLIC_API_URL=https://tvet-quiz-backend.onrender.com
```

### Backend Settings (Render)

```bash
# Build command
pip install -r backend/requirements.txt

# Start command
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT

# Environment variables
DATABASE_URL=<your-postgres-url>
SECRET_KEY=<your-secret-key>
```

## 🌐 Domain Configuration

### Current URLs
- **Frontend**: https://tsskwizi.pages.dev
- **Backend**: https://tvet-quiz-backend.onrender.com
- **Database**: PostgreSQL on Render (Oregon region)

### Custom Domain (Optional)

To use a custom domain like `quiz.tsskwizi.com`:

1. Go to Cloudflare Pages settings
2. Add custom domain
3. Update DNS records
4. No code changes needed (API client auto-detects)

## 🔍 Troubleshooting

### Issue: Frontend shows "Connection failed"

**Solution**:
1. Check Render backend status
2. Verify backend URL: https://tvet-quiz-backend.onrender.com/health
3. Check browser console for CORS errors
4. Ensure backend has CORS enabled for Cloudflare domain

### Issue: Anti-cheating not working

**Solution**:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Check browser console for JavaScript errors
4. Verify fullscreen API is supported (modern browsers only)

### Issue: Backend cold start (slow first request)

**Solution**:
- Render free tier has cold starts (~30-60 seconds)
- Upgrade to paid tier for instant response
- Or keep backend warm with uptime monitor

### Issue: Database connection errors

**Solution**:
1. Check PostgreSQL status on Render
2. Verify DATABASE_URL environment variable
3. Check connection limits (free tier: 97 connections)
4. Restart backend service if needed

## 📊 Monitoring

### Check Deployment Status

**Frontend (Cloudflare)**:
```bash
# Visit deployment logs
https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
```

**Backend (Render)**:
```bash
# Visit service logs
https://dashboard.render.com/
# Select: tvet-quiz-backend → Logs
```

### Test Endpoints

```bash
# Backend health check
curl https://tvet-quiz-backend.onrender.com/health

# Frontend
curl https://tsskwizi.pages.dev
```

## 🔐 Security Checklist

- ✅ HTTPS enabled (automatic on Cloudflare & Render)
- ✅ Environment variables secured
- ✅ Database credentials not in code
- ✅ CORS configured for production domain
- ✅ Anti-cheating system active
- ✅ JWT authentication enabled
- ⚠️ Change default passwords after deployment!

## 🎯 Post-Deployment Tasks

1. **Change Default Credentials**:
   - Login as DOS/Admin
   - Create new teacher accounts
   - Delete default `teacher001` account

2. **Test All Features**:
   - Student registration
   - Quiz creation
   - Quiz taking (with anti-cheating)
   - Results viewing
   - PDF/Excel exports
   - Notifications

3. **Monitor Performance**:
   - Check response times
   - Monitor error logs
   - Track user activity

4. **Backup Database**:
   - Set up automatic backups on Render
   - Export data regularly

## 📱 Mobile Testing

Test on mobile devices:
- iOS Safari
- Android Chrome
- Fullscreen behavior may differ
- Touch interactions
- Network conditions

## 🔄 Update Workflow

When you make changes:

```bash
# 1. Make changes locally
# 2. Test locally with Docker
docker-compose up -d

# 3. Commit and push
git add .
git commit -m "Your changes"
git push origin main

# 4. Cloudflare auto-deploys frontend
# 5. Render auto-deploys backend (if connected to GitHub)
```

## 📞 Support

If issues persist:
1. Check GitHub repository issues
2. Review deployment logs
3. Test locally first with Docker
4. Verify all environment variables

## 🎉 Success Indicators

Your deployment is successful when:
- ✅ Frontend loads at https://tsskwizi.pages.dev
- ✅ Login works with default credentials
- ✅ Backend responds to API calls
- ✅ Anti-cheating features activate during quiz
- ✅ Teacher receives cheating notifications
- ✅ Quiz submission works
- ✅ Results display correctly

---

**Ready to deploy!** Follow the steps above and your production system will be live with all anti-cheating features working. 🚀
