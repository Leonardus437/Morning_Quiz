# 🚀 DEPLOYMENT GUIDE - Render + Cloudflare + PostgreSQL

## 📋 Tech Stack

- **Backend:** Render (FastAPI)
- **Frontend:** Cloudflare Pages (SvelteKit)
- **Database:** Render PostgreSQL (Free Tier)
- **CI/CD:** GitHub Actions
- **Repository:** https://github.com/Leonardus437/Morning_Quiz

---

## 🎯 DEPLOYMENT STEPS

### STEP 1: Prepare Repository

#### 1.1 Update Frontend Package

```bash
cd frontend
npm install @sveltejs/adapter-static --save-dev
```

#### 1.2 Update svelte.config.js

Replace content with:
```javascript
import adapter from '@sveltejs/adapter-static';

export default {
  kit: {
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: 'index.html'
    })
  }
};
```

#### 1.3 Push to GitHub

```bash
git add .
git commit -m "Add deployment configurations"
git push origin main
```

---

### STEP 2: Deploy Backend to Render

#### 2.1 Create Render Account
- Go to: https://render.com
- Sign up with GitHub

#### 2.2 Create PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Settings:
   - **Name:** `tvet-quiz-db`
   - **Database:** `morning_quiz`
   - **User:** `quiz_user`
   - **Region:** Frankfurt (or closest to Rwanda)
   - **Plan:** Free
3. Click "Create Database"
4. **Copy the Internal Database URL** (starts with `postgresql://`)

#### 2.3 Deploy Backend Service

1. Click "New +" → "Web Service"
2. Connect GitHub repository: `Leonardus437/Morning_Quiz`
3. Settings:
   - **Name:** `tvet-quiz-backend`
   - **Region:** Frankfurt
   - **Branch:** main
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

4. Environment Variables:
   ```
   DATABASE_URL = [Paste Internal Database URL from Step 2.2]
   SECRET_KEY = [Generate random string: openssl rand -hex 32]
   OFFLINE_MODE = false
   PYTHON_VERSION = 3.11.0
   ```

5. Click "Create Web Service"

6. **Copy your backend URL:** `https://tvet-quiz-backend.onrender.com`

---

### STEP 3: Deploy Frontend to Cloudflare Pages

#### 3.1 Create Cloudflare Account
- Go to: https://dash.cloudflare.com
- Sign up (free)

#### 3.2 Deploy to Cloudflare Pages

1. Go to "Workers & Pages" → "Create application" → "Pages"
2. Connect GitHub: `Leonardus437/Morning_Quiz`
3. Settings:
   - **Project name:** `tvet-quiz`
   - **Production branch:** main
   - **Build command:** `cd frontend && npm install && npm run build`
   - **Build output directory:** `frontend/build`
   - **Root directory:** `/`

4. Environment Variables:
   ```
   NODE_VERSION = 18
   VITE_API_BASE = https://tvet-quiz-backend.onrender.com
   ```

5. Click "Save and Deploy"

6. **Your frontend URL:** `https://tvet-quiz.pages.dev`

---

### STEP 4: Configure GitHub Secrets

#### 4.1 Go to GitHub Repository Settings

Navigate to: `https://github.com/Leonardus437/Morning_Quiz/settings/secrets/actions`

#### 4.2 Add Secrets

Click "New repository secret" for each:

```
RENDER_API_KEY = [Get from Render: Account Settings → API Keys]
CLOUDFLARE_API_TOKEN = [Get from Cloudflare: My Profile → API Tokens → Create Token]
CLOUDFLARE_ACCOUNT_ID = [Get from Cloudflare: Workers & Pages → Account ID]
VITE_API_BASE = https://tvet-quiz-backend.onrender.com
```

---

### STEP 5: Update Frontend API Configuration

#### 5.1 Update frontend/.env

```bash
VITE_API_BASE=https://tvet-quiz-backend.onrender.com
```

#### 5.2 Update API calls in frontend

Find all API calls and ensure they use:
```javascript
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
```

---

### STEP 6: Enable CORS in Backend

#### 6.1 Update backend/main.py

