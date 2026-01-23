#!/bin/bash

echo "🚀 Deploying TVET Quiz System with Chat to Production..."

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm run build
cd ..

# Deploy to Cloudflare Pages
echo "☁️ Deploying to Cloudflare Pages..."
npx wrangler pages deploy frontend/build --project-name=tsskwizi

# The backend is already deployed to Render at:
# https://tvet-quiz-backend.onrender.com

echo "✅ Deployment complete!"
echo "🌐 Frontend: https://tsskwizi.pages.dev"
echo "🔧 Backend: https://tvet-quiz-backend.onrender.com"
echo ""
echo "💬 Chat system is now live with:"
echo "- SimpleChatButton (always visible)"
echo "- TestChatButton (for debugging)"
echo "- Status indicators"
echo "- Full chat functionality"