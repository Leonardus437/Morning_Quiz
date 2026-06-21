# Railway Environment Variables Template

## 🔧 Required Variables (Backend Service)

Copy these to: **Railway → Backend Service → Variables Tab**

### 1. Database Connection (CRITICAL)
```bash
DATABASE_URL=postgresql://postgres:password@host:port/database
```
**How to get:**
1. Railway → PostgreSQL service → "Variables" tab
2. Copy the full `DATABASE_URL` value
3. Paste exactly as-is (starts with `postgresql://`)

**Common Issues:**
- ❌ Wrong: `postgres://...` (missing 'ql')
- ❌ Wrong: `localhost` (won't work on Railway)
- ✅ Correct: Full URL from Railway PostgreSQL service

---

### 2. Security Key (REQUIRED)
```bash
SECRET_KEY=your-secret-key-here
```
**Options:**

**For Testing (NOT recommended for production):**
```bash
SECRET_KEY=tvet-quiz-secret-2024
```

**For Production (Recommended):**
Generate random key:
```bash
# Run in terminal:
python -c "import secrets; print(secrets.token_hex(32))"

# Then use output:
SECRET_KEY=a1b2c3d4e5f6... (64 characters)
```

**What it does:**
- Encrypts JWT authentication tokens
- Keeps user sessions secure
- Prevents token forgery

---

### 3. Offline Mode (REQUIRED)
```bash
OFFLINE_MODE=false
```
**Options:**
- `false` = Use PostgreSQL (Railway deployment) ✅
- `true` = Use SQLite (local offline mode only)

**For Railway: ALWAYS USE `false`**

---

### 4. Port (OPTIONAL - Railway sets automatically)
```bash
PORT=8000
```
**Note:**
- Railway automatically sets this
- You can add it manually, but not required
- Backend uses Railway's provided PORT if available

---

## 🔐 Optional Security Variables

### 5. JWT Algorithm
```bash
ALGORITHM=HS256
```
**Default:** HS256 (already set in code)
**Only add if:** You want to use different algorithm

---

### 6. Token Expiration
```bash
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```
**Values:**
- `30` = 30 minutes (strict security)
- `480` = 8 hours (school day)
- `1440` = 24 hours (recommended for TVET)
- `10080` = 7 days (very permissive)

**Default:** 30 minutes (if not set)

---

## 📊 PostgreSQL Service Variables

**Railway creates these automatically - DO NOT MODIFY:**

```bash
# These are set by Railway PostgreSQL service:
PGHOST=xxxxx.railway.internal
PGPORT=5432
PGUSER=postgres
PGPASSWORD=xxxxx
PGDATABASE=railway
DATABASE_URL=postgresql://postgres:xxxxx@xxxxx.railway.internal:5432/railway
```

**Just copy `DATABASE_URL` to backend service variables.**

---

## 🌐 Frontend Environment Variables (Cloudflare)

Copy these to: **Cloudflare Pages → tsskwizi → Settings → Environment Variables**

### 1. API Base URL (REQUIRED)
```bash
VITE_API_BASE=https://your-backend.up.railway.app
```

**How to get:**
1. Railway → Backend service → "Settings" → "Networking"
2. Look for "Public Domain"
3. Copy the full URL
4. Paste in Cloudflare (NO trailing slash!)

**Common Issues:**
- ❌ Wrong: `http://...` (must be https)
- ❌ Wrong: `https://.../` (no trailing slash)
- ❌ Wrong: Old Railway URL (if you recreated project)
- ✅ Correct: `https://morning-quiz.up.railway.app`

---

## 📋 Complete Setup Example

### Railway Backend Variables:
```bash
DATABASE_URL=postgresql://postgres:abc123xyz@morning-quiz-db.railway.internal:5432/railway
SECRET_KEY=tvet-quiz-secret-key-2024-production
OFFLINE_MODE=false
PORT=8000
```

### Cloudflare Frontend Variables:
```bash
VITE_API_BASE=https://morning-quiz.up.railway.app
```

---

## ✅ Verification Checklist

After setting variables, verify:

### Railway Backend:
- [ ] Go to "Variables" tab
- [ ] See `DATABASE_URL` (starts with `postgresql://`)
- [ ] See `SECRET_KEY` (at least 16 characters)
- [ ] See `OFFLINE_MODE=false`
- [ ] Click "Redeploy" (if changes made)

### Cloudflare Frontend:
- [ ] Go to "Settings" → "Environment variables"
- [ ] See `VITE_API_BASE` (starts with `https://`)
- [ ] No trailing slash
- [ ] Matches Railway backend domain
- [ ] Go to "Deployments" → "Retry deployment"

### Test:
- [ ] Backend: `https://your-backend.up.railway.app/health`
- [ ] Frontend: `https://tsskwizi.pages.dev` (login works)

---

## 🔄 Updating Variables

### To Change a Variable:

**Railway:**
1. Railway → Backend → "Variables"
2. Find variable → Click "..." → "Edit"
3. Update value → Save
4. Backend automatically restarts

**Cloudflare:**
1. Cloudflare → Pages → Settings → Environment variables
2. Find variable → Click "Edit"
3. Update value → Save
4. Go to "Deployments" → "Retry deployment"

---

## 🛡️ Security Best Practices

### 1. Change Default Passwords
After first deployment:
```bash
# In the app (not environment variables):
- Admin: admin → Change password in dashboard
- Teacher: teacher001 → Change password in dashboard
```

### 2. Use Strong SECRET_KEY
```bash
# Generate new key:
python -c "import secrets; print(secrets.token_hex(32))"

# Update in Railway:
SECRET_KEY=<new random value>
```

### 3. Rotate Keys Regularly
```bash
# Every 3-6 months:
1. Generate new SECRET_KEY
2. Update in Railway variables
3. All users will need to login again (normal)
```

### 4. Monitor Access
```bash
# Check logs regularly:
Railway → Backend → "Deployments" → Latest → Logs
Look for suspicious login attempts
```

---

## 🚨 Troubleshooting Variables

### Problem: "DATABASE_URL not found"
**Fix:**
1. Railway → PostgreSQL → "Variables" → Copy `DATABASE_URL`
2. Railway → Backend → "Variables" → Add `DATABASE_URL`
3. Paste full value
4. Save (backend restarts automatically)

### Problem: "Invalid token" errors
**Fix:**
1. Check `SECRET_KEY` is set
2. Make sure it's at least 16 characters
3. All users need to login again after changing

### Problem: Frontend can't connect
**Fix:**
1. Check `VITE_API_BASE` in Cloudflare
2. Must match Railway backend domain exactly
3. Redeploy Cloudflare after changing

### Problem: "OFFLINE_MODE=true" in logs
**Fix:**
1. Railway → Backend → "Variables"
2. Set `OFFLINE_MODE=false`
3. Save (backend restarts)

---

## 📝 Variable Reference

| Variable | Required? | Default | Purpose |
|----------|-----------|---------|---------|
| `DATABASE_URL` | ✅ Yes | None | PostgreSQL connection |
| `SECRET_KEY` | ✅ Yes | None | JWT encryption |
| `OFFLINE_MODE` | ✅ Yes | `false` | Database mode |
| `PORT` | ❌ No | `8000` | Railway sets this |
| `ALGORITHM` | ❌ No | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ No | `30` | Session length |

---

## 🔍 How to View Current Variables

### Railway:
```bash
1. Railway → Backend service
2. Click "Variables" tab
3. See all set variables (passwords hidden with ***)
```

### Cloudflare:
```bash
1. Cloudflare → Pages → tsskwizi
2. Settings → Environment variables
3. See all variables (can expand to view)
```

### Via Logs (Railway):
```bash
Railway → Backend → Deployments → Latest → Logs
Look for:
"📦 Database: postgresql://..." (shows DATABASE_URL is set)
"🔒 Offline mode: false" (shows OFFLINE_MODE)
```

---

## 💡 Tips

1. **Copy-Paste Carefully:**
   - Don't add extra spaces
   - Don't add quotes around values
   - Copy full URL including protocol

2. **Case Sensitive:**
   - `DATABASE_URL` not `database_url`
   - `OFFLINE_MODE` not `offline_mode`

3. **No Comments:**
   - Railway doesn't support `# comments`
   - Just paste raw values

4. **Test After Changes:**
   - Always test health endpoint after updating variables
   - Check logs for confirmation

---

## ✅ Quick Setup Commands

```bash
# 1. Get DATABASE_URL from Railway PostgreSQL
# 2. Set variables in Railway Backend:

DATABASE_URL=postgresql://... (from PostgreSQL service)
SECRET_KEY=tvet-quiz-2024-production
OFFLINE_MODE=false

# 3. Set variable in Cloudflare Pages:

VITE_API_BASE=https://your-backend.up.railway.app

# 4. Verify:
curl https://your-backend.up.railway.app/health
# Expected: {"status":"healthy"}
```

---

**Variables set correctly? Your system is ready to deploy! 🚀**
