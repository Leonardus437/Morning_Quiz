# 🚀 DEPLOY TO PRODUCTION

## ✅ YOUR DEPLOYMENT SETUP

**Backend:** https://tvet-quiz-backend.onrender.com
- Render Dashboard: https://dashboard.render.com/web/srv-d5drg0p5pdvs73dgmbe0
- Auto-deploys from GitHub `main` branch

**Frontend:** https://tsskwizi.pages.dev
- Cloudflare Dashboard: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
- Auto-deploys from GitHub `main` branch

---

## 🎯 DEPLOY IN 2 STEPS

### STEP 1: Push Backend Changes
```bash
git add backend/main.py
git commit -m "Update CORS for production"
git push origin main
```
✅ Render auto-deploys in 2-3 minutes

### STEP 2: Deploy Frontend
```bash
cd frontend
npm install
npm run build
npx wrangler pages deploy build --project-name=tsskwizi
```
✅ Cloudflare deploys in 1 minute

---

## ⚡ ONE-CLICK DEPLOY

Run: `DEPLOY_NOW.bat`

---

## ✅ VERIFY DEPLOYMENT

1. **Backend Health:**
   - Visit: https://tvet-quiz-backend.onrender.com/health
   - Should show: `{"status": "healthy", "version": "2.0-ANTI-CHEAT"}`

2. **Frontend:**
   - Visit: https://tsskwizi.pages.dev/
   - Should load login page

3. **Test Login:**
   - Teacher: `teacher001` / `teacher123`
   - Student: `student001` / `pass123`

---

## 📝 WHAT WAS CHANGED

✅ `frontend/.env.production` → `https://tvet-quiz-backend.onrender.com`
✅ `backend/main.py` → CORS allows `tsskwizi.pages.dev`

---

## 🔄 LOCAL vs PRODUCTION

**Local (Docker):**
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Database: Docker PostgreSQL

**Production:**
- Frontend: `https://tsskwizi.pages.dev`
- Backend: `https://tvet-quiz-backend.onrender.com`
- Database: Render PostgreSQL

**All logic remains 100% identical!** ✅

---

## 🎉 READY!

Everything is configured. Just run `DEPLOY_NOW.bat` or push to GitHub!
