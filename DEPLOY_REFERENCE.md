# 🚀 Quick Deployment Reference

## One-Command Deploy

### Deploy Frontend Only
```cmd
deploy-frontend.bat
```

### Deploy Everything
```cmd
DEPLOY_NOW.bat
```

## Manual Commands

### Push to GitHub
```cmd
git add .
git commit -m "Your message"
git push origin main
```

### Deploy Frontend (Wrangler CLI)
```cmd
cd frontend
npm install
npm run build
npx wrangler pages deploy build --project-name=tsskwizi
```

### First Time Wrangler Setup
```cmd
npm install -g wrangler
wrangler login
```

## Production URLs

| Service | URL |
|---------|-----|
| Frontend | https://tsskwizi.pages.dev |
| Backend | https://tvet-quiz-backend.onrender.com |
| GitHub | https://github.com/Leonardus437/Morning_Quiz |
| Render Dashboard | https://dashboard.render.com |
| Cloudflare Dashboard | https://dash.cloudflare.com |

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin/DOS | admin | admin123 |
| Teacher | teacher001 | teacher123 |
| Student | student001 | pass123 |

## Health Checks

### Backend
```
GET https://tvet-quiz-backend.onrender.com/health
```

### Frontend
```
https://tsskwizi.pages.dev
```

## Environment Variables

### Backend (Render.com)
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
PYTHON_VERSION=3.11.0
```

### Frontend (Cloudflare Pages)
```
VITE_API_BASE=https://tvet-quiz-backend.onrender.com
NODE_VERSION=18
```

## Common Issues

### Backend not responding
- Render free tier spins down after 15 min
- First request takes 30-60 seconds
- Check Render logs

### Frontend build fails
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Check Node.js version (need 18+)

### CORS errors
- Verify backend URL in `.env.production`
- Check backend CORS settings in `main.py`

### Wrangler auth fails
```cmd
wrangler logout
wrangler login
```

## Update Workflow

1. Make changes locally
2. Test locally: `npm run dev`
3. Commit: `git add . && git commit -m "Update"`
4. Push: `git push origin main`
5. Deploy frontend: `deploy-frontend.bat`

## Files to Know

- `backend/main.py` - Backend API
- `backend/requirements.txt` - Python dependencies
- `frontend/src/` - Frontend source code
- `frontend/.env.production` - Production config
- `render.yaml` - Render configuration
- `wrangler.toml` - Cloudflare configuration

## Support

- Full Guide: `PRODUCTION_DEPLOYMENT.md`
- GitHub Issues: https://github.com/Leonardus437/Morning_Quiz/issues
- Render Docs: https://render.com/docs
- Wrangler Docs: https://developers.cloudflare.com/workers/wrangler/
