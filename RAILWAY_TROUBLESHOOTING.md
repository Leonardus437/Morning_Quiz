# Railway Backend Troubleshooting Guide

## Your backend is returning 502 Bad Gateway - Here's how to fix it:

### Step 1: Check Railway Dashboard
1. Go to: https://railway.app/dashboard
2. Find your service: `web-production-2c325`
3. Click on it
4. Go to **"Deployments"** tab
5. Check the latest deployment status

### Step 2: Check Logs
1. In Railway dashboard, click **"Logs"** tab
2. Look for errors like:
   - `ModuleNotFoundError`
   - `Connection refused`
   - `DATABASE_URL not set`
   - `Port already in use`

### Step 3: Verify Environment Variables
In Railway dashboard, go to **"Variables"** tab and ensure you have:

```
DATABASE_URL=postgresql://...  (from Railway PostgreSQL service)
SECRET_KEY=your-secret-key-here
PORT=8000  (Railway sets this automatically)
```

### Step 4: Check Build Logs
1. Go to **"Deployments"** tab
2. Click on the latest deployment
3. Check **"Build Logs"** for errors during installation

### Step 5: Common Fixes

#### Fix 1: Missing Dependencies
If logs show `ModuleNotFoundError`, your requirements.txt might be incomplete.

#### Fix 2: Database Connection
If logs show database errors:
- Make sure PostgreSQL service is running
- Verify DATABASE_URL is set correctly
- Check if database has tables (run migrations)

#### Fix 3: Port Issues
Railway automatically sets $PORT. Make sure your start command uses it:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 6: Manual Redeploy
1. In Railway dashboard
2. Click **"Redeploy"** button
3. Wait for deployment to complete (2-3 minutes)

### Step 7: If Still Not Working
Run locally to test:
```bash
cd backend
python -m uvicorn main:app --reload
```

Then check http://localhost:8000/health

---

## Quick Commands

### Test backend locally:
```bash
cd /home/leo/Documents/Morning_Quiz/backend
uvicorn main:app --reload --port 8000
```

### Test health endpoint:
```bash
curl http://localhost:8000/health
```

### Test provinces endpoint:
```bash
curl http://localhost:8000/hierarchy/provinces
```

---

## Next Steps After Fix:

1. ✅ Backend responds with 200 OK
2. ✅ CORS headers are present
3. ✅ Frontend can fetch data
4. ✅ Login works with school/trade/level dropdowns

---

**Current Status:** Backend is DOWN (502)
**Action Required:** Check Railway dashboard logs and redeploy
