# 🚀 RAILWAY DEPLOYMENT - QUICK REFERENCE CARD

## 🎯 Your Mission:
Deploy backend to NEW Railway account (fresh 30-day trial)

---

## ⚡ SUPER QUICK STEPS (5 Minutes):

### 1️⃣ NEW PROJECT
- Railway.app → **New Project** → **Deploy from GitHub**
- Select: `Morning_Quiz-master` repo

### 2️⃣ ADD DATABASE  
- Click **+ New** → **Database** → **PostgreSQL**
- Copy the `DATABASE_URL` from Variables tab

### 3️⃣ CONFIGURE BACKEND
- Click backend service → **Settings**
- Root Directory: `/backend`
- Start Command: `python start.py`

### 4️⃣ SET VARIABLES
Go to **Variables** tab, add:
```
DATABASE_URL=<paste from step 2>
SECRET_KEY=your-secret-key-2024
OFFLINE_MODE=false
PORT=8000
```

### 5️⃣ GET URL
- Settings → Networking → **Generate Domain**
- Copy URL (e.g., `backend-production-xyz.up.railway.app`)

### 6️⃣ UPDATE CLOUDFLARE
- Cloudflare Pages → `tsskwizi`
- Settings → Environment Variables
- `VITE_API_BASE` = your Railway URL
- **Redeploy**

---

## ✅ TEST IT:

1. Open: `https://tsskwizi.pages.dev`
2. Login: `admin` / `admin123`
3. Works? **DONE!** 🎉

---

## 🆘 TROUBLESHOOTING:

| Problem | Solution |
|---------|----------|
| "Application failed to respond" | Check DATABASE_URL is set correctly |
| "Module not found" | Make sure root directory is `/backend` |
| "Can't connect to database" | Verify PostgreSQL service is running |
| Frontend shows errors | Update VITE_API_BASE in Cloudflare |

---

## 📊 WHAT YOU'LL SEE:

**Railway Dashboard:**
```
┌─────────────────┐
│ PostgreSQL      │ ← Database (auto-created)
├─────────────────┤
│ backend service │ ← Your FastAPI app
└─────────────────┘
```

**Environment Variables:**
```
DATABASE_URL=postgresql://postgres:pass@host:5432/railway
SECRET_KEY=your-secret-key-2024
OFFLINE_MODE=false
PORT=8000
```

**Deployment Logs Should Show:**
```
✓ Building...
✓ Starting server...
✓ Application startup complete
✓ Uvicorn running on http://0.0.0.0:8000
```

---

## 💡 PRO TIPS:

1. **Save Railway URL**: You'll need it for Cloudflare
2. **Check logs first**: If error, go to Deployments → View logs
3. **Database takes ~30s**: Wait for PostgreSQL to be ready
4. **Free tier limits**: $5 credit, 30 days trial

---

## 🔗 IMPORTANT LINKS:

- Railway Dashboard: https://railway.app/dashboard
- Your Frontend: https://tsskwizi.pages.dev
- Cloudflare Dashboard: https://dash.cloudflare.com

---

## 📝 CHECKLIST:

- [ ] Logged into NEW Railway account
- [ ] Created new project from GitHub
- [ ] Added PostgreSQL database
- [ ] Configured backend service (root: `/backend`)
- [ ] Set environment variables (DATABASE_URL, SECRET_KEY)
- [ ] Generated domain
- [ ] Updated Cloudflare VITE_API_BASE
- [ ] Tested login on frontend
- [ ] System working!

---

## 🎓 REMEMBER:

- Backend = Railway (database + API)
- Frontend = Cloudflare Pages (static site)
- They talk via VITE_API_BASE URL

**Current Setup:**
```
Users → Cloudflare (tsskwizi.pages.dev)
          ↓
        Railway (your-backend.up.railway.app)
          ↓
        PostgreSQL Database
```

---

**READY? Go to Step 1 in the full guide!** 📖
