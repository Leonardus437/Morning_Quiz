# BACKEND KEEP-ALIVE SOLUTIONS

## ✅ SOLUTION 1: UptimeRobot (EASIEST - 2 MINUTES)

### Setup:
1. Go to: **https://uptimerobot.com/signUp**
2. Sign up (FREE forever)
3. Click **"+ Add New Monitor"**
4. Fill in:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** TVET Quiz Backend
   - **URL (or IP):** `https://tvet-quiz-backend.onrender.com/health`
   - **Monitoring Interval:** 5 minutes
5. Click **"Create Monitor"**

**Done!** Your backend will be pinged every 5 minutes and never sleep.

---

## ✅ SOLUTION 2: Cron-Job.org (Alternative)

### Setup:
1. Go to: **https://cron-job.org/en/signup.php**
2. Sign up (FREE)
3. Click **"Cronjobs"** → **"Create cronjob"**
4. Fill in:
   - **Title:** Keep TVET Backend Awake
   - **Address:** `https://tvet-quiz-backend.onrender.com/health`
   - **Schedule:** `*/10 * * * *` (every 10 minutes)
5. Click **"Create cronjob"**

**Done!** Backend pinged every 10 minutes.

---

## ✅ SOLUTION 3: EasyCron (Alternative)

### Setup:
1. Go to: **https://www.easycron.com/user/register**
2. Sign up (FREE - 20 cron jobs)
3. Click **"+ Cron Job"**
4. Fill in:
   - **URL:** `https://tvet-quiz-backend.onrender.com/health`
   - **Cron Expression:** `*/10 * * * *`
   - **Name:** TVET Backend Keep-Alive
5. Click **"Create"**

---

## 🎯 RECOMMENDED SETUP

**Use UptimeRobot** - It's the easiest and most reliable:
- ✅ FREE forever
- ✅ Pings every 5 minutes
- ✅ Email alerts if backend goes down
- ✅ No coding needed
- ✅ 2-minute setup

---

## 📊 Monitoring Dashboard

After setup, you can:
- View uptime statistics
- Get email/SMS alerts on downtime
- See response times
- Monitor from multiple locations

---

## ⚡ Quick Test

After setting up, test your backend:
```
https://tvet-quiz-backend.onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "Morning Quiz API",
  "version": "1.2"
}
```

---

## 🔥 FASTEST SETUP (30 SECONDS)

1. Open: https://uptimerobot.com/signUp
2. Enter email, create password
3. Verify email
4. Click "+ Add New Monitor"
5. Paste URL: `https://tvet-quiz-backend.onrender.com/health`
6. Click "Create Monitor"

**DONE!** Backend will never sleep again! 🎉
