# 🚀 MANUAL DEPLOYMENT GUIDE (No Git CLI)

## ⚠️ Git Not Installed - Use GitHub Desktop Instead

Since Git command line is not available, use one of these methods:

---

## METHOD 1: GitHub Desktop (RECOMMENDED)

### Step 1: Install GitHub Desktop
1. Download: https://desktop.github.com/
2. Install and login with your GitHub account
3. Open GitHub Desktop

### Step 2: Add Repository
1. Click "File" → "Add local repository"
2. Browse to: `d:\Morning_Quiz-master`
3. Click "Add repository"

### Step 3: Commit and Push
1. You'll see all changed files in the left panel
2. Write commit message: "Add anti-cheating system"
3. Click "Commit to main"
4. Click "Push origin" (top right)

### Step 4: Monitor Deployment
- Cloudflare: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
- Wait 2-3 minutes for build
- Test: https://tsskwizi.pages.dev

---

## METHOD 2: Direct Upload to GitHub

### Step 1: Zip Your Files
1. Go to `d:\Morning_Quiz-master`
2. Select these folders:
   - `frontend/src/` (with anti-cheating code)
   - `backend/main.py` (with /report-cheating endpoint)
3. Create ZIP file

### Step 2: Upload to GitHub
1. Go to: https://github.com/Leonardus437/Morning_Quiz
2. Click on the file you want to update
3. Click "Edit" (pencil icon)
4. Paste new content
5. Commit changes

**Key Files to Update:**
- `frontend/src/routes/quiz/[id]/+page.svelte` (anti-cheating code)
- `backend/main.py` (cheating report endpoint)

### Step 3: Trigger Cloudflare Deploy
- Cloudflare auto-detects GitHub changes
- Or manually trigger: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi

---

## METHOD 3: Install Git CLI (For Future)

### Quick Install:
1. Download: https://git-scm.com/download/win
2. Run installer (use default settings)
3. Restart Command Prompt
4. Run: `git --version` to verify

### Then Use:
```bash
cd d:\Morning_Quiz-master
git add .
git commit -m "Add anti-cheating system"
git push origin main
```

---

## METHOD 4: Use Cloudflare Direct Upload

### Step 1: Build Frontend Locally
```bash
cd d:\Morning_Quiz-master\frontend
npm install
npm run build
```

### Step 2: Upload to Cloudflare
1. Go to: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
2. Click "Create deployment"
3. Drag and drop `frontend/build` folder
4. Wait for deployment

**Note**: This only updates frontend, not backend

---

## ✅ EASIEST SOLUTION: GitHub Desktop

**Download now**: https://desktop.github.com/

1. Install GitHub Desktop (2 minutes)
2. Add repository (1 click)
3. Commit changes (1 click)
4. Push to GitHub (1 click)
5. Cloudflare auto-deploys (2-3 minutes)

**Total time**: ~5 minutes

---

## 🎯 After Upload (Any Method)

### Monitor Deployment:
- **Cloudflare**: https://dash.cloudflare.com/86089f0bb941af81d975a82b892fe038/pages/view/tsskwizi
- **Check build logs** for errors
- **Wait 2-3 minutes** for completion

### Test Production:
- **Visit**: https://tsskwizi.pages.dev
- **Login**: teacher001 / teacher123
- **Start quiz** → Fullscreen activates
- **Try Esc** → Warning appears
- **Try tab switch** → Warning appears

---

## 🔍 Verify Backend

Backend is already deployed on Render. Test:
```
https://tvet-quiz-backend.onrender.com/health
```

Should return: `{"status":"healthy"}`

---

## 📞 Need Help?

**GitHub Desktop Tutorial**: https://docs.github.com/en/desktop

**Cloudflare Pages Docs**: https://developers.cloudflare.com/pages/

---

## 🎉 RECOMMENDED: Install GitHub Desktop Now

It's the easiest way to deploy. Download here:
👉 **https://desktop.github.com/**

Then follow METHOD 1 above.
