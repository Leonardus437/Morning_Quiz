# 🚀 QUICK DEPLOYMENT TO https://tsskwizi.pages.dev/

## ⚡ 3-STEP DEPLOYMENT (15 minutes)

### 1️⃣ BACKEND → Render.com (FREE)
```
1. https://render.com/ → Sign up
2. New Web Service → Connect repo
3. Build: pip install -r backend/requirements.txt
4. Start: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
5. Add PostgreSQL database (free)
6. Copy URL: https://tsskwizi-backend.onrender.com
```

### 2️⃣ UPDATE CONFIG
```
Edit: frontend/.env.production
Change: PUBLIC_API_URL=https://YOUR-BACKEND-URL.onrender.com
```

### 3️⃣ FRONTEND → Cloudflare Pages
```
Run: DEPLOY_PRODUCTION.bat
OR
cd frontend
npm install
npm run build
npx wrangler pages deploy build --project-name=tsskwizi
```

## ✅ VERIFY
- Backend: https://YOUR-BACKEND.onrender.com/health
- Frontend: https://tsskwizi.pages.dev/
- Login: teacher001 / teacher123

## 📝 NOTES
- Backend sleeps after 15 min (wakes in 30 sec)
- Free PostgreSQL: 1GB
- Cloudflare Pages: Unlimited bandwidth

## 🔧 FILES UPDATED
✅ frontend/.env.production → Backend URL
✅ backend/main.py → CORS for tsskwizi.pages.dev
✅ DEPLOY_PRODUCTION.bat → One-click deploy script
