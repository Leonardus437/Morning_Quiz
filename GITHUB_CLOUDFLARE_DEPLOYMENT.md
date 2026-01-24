# Deploy to GitHub and Cloudflare Pages (tsskwizi.pages.dev)

## Quick Deployment Steps

### Step 1: Initialize Git Repository (if not already done)
```cmd
cd d:\Morning_Quiz-master
git init
git add .
git commit -m "Initial commit - TVET Quiz System"
```

### Step 2: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `tvet-quiz-system` (or any name you prefer)
3. Make it **Public** or **Private**
4. **DO NOT** initialize with README, .gitignore, or license
5. Click "Create repository"

### Step 3: Push to GitHub
```cmd
git remote add origin https://github.com/YOUR_USERNAME/tvet-quiz-system.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

### Step 4: Setup Cloudflare Pages

#### A. Get Cloudflare API Token
1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Click "Create Token"
3. Use template: "Edit Cloudflare Workers"
4. Or create custom token with permissions:
   - Account > Cloudflare Pages > Edit
5. Copy the token (you'll need it for GitHub Secrets)

#### B. Get Cloudflare Account ID
1. Go to https://dash.cloudflare.com
2. Select any domain or go to Workers & Pages
3. Copy your Account ID from the right sidebar

#### C. Add GitHub Secrets
1. Go to your GitHub repository
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add these secrets:
   - Name: `CLOUDFLARE_API_TOKEN`
     Value: [Your Cloudflare API Token]
   - Name: `CLOUDFLARE_ACCOUNT_ID`
     Value: [Your Cloudflare Account ID]

### Step 5: Create Cloudflare Pages Project
1. Go to https://dash.cloudflare.com
2. Click **Workers & Pages** > **Create application** > **Pages**
3. Connect to your GitHub repository
4. Configure build settings:
   - **Project name**: `tsskwizi`
   - **Production branch**: `main`
   - **Build command**: `cd frontend && npm install && npm run build`
   - **Build output directory**: `frontend/build`
   - **Root directory**: `/`
5. Add environment variable:
   - `VITE_API_BASE` = `https://tvet-quiz-backend.onrender.com`
6. Click **Save and Deploy**

### Step 6: Configure Custom Domain (Optional)
Your site will be available at: `https://tsskwizi.pages.dev`

To use a custom domain:
1. In Cloudflare Pages project settings
2. Go to **Custom domains**
3. Add your domain (e.g., `quiz.yourdomain.com`)

## Automatic Deployment

Once setup is complete, every time you push to GitHub:
```cmd
git add .
git commit -m "Your update message"
git push
```

GitHub Actions will automatically:
1. Build your frontend
2. Deploy to Cloudflare Pages
3. Your site updates at `https://tsskwizi.pages.dev`

## Manual Deployment (Alternative)

If you prefer manual deployment without GitHub Actions:

```cmd
cd d:\Morning_Quiz-master\frontend
npm install
npm run build
npx wrangler pages deploy build --project-name=tsskwizi
```

You'll need to login to Cloudflare first:
```cmd
npx wrangler login
```

## Backend Deployment (Render.com)

Your backend is already configured for Render.com. To deploy:

1. Go to https://render.com
2. Create new **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `tvet-quiz-backend`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. Add environment variables:
   - `DATABASE_URL` = [Your PostgreSQL URL]
   - `SECRET_KEY` = [Random secret key]
6. Deploy

## Troubleshooting

### Build fails on Cloudflare Pages
- Check that `frontend/package.json` has all dependencies
- Verify Node version is 18 or higher
- Check build logs in Cloudflare dashboard

### API not connecting
- Verify `VITE_API_BASE` environment variable is set correctly
- Check backend is running on Render.com
- Check CORS settings in backend `main.py`

### GitHub push fails
```cmd
git config --global user.email "your.email@example.com"
git config --global user.name "Your Name"
```

## File Structure for Deployment

```
Morning_Quiz-master/
├── .github/
│   └── workflows/
│       └── deploy.yml          # Auto-deployment workflow
├── backend/
│   ├── main.py                 # Main backend file
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # Docker config
├── frontend/
│   ├── src/                    # Source code
│   ├── static/                 # Static assets
│   ├── build/                  # Build output (generated)
│   ├── package.json            # Dependencies
│   ├── svelte.config.js        # Svelte config
│   └── .env.production         # Production env vars
├── .gitignore                  # Git ignore rules
├── wrangler.toml               # Cloudflare config
└── README.md                   # Documentation
```

## Important Notes

1. **Backend URL**: Make sure your backend is deployed and accessible at the URL specified in `VITE_API_BASE`
2. **Database**: Backend needs PostgreSQL database (use Render.com free tier or other provider)
3. **Secrets**: Never commit `.env` files with real credentials to GitHub
4. **Build Time**: First deployment may take 3-5 minutes
5. **Free Tier**: Cloudflare Pages offers unlimited free deployments

## Support

If deployment fails:
1. Check GitHub Actions logs in your repository
2. Check Cloudflare Pages deployment logs
3. Verify all secrets are correctly set
4. Ensure backend is running and accessible

## Success Checklist

- [ ] Git repository initialized
- [ ] Code pushed to GitHub
- [ ] Cloudflare API Token created
- [ ] GitHub Secrets added (CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID)
- [ ] Cloudflare Pages project created
- [ ] First deployment successful
- [ ] Site accessible at https://tsskwizi.pages.dev
- [ ] Backend deployed and accessible
- [ ] Frontend can connect to backend API

Your TVET Quiz System is now live! 🎉
