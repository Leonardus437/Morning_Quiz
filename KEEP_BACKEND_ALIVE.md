# Keep Backend Alive - Render Free Tier

Your backend on Render free tier sleeps after 15 minutes of inactivity. Here are 3 solutions:

## ✅ Solution 1: UptimeRobot (Recommended - 100% Free)

**Setup (2 minutes):**

1. Go to https://uptimerobot.com
2. Sign up for FREE account
3. Click "Add New Monitor"
4. Configure:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** TVET Quiz Backend
   - **URL:** `https://tvet-quiz-backend.onrender.com/health`
   - **Monitoring Interval:** 5 minutes (free tier)
   - Click "Create Monitor"

**Done!** UptimeRobot will ping your backend every 5 minutes, keeping it awake.

---

## ✅ Solution 2: Cron-Job.org (Free Alternative)

1. Go to https://cron-job.org
2. Sign up FREE
3. Create new cron job:
   - **URL:** `https://tvet-quiz-backend.onrender.com/health`
   - **Interval:** Every 5 minutes
   - **Method:** GET

---

## ✅ Solution 3: Cloudflare Worker (Advanced)

Deploy the worker below to ping your backend every 2 minutes.

**File:** `keep-alive-worker.js` (already created in this folder)

**Deploy:**
```bash
npx wrangler deploy keep-alive-worker.js
```

---

## 🎯 Best Practice: Use UptimeRobot

**Why?**
- ✅ 100% Free forever
- ✅ No coding needed
- ✅ Email alerts if backend goes down
- ✅ 50 monitors on free plan
- ✅ 5-minute intervals (perfect for Render)
- ✅ Status page included

**Render Free Tier:** Sleeps after 15 minutes → UptimeRobot pings every 5 minutes → Backend stays awake!

---

## 📊 Monitor Multiple Endpoints

Add these monitors to UptimeRobot:

1. **Health Check:** `https://tvet-quiz-backend.onrender.com/health`
2. **API Status:** `https://tvet-quiz-backend.onrender.com/`
3. **Chat API:** `https://tvet-quiz-backend.onrender.com/chat/rooms`

---

## ⚠️ Important Notes

- Render free tier has **750 hours/month** limit
- With keep-alive: Uses ~720 hours/month (30 days × 24 hours)
- **You're safe!** Still within free tier limits
- Backend will restart if it crashes (automatic)

---

## 🚀 Quick Start (30 seconds)

1. Open https://uptimerobot.com/signUp
2. Verify email
3. Add monitor: `https://tvet-quiz-backend.onrender.com/health`
4. Set interval: 5 minutes
5. Done! ✅

Your backend will now stay awake 24/7 for FREE!
