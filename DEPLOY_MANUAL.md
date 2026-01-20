# Deploy Without Git - Manual Upload

## Frontend (Cloudflare Pages)

1. **Build locally** (if Node.js installed):
   ```
   cd frontend
   npm install
   npm run build
   ```

2. **Upload to Cloudflare:**
   - Go to: https://dash.cloudflare.com
   - Click: Pages > tsskwizi
   - Click: "Create deployment"
   - Upload folder: `frontend/build`
   - Click: "Save and Deploy"

## Backend (Render)

**Option 1: Use Render Dashboard**
1. Go to: https://dashboard.render.com
2. Click: tsskwizi-backend
3. Click: "Manual Deploy" > "Deploy latest commit"

**Option 2: Upload files directly**
1. Zip your `backend` folder
2. Go to Render dashboard
3. Create new Web Service
4. Upload zip file

## Test Deployment

- Frontend: https://tsskwizi.pages.dev
- Backend: https://tvet-quiz-backend.onrender.com/health

## Install Git (Optional)

Download: https://git-scm.com/download/win
Then you can use: `git push origin main`
