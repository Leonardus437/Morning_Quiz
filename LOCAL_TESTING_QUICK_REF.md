# 🧪 LOCAL TESTING - QUICK REFERENCE

## ⚡ FASTEST WAY TO TEST

### 1. Start System
```cmd
SETUP_DOCKER_NOW.bat
```
Wait 5-10 minutes

### 2. Run Tests
```cmd
RUN_LOCAL_TESTS.bat
```
This will:
- ✅ Check Docker is running
- ✅ Start containers if needed
- ✅ Test backend health
- ✅ Test frontend access
- ✅ Open test page automatically
- ✅ Open frontend in browser

### 3. Review Results
- Automated tests run in browser
- All should show ✅ PASS
- If any fail, see troubleshooting below

---

## 📋 MANUAL TEST CHECKLIST

### Quick Test (5 minutes)
- [ ] Open http://localhost:3000
- [ ] Login as admin (admin/admin123)
- [ ] Dashboard loads correctly
- [ ] Click "Students" - page loads
- [ ] Click "Teachers" - page loads
- [ ] Logout and login as teacher001
- [ ] Dashboard loads correctly
- [ ] Logout and login as student001
- [ ] Dashboard loads correctly

### Full Test (30 minutes)
Follow: `LOCAL_TESTING_COMPLETE_GUIDE.md`

---

## 🌐 Test URLs

```
Frontend:     http://localhost:3000
Backend:      http://localhost:8000
API Docs:     http://localhost:8000/docs
Health Check: http://localhost:8000/health
Test Page:    TEST_LOCAL_SYSTEM.html
```

---

## 🔑 Test Accounts

```
Admin:
  Username: admin
  Password: admin123

Teacher:
  Username: teacher001
  Password: teacher123

Student:
  Username: student001
  Password: pass123
```

---

## ✅ What to Test

### Core Functionality
1. **Authentication** - All 3 user types can login
2. **Admin Panel** - Upload students, register teachers
3. **Teacher Panel** - Create questions, create quiz, broadcast
4. **Student Panel** - View quizzes, take quiz, submit
5. **Results** - View results, export PDF/Excel
6. **Data Persistence** - Restart containers, data remains

### Edge Cases
1. **Wrong password** - Shows error
2. **Expired quiz** - Can't access
3. **Duplicate submission** - Prevented
4. **Large file upload** - Works correctly
5. **Multiple users** - No conflicts

---

## 🐛 Quick Fixes

### Backend Not Responding
```cmd
docker-compose restart backend
```

### Frontend Not Loading
```cmd
docker-compose restart frontend
```

### Database Issues
```cmd
docker-compose restart db
timeout /t 10
docker-compose restart backend
```

### Start Fresh
```cmd
docker-compose down -v
SETUP_DOCKER_NOW.bat
```

---

## 📊 Success Criteria

**System is ready when:**
- ✅ All automated tests pass
- ✅ All 3 user types can login
- ✅ Can create and broadcast quiz
- ✅ Can take and submit quiz
- ✅ Results display correctly
- ✅ Exports work
- ✅ No errors in console
- ✅ No errors in logs

---

## 🚀 After Testing

**If all tests pass:**
1. System is ready for production
2. Proceed with deployment to Render/Cloudflare
3. Your cloud deployment is already live at:
   - https://tsskqizi.pages.dev

**If tests fail:**
1. Check logs: `docker-compose logs`
2. Run: `FIX_DOCKER.bat`
3. Review: `LOCAL_TESTING_COMPLETE_GUIDE.md`
4. Fix issues and retest

---

## 📞 Quick Commands

```cmd
# Start system
docker-compose up -d

# Stop system
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Run tests
RUN_LOCAL_TESTS.bat

# Fix issues
FIX_DOCKER.bat

# Rebuild
SETUP_DOCKER_NOW.bat
```

---

## 🎯 Testing Workflow

```
1. SETUP_DOCKER_NOW.bat
   ↓
2. Wait 5-10 minutes
   ↓
3. RUN_LOCAL_TESTS.bat
   ↓
4. Review automated test results
   ↓
5. Manual testing (follow checklist)
   ↓
6. All pass? → Ready for production!
   ↓
7. Any fail? → Fix and retest
```

---

**Start Now:** Run `SETUP_DOCKER_NOW.bat` then `RUN_LOCAL_TESTS.bat`
