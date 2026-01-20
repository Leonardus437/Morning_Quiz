# Cloudflare Pages Deployment - FIXED ✅

## Your URLs:
- **Frontend**: https://tsskwizi.pages.dev
- **Backend**: https://tvet-quiz-backend.onrender.com
- **Render Dashboard**: https://dashboard.render.com/web/srv-d5drg0p5pdvs73dgmbe0

## Latest Fixes (Applied):
✅ Fixed Mixed Content Error (HTTP → HTTPS)
✅ Fixed Render build configuration
✅ API now correctly detects Cloudflare Pages
✅ Backend is deployed and running

## IMPORTANT: Fix Teacher Login Issue

### Problem:
Newly created teachers (like "Elam") cannot login because password hashes don't match.

### Solution:
Run this in Render Shell to fix teacher passwords:

1. **Go to Render Shell**: https://dashboard.render.com/web/srv-d5drg0p5pdvs73dgmbe0/shell

2. **Run the fix script**:
   ```bash
   cd backend
   python3 fix_teacher_password.py
   ```

3. **Follow the prompts**:
   - Enter teacher username (e.g., `Elam`)
   - Enter new password (e.g., `teacher123`)

4. **Test login** at https://tsskwizi.pages.dev/teacher

### Alternative: Reset All Teacher Passwords

If you want to reset ALL teacher passwords to `teacher123`:

```bash
cd backend
python3 -c "
import sqlite3
import hashlib
import secrets

def hash_password(password):
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    except:
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f'{salt}:{password_hash}'

conn = sqlite3.connect('quiz.db')
cursor = conn.cursor()
new_hash = hash_password('teacher123')
cursor.execute('UPDATE users SET password_hash = ? WHERE role = \'teacher\'', (new_hash,))
conn.commit()
print(f'✅ Reset {cursor.rowcount} teacher passwords to: teacher123')
conn.close()
"
```

## Test Login After Fix:

**Default Teacher:**
- Username: `teacher001`
- Password: `teacher123`

**Newly Created Teacher (after fix):**
- Username: `Elam` (or whatever you created)
- Password: `teacher123` (or whatever you set)

**Admin:**
- Username: `admin`
- Password: `admin123`

## Important Notes:
- ⚠️ Render free tier sleeps after 15 mins inactivity
- ⏱️ First request takes 30-50 seconds to wake up
- ✅ After wake up, works normally
- 🔒 All connections now use HTTPS

## If Login Still Fails:
1. Verify Render backend is "Live" (green)
2. Check Render logs for errors
3. Test backend directly: https://tvet-quiz-backend.onrender.com/health
4. Check browser console (F12)
5. Make sure you ran the password fix script
