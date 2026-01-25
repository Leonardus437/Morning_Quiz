# 🚀 Deploy TVET Quiz Backend to Render

## Quick Deployment Steps

### 1. Create Render Account
- Go to https://render.com
- Sign up with your GitHub account
- Connect your GitHub account

### 2. Deploy Backend
1. Click "New +" → "Web Service"
2. Connect your GitHub repository: `Leonardus437/Morning_Quiz`
3. Configure the service:
   - **Name**: `tvet-quiz-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Environment Variables
Add these environment variables in Render dashboard:
- `DATABASE_URL`: `sqlite:///quiz.db`
- `SECRET_KEY`: (Generate a random string or let Render auto-generate)

### 4. Deploy
- Click "Create Web Service"
- Wait for deployment (5-10 minutes)
- Your backend will be available at: `https://tvet-quiz-backend.onrender.com`

### 5. Test Deployment
Visit: `https://tvet-quiz-backend.onrender.com/health`
You should see: `{"status": "healthy", ...}`

## ✅ After Deployment

Your frontend at https://tsskwizi.pages.dev will automatically connect to the deployed backend!

### Default Login Credentials
- **Teacher**: `teacher001` / `teacher123`
- **Student**: `student001` / `pass123`
- **Admin**: `admin` / `admin123`

## 🔧 Troubleshooting

If deployment fails:
1. Check build logs in Render dashboard
2. Ensure all dependencies are in requirements.txt
3. Verify Python version compatibility

## 📊 Features Available
- ✅ All 12 advanced question types
- ✅ Real-time quiz system
- ✅ Teacher dashboard
- ✅ Student progress tracking
- ✅ PDF/Excel exports
- ✅ Chat system
- ✅ Offline-first design

Your TVET Quiz System will be fully functional once deployed! 🎉