# Fix Teacher Password - NO SHELL ACCESS NEEDED! ✅

## Problem
Newly created teachers (like "Elam") cannot login because password hashes don't match.

## Solution (Works WITHOUT Render Shell!)

### Option 1: Use Browser Console (EASIEST!)

1. **Login as Admin** at https://tsskwizi.pages.dev/admin
   - Username: `admin`
   - Password: `admin123`

2. **Open Browser Console** (Press F12)

3. **Run this code** (replace "Elam" and "teacher123" with your values):

```javascript
fetch('https://tvet-quiz-backend.onrender.com/admin/fix-teacher-password?username=Elam&new_password=teacher123', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token'),
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(data => console.log('✅ Success:', data))
.catch(err => console.error('❌ Error:', err));
```

4. **Test Login** at https://tsskwizi.pages.dev/teacher
   - Username: `Elam`
   - Password: `teacher123`

### Option 2: Use Postman/Thunder Client

1. **Create POST Request**:
   - URL: `https://tvet-quiz-backend.onrender.com/admin/fix-teacher-password?username=Elam&new_password=teacher123`
   - Method: POST
   - Headers:
     - `Authorization`: `Bearer YOUR_ADMIN_TOKEN`
     - `Content-Type`: `application/json`

2. **Get Admin Token**:
   - Login as admin at https://tsskwizi.pages.dev/admin
   - Open Browser Console (F12)
   - Type: `localStorage.getItem('token')`
   - Copy the token

3. **Send Request** and test login!

### Option 3: Reset ALL Teacher Passwords

Run this in browser console (after logging in as admin):

```javascript
// Reset all teachers to password: teacher123
fetch('https://tvet-quiz-backend.onrender.com/reset-all-teacher-passwords', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
})
.then(r => r.json())
.then(data => console.log('✅ All teachers reset:', data))
.catch(err => console.error('❌ Error:', err));
```

## Quick Test

After fixing, test with:
- Username: `Elam` (or your teacher username)
- Password: `teacher123` (or whatever you set)
- URL: https://tsskwizi.pages.dev/teacher

## Why This Happens

When admin creates a new teacher, the password hashing might not match the login verification. This API endpoint re-hashes the password correctly.

## Default Credentials (Always Work)

- **Admin**: `admin` / `admin123`
- **Teacher001**: `teacher001` / `teacher123`
- **Student001**: `student001` / `student123`

---

**No Render Shell access needed!** 🎉
