# DEPLOYMENT TROUBLESHOOTING GUIDE

## Issue: Cloudflare Deployment Failed
**Error:** "Unknown internal error occurred"
**Status:** Failed at 7:49AM January 26, 2026

---

## QUICK FIX OPTIONS

### Option 1: Retry Deployment (RECOMMENDED)
```bash
RETRY_DEPLOYMENT.bat
```
- Cleans previous build
- Rebuilds fresh
- Retries deployment 3 times with delays
- Most likely to succeed

### Option 2: Deploy via Git Push
```bash
DEPLOY_VIA_GIT.bat
```
- Commits changes to Git
- Pushes to GitHub
- Cloudflare auto-deploys from GitHub
- More reliable for large deployments

### Option 3: Run Diagnostics First
```bash
DIAGNOSE_DEPLOYMENT.bat
```
- Checks all dependencies
- Verifies authentication
- Identifies specific issues
- Provides targeted solutions

---

## COMMON CAUSES & SOLUTIONS

### 1. Cloudflare Internal Error (Most Common)
**Cause:** Temporary Cloudflare service issue
**Solution:** 
- Wait 5-10 minutes
- Run `RETRY_DEPLOYMENT.bat`
- Check https://www.cloudflarestatus.com/

### 2. Authentication Issue
**Cause:** Wrangler not authenticated
**Solution:**
```bash
cd frontend
npx wrangler login
```
Then retry deployment

### 3. Build Size Too Large
**Cause:** Build exceeds Cloudflare limits
**Solution:**
- Check build size: `dir frontend\build`
- If > 25MB, optimize assets
- Remove unused dependencies

### 4. Function Deployment Error
**Cause:** Cloudflare Functions configuration issue
**Solution:**
- Check `frontend/functions` directory
- Verify function syntax
- Or disable functions temporarily

### 5. Network/Timeout Issue
**Cause:** Slow connection during upload
**Solution:**
- Use Git-based deployment instead
- Run `DEPLOY_VIA_GIT.bat`

---

## MANUAL DEPLOYMENT STEPS

If all automated methods fail:

1. **Build locally:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Login to Cloudflare Dashboard:**
   - Go to: https://dash.cloudflare.com/
   - Navigate to: Pages > tsskwizi

3. **Manual Upload:**
   - Click "Create deployment"
   - Upload `frontend/build` folder
   - Wait for deployment

---

## VERIFICATION AFTER DEPLOYMENT

Once deployment succeeds:

1. **Check deployment status:**
   - https://dash.cloudflare.com/ → Pages → tsskwizi

2. **Test the fixes:**
   - Go to: https://tsskwizi.pages.dev/teacher
   - Login: teacher001 / teacher123
   - Verify "My Questions" button appears
   - Logout and re-login (should work without 401 errors)

3. **Check browser console:**
   - Press F12
   - Look for any errors
   - Token should persist after re-login

---

## WHAT WAS FIXED

### 1. Token Expiration Issue
- **File:** `frontend/src/lib/api.js`
- **Fix:** Token syncs from localStorage before every request
- **Result:** No more 401 errors after re-login

### 2. Missing "My Questions" Button
- **File:** `frontend/src/routes/teacher/+page.svelte`
- **Fix:** Added button to main navigation
- **Result:** Easy access to all your questions

---

## NEED HELP?

If deployment still fails after trying all options:

1. **Check Cloudflare Status:**
   - https://www.cloudflarestatus.com/

2. **Check Build Logs:**
   - Look for specific error messages
   - Share error details for targeted help

3. **Alternative: Use Local Development:**
   ```bash
   cd frontend
   npm run dev
   ```
   - Test fixes locally first
   - Deploy when Cloudflare is stable

---

## DEPLOYMENT SCRIPTS SUMMARY

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `RETRY_DEPLOYMENT.bat` | Retry with clean build | First attempt after failure |
| `DEPLOY_VIA_GIT.bat` | Deploy via GitHub | If direct deploy fails |
| `DIAGNOSE_DEPLOYMENT.bat` | Check configuration | Before any deployment |
| `DEPLOY_FIXES.bat` | Standard deployment | When everything works |

---

## SUCCESS INDICATORS

✅ Deployment succeeded when you see:
- "Deployment successful" message
- New deployment in Cloudflare dashboard
- Changes visible at https://tsskwizi.pages.dev/teacher
- "My Questions" button in navigation
- No 401 errors after re-login

---

**Last Updated:** January 26, 2026
**Status:** Fixes ready, awaiting successful deployment
