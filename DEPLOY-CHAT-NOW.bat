@echo off
echo 🚀 Force Deploying Chat System to Production...

echo 📝 Adding all changes to git...
git add .
git commit -m "Add complete chat system with visible buttons and debug tools"

echo 🌐 Pushing to GitHub (triggers Cloudflare deployment)...
git push origin main

echo 📦 Building frontend locally...
cd frontend
call npm run build
cd ..

echo ☁️ Direct deploy to Cloudflare Pages...
call npx wrangler pages deploy frontend/build --project-name=tsskwizi

echo ✅ Deployment complete!
echo 🌐 Check: https://tsskwizi.pages.dev
echo 💬 Chat button should now be visible in bottom-right corner
echo 🔍 Look for blue chat button (💬) and yellow debug button (🔍)
echo ✅/❌ Status indicator shows login state

pause