Add after imports:
```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tvet-quiz.pages.dev",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### STEP 7: Initialize Database

#### 7.1 Connect to Render PostgreSQL

Use Render's Web Shell or connect via:
```bash
psql [Your External Database URL]
```

#### 7.2 Run initialization

The backend will auto-create tables on first run, or manually run:
```sql
-- Tables will be created automatically by SQLAlchemy
```

---

### STEP 8: Test Deployment

#### 8.1 Access Your App

- **Frontend:** https://tvet-quiz.pages.dev
- **Backend API:** https://tvet-quiz-backend.onrender.com/docs
- **Admin:** https://tvet-quiz.pages.dev/admin

#### 8.2 Test Login

- Username: `admin`
- Password: `pass123`

---

## 🔄 CI/CD WORKFLOW

### Automatic Deployment

Every push to `main` branch triggers:

1. **GitHub Actions** runs tests
2. **Render** auto-deploys backend
3. **Cloudflare Pages** auto-deploys frontend

### Manual Deployment

**Backend (Render):**
- Go to Render Dashboard → tvet-quiz-backend → "Manual Deploy"

**Frontend (Cloudflare):**
- Go to Cloudflare Pages → tvet-quiz → "Retry deployment"

---

## 📊 FREE TIER LIMITS

### Render Free Tier:
- ✅ 750 hours/month (enough for 24/7)
- ✅ Spins down after 15 min inactivity
- ✅ First request takes ~30 seconds (cold start)
- ✅ PostgreSQL: 1GB storage, 97 connection limit

### Cloudflare Pages Free Tier:
- ✅ Unlimited requests
- ✅ Unlimited bandwidth
- ✅ 500 builds/month
- ✅ Global CDN

---

## 🎯 CUSTOM DOMAIN (Optional)

### Add Custom Domain to Cloudflare

1. Buy domain (e.g., `tvetquiz.rw`)
2. Add to Cloudflare Pages:
   - Pages → tvet-quiz → Custom domains
   - Add domain
   - Update DNS records

### Update Backend CORS

Add your domain to allowed origins in `backend/main.py`:
```python
allow_origins=[
    "https://tvetquiz.rw",
    "https://tvet-quiz.pages.dev",
    ...
]
```

---

## 🔧 TROUBLESHOOTING

### Backend Issues

**Problem:** Backend not starting
```bash
# Check Render logs
# Go to: Render Dashboard → tvet-quiz-backend → Logs
```

**Problem:** Database connection failed
```bash
# Verify DATABASE_URL in environment variables
# Check PostgreSQL is running
```

### Frontend Issues

**Problem:** API calls failing
```bash
# Check VITE_API_BASE is set correctly
# Verify CORS is enabled in backend
# Check browser console for errors
```

**Problem:** Build failing
```bash
# Check Cloudflare Pages build logs
# Verify Node version is 18
# Check all dependencies are installed
```

---

## 📱 ACCESSING FROM EDNET

### Students Access:

1. Connect to EdNet WiFi
2. Open browser
3. Go to: `https://tvet-quiz.pages.dev`
4. Login with credentials

### Data Usage:

- Login: ~5 KB
- Quiz: ~10-20 KB
- Total per student: ~20 KB
- 60 students: ~1.2 MB per quiz

**Even slow EdNet can handle this!**

---

## 🎉 DEPLOYMENT CHECKLIST

- [ ] GitHub repository updated
- [ ] Render account created
- [ ] PostgreSQL database created
- [ ] Backend deployed to Render
- [ ] Cloudflare account created
- [ ] Frontend deployed to Cloudflare Pages
- [ ] GitHub secrets configured
- [ ] CORS enabled in backend
- [ ] Environment variables set
- [ ] Database initialized
- [ ] Admin login tested
- [ ] Student login tested
- [ ] Quiz creation tested
- [ ] Quiz taking tested

---

## 🚀 QUICK START COMMANDS

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Deploy Updates

```bash
# Commit and push
git add .
git commit -m "Update feature"
git push origin main

# Auto-deploys via GitHub Actions!
```

---

## 📞 SUPPORT URLS

- **Render Dashboard:** https://dashboard.render.com
- **Cloudflare Dashboard:** https://dash.cloudflare.com
- **GitHub Actions:** https://github.com/Leonardus437/Morning_Quiz/actions
- **Backend API Docs:** https://tvet-quiz-backend.onrender.com/docs

---

## 💰 COST SUMMARY

| Service | Plan | Cost |
|---------|------|------|
| Render Backend | Free | $0/month |
| Render PostgreSQL | Free | $0/month |
| Cloudflare Pages | Free | $0/month |
| GitHub | Free | $0/month |
| **TOTAL** | | **$0/month** |

**100% FREE deployment!** 🎉

---

## 🎯 NEXT STEPS

1. **Follow Step 1-8** above
2. **Test with students** on EdNet
3. **Monitor performance** in dashboards
4. **Scale up** if needed (paid plans)

**Your system will be live in ~30 minutes!** 🚀
