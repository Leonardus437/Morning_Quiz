# 🚀 Deploy to Production

## System Architecture
- **Backend**: Render.com (FastAPI + PostgreSQL)
- **Frontend**: Cloudflare Pages (SvelteKit)
- **Repository**: https://github.com/Leonardus437/Morning_Quiz

## Quick Deploy (3 Commands)

```cmd
git add .
git commit -m "Deploy to production"
git push origin main
cd frontend && npm install && npm run build && npx wrangler pages deploy build --project-name=tsskwizi
```

## Step-by-Step Deployment

### 1️⃣ Backend Deployment (Render.com)

#### A. Create PostgreSQL Database
1. Go to https://render.com/dashboard
2. Click **New** → **PostgreSQL**
3. Configure:
   - Name: `tvet-quiz-db`
   - Database: `tvet_quiz`
   - User: `tvet_quiz_user`
   - Region: Frankfurt (or closest to you)
   - Plan: **Free**
4. Click **Create Database**
5. **Copy the Internal Database URL** (starts with `postgresql://`)

#### B. Deploy Backend Service
1. Click **New** → **Web Service**
2. Connect to GitHub: `Leonardus437/Morning_Quiz`
3. Configure:
   - **Name**: `tvet-quiz-backend`
   - **Region**: Frankfurt
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `DATABASE_URL` = [Paste Internal Database URL from step A]
   - `SECRET_KEY` = `tvet-quiz-secret-key-2025-change-this`
   - `PYTHON_VERSION` = `3.11.0`
5. Click **Create Web Service**
6. Wait 5-10 minutes for deployment
7. **Copy your backend URL** (e.g., `https://tvet-quiz-backend.onrender.com`)

### 2️⃣ Frontend Deployment (Cloudflare Pages via Wrangler)

#### A. Install Wrangler CLI (First Time Only)
```cmd
npm install -g wrangler
wrangler login
```

#### B. Update Frontend Environment
Edit `frontend/.env.production`:
```
VITE_API_BASE=https://tvet-quiz-backend.onrender.com
```
(Replace with your actual Render backend URL)

#### C. Build and Deploy
```cmd
cd frontend
npm install
npm run build
npx wrangler pages deploy build --project-name=tsskwizi
```

#### D. Access Your Site
Your site is live at: **https://tsskwizi.pages.dev**

### 3️⃣ Push to GitHub

```cmd
git add .
git commit -m "Production deployment"
git push origin main
```

## Environment Variables

### Backend (Render.com)
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key-here
PYTHON_VERSION=3.11.0
```

### Frontend (Cloudflare Pages)
```
VITE_API_BASE=https://tvet-quiz-backend.onrender.com
NODE_VERSION=18
```

## Automated Deployment

### Option 1: Use Batch File
```cmd
DEPLOY_NOW.bat
```

### Option 2: Manual Commands
```cmd
REM Push to GitHub
git add .
git commit -m "Update"
git push origin main

REM Deploy frontend
cd frontend
npm run build
npx wrangler pages deploy build --project-name=tsskwizi
```

## Verify Deployment

### Backend Health Check
```
https://tvet-quiz-backend.onrender.com/health
```
Should return:
```json
{
  "status": "healthy",
  "service": "Morning Quiz API",
  "version": "2.0-ANTI-CHEAT-PROD"
}
```

### Frontend Check
```
https://tsskwizi.pages.dev
```
Should load the quiz homepage.

### Test Login
- Teacher: `teacher001` / `teacher123`
- Student: `student001` / `pass123`

## Troubleshooting

### Backend Issues

**"Application failed to respond"**
- Check Render logs: Dashboard → Your Service → Logs
- Verify DATABASE_URL is correct
- Check if all dependencies installed

**Database connection error**
- Verify DATABASE_URL format: `postgresql://user:pass@host:5432/dbname`
- Check database is running
- Use Internal Database URL (not External)

**CORS errors**
- Backend `main.py` already configured for `tsskwizi.pages.dev`
- If using custom domain, add it to CORS origins

### Frontend Issues

**Build fails**
- Check Node.js version: `node --version` (should be 18+)
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

**API connection fails**
- Verify `VITE_API_BASE` in `.env.production`
- Check backend is running
- Open browser console (F12) for errors

**Wrangler login fails**
- Run `wrangler logout` then `wrangler login` again
- Check internet connection
- Try different browser

### GitHub Issues

**Push rejected**
```cmd
git pull origin main --rebase
git push origin main
```

**Authentication failed**
- Use Personal Access Token instead of password
- GitHub Settings → Developer settings → Personal access tokens

## Update Deployment

### Update Backend
1. Make changes to `backend/` files
2. Push to GitHub:
   ```cmd
   git add .
   git commit -m "Update backend"
   git push origin main
   ```
3. Render auto-deploys from GitHub (takes 2-5 minutes)

### Update Frontend
1. Make changes to `frontend/` files
2. Build and deploy:
   ```cmd
   cd frontend
   npm run build
   npx wrangler pages deploy build --project-name=tsskwizi
   ```

## Production URLs

- **Frontend**: https://tsskwizi.pages.dev
- **Backend API**: https://tvet-quiz-backend.onrender.com
- **GitHub Repo**: https://github.com/Leonardus437/Morning_Quiz
- **Render Dashboard**: https://dashboard.render.com

## Cost

- **Render Free Tier**:
  - Web Service: Free (spins down after 15 min inactivity)
  - PostgreSQL: Free (1GB storage)
- **Cloudflare Pages**: Free (unlimited deployments)
- **GitHub**: Free

**Total: $0/month** 🎉

## Important Notes

1. **Render Free Tier**: Backend spins down after 15 minutes of inactivity. First request after spin-down takes 30-60 seconds.

2. **Database Backups**: Free tier doesn't include automatic backups. Export data regularly:
   ```
   Render Dashboard → Database → Backups → Create Backup
   ```

3. **Custom Domain**: 
   - Cloudflare Pages: Settings → Custom domains → Add domain
   - Render: Settings → Custom domain → Add domain

4. **Monitoring**:
   - Render: Dashboard → Metrics
   - Cloudflare: Analytics → Web Analytics

## Support

- **Render Docs**: https://render.com/docs
- **Wrangler Docs**: https://developers.cloudflare.com/workers/wrangler/
- **GitHub Issues**: https://github.com/Leonardus437/Morning_Quiz/issues

## Success Checklist

- [ ] PostgreSQL database created on Render
- [ ] Backend deployed to Render
- [ ] Backend health check returns 200 OK
- [ ] Frontend built successfully
- [ ] Frontend deployed to Cloudflare Pages
- [ ] Site accessible at tsskwizi.pages.dev
- [ ] Login works (teacher001/teacher123)
- [ ] API calls work (check browser console)
- [ ] Code pushed to GitHub

Your TVET Quiz System is now LIVE! 🎉
