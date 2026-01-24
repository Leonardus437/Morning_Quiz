# 📋 Deployment Checklist for tsskwizi.pages.dev

## Pre-Deployment Checklist

- [ ] Git installed (`git --version`)
- [ ] Node.js installed (`node --version` - should be 18+)
- [ ] GitHub account created
- [ ] Cloudflare account created (free tier is fine)

## Step-by-Step Deployment

### 1️⃣ Setup Git (First Time Only)
```cmd
GIT_SETUP.bat
```
- Enter your name and email
- This configures Git on your computer

### 2️⃣ Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `tvet-quiz-system` (or your choice)
3. **Public** or **Private** (your choice)
4. **DO NOT** check any boxes (no README, no .gitignore, no license)
5. Click **Create repository**
6. Copy the repository URL (e.g., `https://github.com/YOUR_USERNAME/tvet-quiz-system.git`)

### 3️⃣ Push Code to GitHub
```cmd
PUSH_TO_GITHUB.bat
```
- Paste your GitHub repository URL when prompted
- Wait for upload to complete

### 4️⃣ Get Cloudflare Credentials

#### A. Get API Token
1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Click **Create Token**
3. Use template: **Edit Cloudflare Workers**
4. Click **Continue to summary** → **Create Token**
5. **COPY THE TOKEN** (you won't see it again!)

#### B. Get Account ID
1. Go to https://dash.cloudflare.com
2. Click **Workers & Pages** in left sidebar
3. Copy **Account ID** from the right side

### 5️⃣ Add GitHub Secrets (For Auto-Deployment)
1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add first secret:
   - Name: `CLOUDFLARE_API_TOKEN`
   - Value: [Paste your Cloudflare API Token]
   - Click **Add secret**
5. Add second secret:
   - Name: `CLOUDFLARE_ACCOUNT_ID`
   - Value: [Paste your Cloudflare Account ID]
   - Click **Add secret**

### 6️⃣ Create Cloudflare Pages Project
1. Go to https://dash.cloudflare.com
2. Click **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**
3. Click **Connect GitHub** (authorize if needed)
4. Select your repository: `tvet-quiz-system`
5. Click **Begin setup**
6. Configure build settings:
   - **Project name**: `tsskwizi`
   - **Production branch**: `main`
   - **Framework preset**: None
   - **Build command**: `cd frontend && npm install && npm run build`
   - **Build output directory**: `frontend/build`
7. Click **Environment variables (advanced)**
8. Add variable:
   - **Variable name**: `VITE_API_BASE`
   - **Value**: `https://tvet-quiz-backend.onrender.com`
9. Click **Save and Deploy**

### 7️⃣ Wait for Deployment
- First deployment takes 3-5 minutes
- Watch the build logs
- When complete, you'll see: **Success! Your site is live!**

### 8️⃣ Access Your Site
Your site is now live at: **https://tsskwizi.pages.dev**

## Backend Deployment (Required)

Your frontend needs a backend. Deploy to Render.com:

### 1️⃣ Create Render Account
- Go to https://render.com
- Sign up with GitHub

### 2️⃣ Create PostgreSQL Database
1. Click **New** → **PostgreSQL**
2. Name: `tvet-quiz-db`
3. Select **Free** tier
4. Click **Create Database**
5. **COPY** the **Internal Database URL**

### 3️⃣ Deploy Backend
1. Click **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `tvet-quiz-backend`
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `DATABASE_URL` = [Paste Internal Database URL]
   - `SECRET_KEY` = `your-secret-key-here-change-this`
5. Click **Create Web Service**

### 4️⃣ Update Frontend Environment
1. Go to Cloudflare Pages dashboard
2. Select your project: `tsskwizi`
3. Go to **Settings** → **Environment variables**
4. Edit `VITE_API_BASE`:
   - Change to your Render backend URL (e.g., `https://tvet-quiz-backend.onrender.com`)
5. Click **Save**
6. Go to **Deployments** → Click **Retry deployment** on latest deployment

## Testing Your Deployment

- [ ] Visit https://tsskwizi.pages.dev
- [ ] Homepage loads correctly
- [ ] Click "Login" - login page appears
- [ ] Try login with: `teacher001` / `teacher123`
- [ ] Teacher dashboard loads
- [ ] Try creating a quiz
- [ ] Test student login

## Automatic Updates

Now whenever you make changes:

```cmd
git add .
git commit -m "Your update description"
git push
```

GitHub Actions will automatically rebuild and deploy to Cloudflare Pages!

## Troubleshooting

### Build Fails
- Check build logs in Cloudflare dashboard
- Verify `package.json` has all dependencies
- Try manual build: `cd frontend && npm install && npm run build`

### API Connection Fails
- Verify backend is running on Render
- Check `VITE_API_BASE` environment variable
- Check browser console for errors (F12)

### GitHub Push Fails
```cmd
git config --global user.email "your.email@example.com"
git config --global user.name "Your Name"
```

### "Permission Denied" on GitHub
- Use HTTPS URL, not SSH
- Or setup SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

## Cost Breakdown

- **Cloudflare Pages**: FREE (unlimited deployments)
- **GitHub**: FREE (public/private repos)
- **Render.com**: FREE tier available (backend + database)

Total Cost: **$0/month** 🎉

## Support Files Created

- `GIT_SETUP.bat` - Initial Git configuration
- `PUSH_TO_GITHUB.bat` - Easy GitHub push
- `DEPLOY_TO_CLOUDFLARE.bat` - Manual deployment
- `GITHUB_CLOUDFLARE_DEPLOYMENT.md` - Detailed guide
- `DEPLOY_QUICK_START.md` - Quick reference
- `.github/workflows/deploy.yml` - Auto-deployment

## Success! 🎉

Your TVET Quiz System is now:
- ✅ Hosted on GitHub
- ✅ Deployed to Cloudflare Pages
- ✅ Accessible at https://tsskwizi.pages.dev
- ✅ Auto-deploys on every push
- ✅ 100% FREE hosting

Share the URL with your students and start quizzing!
