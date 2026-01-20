# Keep Render Backend Awake - Setup Guide

## Solution 1: GitHub Actions (Already Configured ✅)
The `.github/workflows/keep-alive.yml` file pings your backend every 10 minutes automatically.

**Status:** Active once you push to GitHub

---

## Solution 2: UptimeRobot (FREE - Recommended)

### Setup Steps:

1. **Go to UptimeRobot**
   - Visit: https://uptimerobot.com
   - Click "Sign Up" (100% FREE)

2. **Create Monitor**
   - Click "+ Add New Monitor"
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** TVET Quiz Backend
   - **URL:** `https://tvet-quiz-backend.onrender.com/health`
   - **Monitoring Interval:** 5 minutes (FREE tier)
   - Click "Create Monitor"

3. **Done!**
   - UptimeRobot will ping your backend every 5 minutes
   - You'll get email alerts if backend goes down
   - Keeps Render awake 24/7

**Benefits:**
- ✅ FREE forever
- ✅ Pings every 5 minutes
- ✅ Email alerts on downtime
- ✅ No coding required
- ✅ Works even if GitHub Actions fails

---

## Solution 3: Cron-Job.org (Alternative)

1. **Go to Cron-Job.org**
   - Visit: https://cron-job.org
   - Sign up (FREE)

2. **Create Cronjob**
   - Click "Create cronjob"
   - **Title:** Keep TVET Backend Awake
   - **URL:** `https://tvet-quiz-backend.onrender.com/health`
   - **Schedule:** Every 10 minutes
   - Click "Create"

---

## Solution 4: Frontend Auto-Ping (Backup)

The frontend already pings the backend when students/teachers login, providing additional keep-alive functionality.

---

## Recommended Setup

**Use ALL THREE for maximum reliability:**

1. ✅ **GitHub Actions** - Pings every 10 minutes (already configured)
2. ✅ **UptimeRobot** - Pings every 5 minutes + monitoring (setup in 2 minutes)
3. ✅ **Frontend** - Pings on user activity (already working)

This ensures your backend NEVER sleeps!

---

## Quick UptimeRobot Setup (2 minutes)

```
1. Go to: https://uptimerobot.com/signUp
2. Verify email
3. Click "+ Add New Monitor"
4. Fill in:
   - Type: HTTP(s)
   - Name: TVET Quiz Backend
   - URL: https://tvet-quiz-backend.onrender.com/health
   - Interval: 5 minutes
5. Click "Create Monitor"
6. Done! ✅
```

Your backend will now stay awake 24/7 for FREE!
