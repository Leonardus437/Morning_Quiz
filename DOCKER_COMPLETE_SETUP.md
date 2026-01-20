# 🎯 DOCKER SETUP - NEW PC COMPLETE GUIDE

## 🚀 FASTEST WAY (Recommended)

### Just Double-Click This:
```
SETUP_DOCKER_NOW.bat
```

**That's it!** Wait 5-10 minutes and everything will be ready.

---

## 📦 What Gets Installed

Your system will have:
- ✅ Frontend (SvelteKit) - Port 3000
- ✅ Backend (FastAPI) - Port 8000  
- ✅ Database (PostgreSQL) - Port 5432
- ✅ All default accounts created
- ✅ Sample data loaded

---

## 📋 Prerequisites

### 1. Install Docker Desktop
- Download: https://www.docker.com/products/docker-desktop
- Install and restart PC
- Open Docker Desktop
- Wait for "Docker Desktop is running"

### 2. Verify Installation
Open Command Prompt:
```cmd
docker --version
docker-compose --version
```

Should show version numbers.

---

## 🎬 Step-by-Step Setup

### Option A: One-Click (Easiest)
```cmd
1. Double-click: SETUP_DOCKER_NOW.bat
2. Wait 5-10 minutes
3. Browser opens automatically
4. Login with: admin / admin123
```

### Option B: Manual Setup
```cmd
1. Open Command Prompt
2. cd d:\Morning_Quiz-master
3. docker-compose down -v
4. docker-compose build --no-cache
5. docker-compose up -d
6. Wait 2 minutes
7. Open http://localhost:3000
```

---

## ✅ Verify Everything Works

### Quick Test (2 minutes)
```cmd
1. Run: CHECK_DOCKER.bat
2. Open: http://localhost:3000
3. Login: admin / admin123
4. See dashboard? ✅ Working!
```

### Full Test (5 minutes)
```cmd
1. Login as admin
2. Go to Students → Upload Students
3. Go to Teachers → Register Teacher
4. Go to Lessons → Create Lesson
5. Login as teacher (new tab)
6. Create a quiz
7. Broadcast quiz
8. Login as student (new tab)
9. Take quiz
10. Submit quiz
11. Check results ✅ All working!
```

---

## 🔧 Useful Scripts

| Script | Purpose |
|--------|---------|
| `SETUP_DOCKER_NOW.bat` | One-click complete setup |
| `CHECK_DOCKER.bat` | Verify system status |
| `FIX_DOCKER.bat` | Interactive troubleshooter |
| `REBUILD_DOCKER.bat` | Clean rebuild |

---

## 🌐 Access Your System

After setup completes:

**Main URLs:**
```
Student/Teacher Access:  http://localhost:3000
Admin Dashboard:         http://localhost:3000
Backend API:             http://localhost:8000
API Documentation:       http://localhost:8000/docs
Health Check:            http://localhost:8000/health
```

**Network Access (from other devices):**
```
Find your IP: ipconfig
Then use: http://[YOUR-IP]:3000
```

---

## 🔑 Default Accounts

```
DOS Administrator:
  Username: admin
  Password: admin123
  Access: Full system control

Default Teacher:
  Username: teacher001
  Password: teacher123
  Department: Software Development

Default Student:
  Username: student001
  Password: pass123
  Department: Software Development
  Level: Level 5
```

---

## 📊 Container Management

### View Status
```cmd
docker-compose ps
```

### View Logs
```cmd
# All services
docker-compose logs -f

# Specific service
docker-compose logs backend -f
docker-compose logs frontend -f
docker-compose logs db -f
```

### Start/Stop
```cmd
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Restart specific service
docker-compose restart backend
```

---

## 🐛 Troubleshooting

### Problem: Docker not running
**Solution:**
```
1. Open Docker Desktop
2. Wait for green "Running" status
3. Try again
```

### Problem: Port already in use
**Solution:**
```cmd
# Option 1: Use fix script
FIX_DOCKER.bat → Option 5

# Option 2: Manual
docker-compose down
netstat -ano | findstr :3000
taskkill /PID [PID] /F
docker-compose up -d
```

### Problem: Build fails
**Solution:**
```cmd
# Clean rebuild
docker system prune -af --volumes
docker-compose build --no-cache
docker-compose up -d
```

### Problem: Frontend not loading
**Solution:**
```cmd
# Wait 2 minutes after starting
# Then check logs
docker-compose logs frontend

# If still not working, rebuild
docker-compose up -d --build frontend
```

### Problem: Backend errors
**Solution:**
```cmd
# Check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend

# If database error, restart db
docker-compose restart db
timeout /t 10
docker-compose restart backend
```

