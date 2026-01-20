# 🐳 DOCKER QUICK START - NEW PC

## ⚡ ONE-CLICK SETUP

**Just run this:**
```cmd
SETUP_DOCKER_NOW.bat
```

That's it! Wait 5-10 minutes and your system will be ready.

---

## 📋 What You Need

1. **Docker Desktop** - Download from https://docker.com
2. **This folder** - d:\Morning_Quiz-master
3. **5-10 minutes** - For first-time setup

---

## 🚀 Quick Commands

| Action | Command |
|--------|---------|
| **Setup Everything** | `SETUP_DOCKER_NOW.bat` |
| **Check Status** | `CHECK_DOCKER.bat` |
| **Fix Problems** | `FIX_DOCKER.bat` |
| **Rebuild Clean** | `REBUILD_DOCKER.bat` |

---

## 🌐 Access URLs

After setup, open these in your browser:

```
Frontend:  http://localhost:3000
Backend:   http://localhost:8000
API Docs:  http://localhost:8000/docs
```

---

## 🔑 Default Login

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

## 🔧 Daily Usage

**Start System:**
```cmd
docker-compose up -d
```

**Stop System:**
```cmd
docker-compose down
```

**View Logs:**
```cmd
docker-compose logs -f
```

---

## ❌ Common Problems & Fixes

### "Docker is not running"
→ Open Docker Desktop and wait for it to start

### "Port already in use"
→ Run `FIX_DOCKER.bat` → Option 5

### "Build failed"
→ Run `REBUILD_DOCKER.bat`

### "Can't access frontend"
→ Wait 2 minutes after starting, then refresh browser

### "Database connection error"
→ Run `docker-compose restart db`

---

## 📊 Check Everything Works

1. Run `CHECK_DOCKER.bat`
2. Open http://localhost:3000
3. Login as admin
4. Create a test quiz
5. ✅ If all works, you're ready!

---

## 🆘 Need Help?

**View detailed guide:**
```
DOCKER_SETUP_GUIDE.md
```

**Interactive troubleshooter:**
```
FIX_DOCKER.bat
```

**Check logs:**
```cmd
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

---

## 💾 Your Data

**Data is saved in Docker volumes:**
- Survives container restarts
- Survives PC restarts
- Only deleted with `docker-compose down -v`

**Backup database:**
```cmd
docker exec tvet_quiz-db-1 pg_dump -U quiz_user morning_quiz > backup.sql
```

---

## 🎯 Next Steps After Setup

1. ✅ Verify system works (login as admin)
2. 📤 Upload your student lists
3. 👨‍🏫 Register your teachers
4. 📚 Create lessons
5. 📝 Start creating quizzes!

---

## 🔄 Update After Code Changes

```cmd
docker-compose up -d --build
```

---

**Ready?** Run `SETUP_DOCKER_NOW.bat` to begin! 🚀
