# 🚀 DEPLOY TO tsskwizi.pages.dev - START HERE

## What You Need (5 minutes setup)

1. **GitHub Account** - https://github.com/signup (FREE)
2. **Cloudflare Account** - https://dash.cloudflare.com/sign-up (FREE)
3. **Git Installed** - https://git-scm.com/download/win
4. **Node.js Installed** - https://nodejs.org (version 18+)

## Quick Deploy (3 Simple Steps)

### Step 1: Setup Git & Push to GitHub
```cmd
GIT_SETUP.bat
```
Then:
```cmd
PUSH_TO_GITHUB.bat
```
Enter your GitHub repository URL when prompted.

### Step 2: Connect Cloudflare Pages
1. Go to https://dash.cloudflare.com
2. **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
3. Select your GitHub repository
4. Project name: `tsskwizi`
5. Build command: `cd frontend && npm install && npm run build`
6. Build output: `frontend/build`
7. Add environment variable: `VITE_API_BASE` = `https://tvet-quiz-backend.onrender.com`
8. Click **Save and Deploy**

### Step 3: Done! 🎉
Your site is live at: **https://tsskwizi.pages.dev**

## Files You Need to Know

- **DEPLOYMENT_CHECKLIST.md** - Complete step-by-step guide with screenshots
- **GIT_SETUP.bat** - Run this first to setup Git
- **PUSH_TO_GITHUB.bat** - Run this to upload code to GitHub
- **DEPLOY_TO_CLOUDFLARE.bat** - Alternative manual deployment

## Need Help?

1. Read **DEPLOYMENT_CHECKLIST.md** for detailed instructions
2. Read **GITHUB_CLOUDFLARE_DEPLOYMENT.md** for troubleshooting
3. Read **DEPLOY_QUICK_START.md** for quick reference

## What Happens After Deployment?

Every time you make changes and push to GitHub:
```cmd
git add .
git commit -m "My changes"
git push
```

Your site automatically updates at https://tsskwizi.pages.dev (takes 2-3 minutes)

## Backend Deployment

Your frontend needs a backend API. See **DEPLOYMENT_CHECKLIST.md** section "Backend Deployment" for instructions to deploy backend to Render.com (FREE).

## Cost

- Cloudflare Pages: **FREE** ✅
- GitHub: **FREE** ✅
- Render.com (backend): **FREE tier available** ✅

Total: **$0/month**

## Start Now!

1. Run `GIT_SETUP.bat`
2. Run `PUSH_TO_GITHUB.bat`
3. Follow Step 2 above
4. Your site is LIVE!

Good luck! 🚀