### Problem: Database connection failed
**Solution:**
```cmd
# Reset database
docker-compose down -v
docker-compose up -d
```

**Warning:** This deletes all data!

---

## 💾 Data Management

### Backup Database
```cmd
docker exec tvet_quiz-db-1 pg_dump -U quiz_user morning_quiz > backup.sql
```

### Restore Database
```cmd
docker exec -i tvet_quiz-db-1 psql -U quiz_user morning_quiz < backup.sql
```

### Clear All Data (Fresh Start)
```cmd
docker-compose down -v
docker-compose up -d
```

---

## 🔄 Daily Usage

### Morning (Start Work)
```cmd
cd d:\Morning_Quiz-master
docker-compose up -d
```

### Evening (Stop Work)
```cmd
docker-compose down
```

### Check Status Anytime
```cmd
CHECK_DOCKER.bat
```

---

## 🚀 Performance Tips

### Allocate More Resources
```
1. Open Docker Desktop
2. Settings → Resources
3. Set:
   - CPUs: 4
   - Memory: 4 GB
   - Disk: 20 GB
4. Apply & Restart
```

### Speed Up Builds
```cmd
set DOCKER_BUILDKIT=1
docker-compose build
```

---

## 📱 Network Setup (LAN Access)

### Enable Firewall
```cmd
# Run as Administrator
netsh advfirewall firewall add rule name="TVET Quiz Frontend" dir=in action=allow protocol=TCP localport=3000
netsh advfirewall firewall add rule name="TVET Quiz Backend" dir=in action=allow protocol=TCP localport=8000
```

### Find Your IP
```cmd
ipconfig
```
Look for "IPv4 Address" (e.g., 192.168.1.100)

### Share with Students
```
Give students: http://[YOUR-IP]:3000
Example: http://192.168.1.100:3000
```

---

## 🎓 What to Do After Setup

### 1. Upload Real Students
```
1. Login as admin
2. Students → Upload Students
3. Select Excel/PDF file
4. Generate credentials
5. Print and distribute
```

### 2. Register Teachers
```
1. Login as admin
2. Teachers → Register Teacher
3. Fill details
4. Give credentials to teacher
```

### 3. Create Lessons
```
1. Login as admin
2. Lessons → Create Lesson
3. Assign to teachers
```

### 4. Start Teaching
```
1. Teacher creates questions
2. Teacher creates quiz
3. Teacher broadcasts quiz
4. Students take quiz
5. Teacher views results
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `DOCKER_QUICK_START.md` | Quick reference |
| `DOCKER_SETUP_GUIDE.md` | Detailed guide |
| `DEPLOYMENT_STATUS_REPORT.md` | Cloud deployment info |
| `DEPLOYMENT_VERIFICATION_CHECKLIST.md` | Testing checklist |

---

## 🆘 Get Help

### Interactive Troubleshooter
```cmd
FIX_DOCKER.bat
```

### Check Logs
```cmd
docker-compose logs -f
```

### View Container Status
```cmd
docker-compose ps
docker stats
```

### Access Container Shell
```cmd
# Backend
docker exec -it tvet_quiz-backend-1 bash

# Database
docker exec -it tvet_quiz-db-1 psql -U quiz_user -d morning_quiz
```

---

## ✅ Success Checklist

After running setup, verify:

- [ ] Docker Desktop is running
- [ ] All 3 containers are up (ps shows "Up")
- [ ] Frontend loads at localhost:3000
- [ ] Backend health check passes
- [ ] Can login as admin
- [ ] Can login as teacher
- [ ] Can login as student
- [ ] Can create quiz
- [ ] Can take quiz
- [ ] Can view results

**If all checked:** 🎉 **System is ready for production!**

---

## 🔗 Quick Links

**Local Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Cloud Deployment (Already Live):**
- Frontend: https://tsskqizi.pages.dev
- Backend: https://tvet-quiz-backend.onrender.com

**Management:**
- Docker Desktop: Open from Start Menu
- Render Dashboard: https://dashboard.render.com
- Cloudflare Dashboard: https://dash.cloudflare.com

---

## 🎯 Summary

**You have TWO systems:**

1. **Local (Docker)** - For development/offline use
   - Run on your PC
   - Access: http://localhost:3000
   - Full control, fast, offline-capable

2. **Cloud (Render + Cloudflare)** - For production/online use
   - Already deployed and running
   - Access: https://tsskqizi.pages.dev
   - Accessible from anywhere

**Use local for:**
- Testing new features
- Offline demonstrations
- Development work
- Training sessions

**Use cloud for:**
- Real student quizzes
- Remote access
- Production use
- 24/7 availability

---

**Ready to start?** Run `SETUP_DOCKER_NOW.bat` now! 🚀
