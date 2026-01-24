# 🚀 Quick Deploy to tsskwizi.pages.dev

## Option 1: Automatic Deployment (Recommended)

### Prerequisites
- GitHub account
- Cloudflare account (free)

### Steps

1. **Push to GitHub**
   ```cmd
   PUSH_TO_GITHUB.bat
   ```
   - Enter your GitHub repository URL when prompted
   - Example: `https://github.com/YOUR_USERNAME/tvet-quiz-system.git`

2. **Setup Cloudflare Pages**
   - Go to https://dash.cloudflare.com
   - Click **Workers & Pages** → **Create** → **Pages** → **Connect to Git**
   - Select your GitHub repository
   - Configure:
     - Project name: `tsskwizi`
     - Build command: `cd frontend && npm install && npm run build`
     - Build output: `frontend/build`
     - Environment variable: `VITE_API_BASE` = `https://tvet-quiz-backend.onrender.com`
   - Click **Save and Deploy**

3. **Done!** Your site is live at `https://tsskwizi.pages.dev`

## Option 2: Manual Deployment

### Prerequisites
- Node.js installed
- Cloudflare account

### Steps

1. **Login to Cloudflare**
   ```cmd
   cd frontend
   npx wrangler login
   ```

2. **Deploy**
   ```cmd
   DEPLOY_TO_CLOUDFLARE.bat
   ```

3. **Done!** Your site is live at `https://tsskwizi.pages.dev`

## Backend Deployment (Required)

Your frontend needs a backend API. Deploy backend to Render.com:

1. Go to https://render.com
2. Create **New** → **Web Service**
3. Connect GitHub repository
4. Configure:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `DATABASE_URL` (PostgreSQL connection string)
   - `SECRET_KEY` (random string)
6. Deploy

Update frontend environment variable `VITE_API_BASE` with your Render backend URL.

## Troubleshooting

**"git not found"**
- Install Git: https://git-scm.com/download/win

**"npm not found"**
- Install Node.js: https://nodejs.org

**"wrangler not found"**
- Run: `npm install -g wrangler`

**Build fails**
- Check Node.js version: `node --version` (should be 18+)
- Delete `frontend/node_modules` and run `npm install` again

**Site loads but API fails**
- Verify backend is deployed and running
- Check `VITE_API_BASE` environment variable
- Check browser console for errors

## Files Created

- `.github/workflows/deploy.yml` - Auto-deployment workflow
- `frontend/.env.production` - Production environment variables
- `PUSH_TO_GITHUB.bat` - Easy GitHub push
- `DEPLOY_TO_CLOUDFLARE.bat` - Manual deployment
- `GITHUB_CLOUDFLARE_DEPLOYMENT.md` - Detailed guide

## Next Steps After Deployment

1. Test your site at `https://tsskwizi.pages.dev`
2. Login with default credentials: `teacher001` / `teacher123`
3. Upload students and create quizzes
4. Share the URL with students

## Support

See `GITHUB_CLOUDFLARE_DEPLOYMENT.md` for detailed instructions.
