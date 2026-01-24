# 🚀 DEPLOY YOUR TVET QUIZ SYSTEM TO tsskwizi.pages.dev

## ⚡ FASTEST WAY TO DEPLOY (5 Minutes)

### What You Need
- GitHub account (free) - https://github.com/signup
- Cloudflare account (free) - https://dash.cloudflare.com/sign-up
- Git installed - https://git-scm.com/download/win
- Node.js installed - https://nodejs.org

### 3 Simple Steps

#### 1️⃣ Setup Git (First Time Only)
Double-click: **`GIT_SETUP.bat`**
- Enter your name and email
- Done!

#### 2️⃣ Push to GitHub
Double-click: **`PUSH_TO_GITHUB.bat`**
- Create a repository on GitHub first: https://github.com/new
- Copy the repository URL
- Paste it when prompted
- Wait for upload to complete

#### 3️⃣ Deploy to Cloudflare Pages
1. Go to https://dash.cloudflare.com
2. Click **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
3. Select your GitHub repository
4. Configure:
   ```
   Project name: tsskwizi
   Build command: cd frontend && npm install && npm run build
   Build output: frontend/build
   Environment variable: VITE_API_BASE = https://tvet-quiz-backend.onrender.com
   ```
5. Click **Save and Deploy**

### ✅ Done!
Your site is live at: **https://tsskwizi.pages.dev**

---

## 📚 Need More Help?

### For Beginners
→ **`START_DEPLOYMENT_HERE.md`** - Simple overview

### For Step-by-Step Guide
→ **`DEPLOYMENT_CHECKLIST.md`** - Complete checklist with every detail

### For Visual Learners
→ **`DEPLOYMENT_VISUAL_GUIDE.md`** - Diagrams and flowcharts

### For Detailed Instructions
→ **`GITHUB_CLOUDFLARE_DEPLOYMENT.md`** - Full technical guide

---

## 🎯 What's Included?

### Batch Files (Double-click to run)
- **`GIT_SETUP.bat`** - Configure Git (run first)
- **`PUSH_TO_GITHUB.bat`** - Upload to GitHub
- **`DEPLOY_TO_CLOUDFLARE.bat`** - Manual deployment option

### Documentation
- **`START_DEPLOYMENT_HERE.md`** - Quick start
- **`DEPLOYMENT_CHECKLIST.md`** - Step-by-step guide
- **`DEPLOYMENT_VISUAL_GUIDE.md`** - Visual diagrams
- **`GITHUB_CLOUDFLARE_DEPLOYMENT.md`** - Full guide
- **`DEPLOYMENT_READY.md`** - Summary of all files

### Auto-Deployment
- **`.github/workflows/deploy.yml`** - GitHub Actions workflow
- Automatically deploys when you push to GitHub!

---

## 💰 Cost: $0/month (100% FREE)

- ✅ GitHub: Free
- ✅ Cloudflare Pages: Free (unlimited deployments)
- ✅ Render.com: Free tier for backend

---

## 🔄 Future Updates

After initial deployment, updating is super easy:

```cmd
git add .
git commit -m "My updates"
git push
```

Your site automatically updates in 2-3 minutes! 🎉

---

## 🆘 Troubleshooting

**"git not found"**
→ Install Git: https://git-scm.com/download/win

**"npm not found"**
→ Install Node.js: https://nodejs.org (version 18+)

**Build fails**
→ Check `DEPLOYMENT_CHECKLIST.md` troubleshooting section

**Need backend?**
→ See `DEPLOYMENT_CHECKLIST.md` - Backend Deployment section

---

## 📋 Quick Checklist

Before you start:
- [ ] Git installed? (`git --version`)
- [ ] Node.js installed? (`node --version`)
- [ ] GitHub account created?
- [ ] Cloudflare account created?

Ready to deploy:
- [ ] Run `GIT_SETUP.bat`
- [ ] Create GitHub repository
- [ ] Run `PUSH_TO_GITHUB.bat`
- [ ] Connect Cloudflare Pages
- [ ] Site is live! 🎉

---

## 🎊 START NOW!

1. Double-click **`GIT_SETUP.bat`**
2. Double-click **`PUSH_TO_GITHUB.bat`**
3. Follow Step 3 above

Your quiz system will be live at **https://tsskwizi.pages.dev** in minutes!

---

## 📞 Need Detailed Help?

Open any of these files for more information:
- `START_DEPLOYMENT_HERE.md` - Quick overview
- `DEPLOYMENT_CHECKLIST.md` - Complete guide
- `DEPLOYMENT_VISUAL_GUIDE.md` - Visual diagrams
- `GITHUB_CLOUDFLARE_DEPLOYMENT.md` - Technical details

---

**Ready? Let's deploy! 🚀**

Double-click `GIT_SETUP.bat` to begin!
