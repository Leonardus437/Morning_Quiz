# 🚀 Quick Deployment Guide

## Frontend (Cloudflare Pages)

### Option 1: Wrangler CLI (Fastest)
```bash
cd frontend
npm install
npm run build
npx wrangler pages deploy build --project-name=tsskwizi
```

### Option 2: Cloudflare Dashboard
1. Build locally:
   ```bash
   cd frontend
   npm install
   npm run build
   ```
2. Go to https://dash.cloudflare.com
3. Select Pages > tsskwizi
4. Click "Create deployment"
5. Upload `frontend/build` folder

### Option 3: Git Integration (Automatic)
```bash
git add .
git commit -m "Deploy: Latest version"
git push origin main
```
Cloudflare will auto-deploy from Git.

---

## Backend (Render)

### Option 1: Manual Deploy (Dashboard)
1. Go to https://dashboard.render.com
2. Select service: **tsskwizi-backend**
3. Click "Manual Deploy" > "Deploy latest commit"

### Option 2: Git Push (Automatic)
```bash
git add .
git commit -m "Deploy: Backend update"
git push origin main
```
Render will auto-deploy from Git.

### Option 3: Render CLI
```bash
render deploy
```

---

## ⚡ Quick Deploy (Both at Once)

```bash
# Build frontend
cd frontend && npm run build && cd ..

# Commit and push
git add .
git commit -m "Deploy: Latest version $(date)"
git push origin main
```

Both Cloudflare and Render will auto-deploy!

---

## 🔍 Verify Deployment

### Frontend
- URL: https://tsskwizi.pages.dev
- Test: Login with `teacher001` / `teacher123`

### Backend
- URL: https://tvet-quiz-backend.onrender.com/health
- Expected: `{"status": "healthy"}`

### Full Test
1. Open frontend URL
2. Login as teacher
3. Create a quiz
4. Login as student (new tab)
5. Take the quiz
6. View results

---

## 🐛 Troubleshooting

**Frontend not updating?**
- Clear Cloudflare cache
- Hard refresh browser (Ctrl+Shift+R)

**Backend not responding?**
- Check Render logs
- Verify DATABASE_URL is set
- Cold start takes 30-60 seconds

**Database issues?**
- Check PostgreSQL is running on Render
- Verify connection string

---

## 📝 Environment Variables (Render)

Make sure these are set in Render dashboard:

```
DATABASE_URL = [Your PostgreSQL connection string]
SECRET_KEY = [Random 32-character string]
OFFLINE_MODE = false
```

To set:
1. Go to Render dashboard
2. Select tsskwizi-backend
3. Environment > Add Environment Variable
