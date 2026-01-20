# 🔑 GitHub Personal Access Token - Quick Guide

## Generate Token (2 minutes)

### Step 1: Go to GitHub Settings
1. Open browser
2. Go to: **https://github.com/settings/tokens**
3. Or: GitHub → Click your profile (top right) → Settings → Developer settings → Personal access tokens → Tokens (classic)

### Step 2: Generate New Token
1. Click **"Generate new token"** → **"Generate new token (classic)"**
2. Note: `Deploy TVET Quiz System`
3. Expiration: **No expiration** (or 90 days)
4. Select scopes:
   - ✅ **repo** (Full control of private repositories)
     - ✅ repo:status
     - ✅ repo_deployment
     - ✅ public_repo
     - ✅ repo:invite
     - ✅ security_events
   - ✅ **workflow** (Update GitHub Action workflows)
5. Scroll down, click **"Generate token"**

### Step 3: Copy Token
1. **IMPORTANT**: Copy the token immediately (starts with `ghp_`)
2. Save it somewhere safe (you won't see it again!)
3. Example: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## Use Token to Push

### Method 1: Update Remote URL with Token

Run this in Command Prompt:

```cmd
cd d:\Morning_Quiz-master
"C:\Program Files\Git\bin\git.exe" remote set-url origin https://YOUR_TOKEN@github.com/Leonardus437/Morning_Quiz.git
```

Replace `YOUR_TOKEN` with your actual token.

Example:
```cmd
"C:\Program Files\Git\bin\git.exe" remote set-url origin https://ghp_abc123xyz789@github.com/Leonardus437/Morning_Quiz.git
```

Then push:
```cmd
"C:\Program Files\Git\bin\git.exe" push -u origin main --force
```

---

### Method 2: Use Token When Prompted

When git asks for password, paste your token (not your GitHub password).

Username: `Leonardus437`
Password: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (your token)

---

## Quick Deploy Script with Token

Save your token, then run:

```cmd
d:\Morning_Quiz-master\deploy-with-token.bat
```

(Script created below)

---

## ⚠️ Security Notes

- **Never commit token to repository**
- **Don't share token publicly**
- **Regenerate if compromised**
- **Use fine-grained tokens for better security** (optional)

---

## Alternative: Use GitHub Desktop (No Token Needed)

Download: https://desktop.github.com/

GitHub Desktop handles authentication automatically - no token needed!

---

## Quick Links

- **Generate Token**: https://github.com/settings/tokens/new
- **Token Settings**: https://github.com/settings/tokens
- **GitHub Desktop**: https://desktop.github.com/
