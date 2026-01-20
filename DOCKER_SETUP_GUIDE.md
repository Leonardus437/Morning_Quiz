# 🐳 DOCKER SETUP GUIDE - NEW PC

## Quick Start (5 Minutes)

### Step 1: Install Docker Desktop
1. Download Docker Desktop for Windows:
   - Go to: https://www.docker.com/products/docker-desktop
   - Download and install
   - Restart your PC if prompted

2. Start Docker Desktop
   - Open Docker Desktop application
   - Wait for "Docker Desktop is running" message

### Step 2: Verify Docker Installation
```cmd
docker --version
docker-compose --version
```

Expected output:
```
Docker version 24.x.x
Docker Compose version v2.x.x
```

### Step 3: Rebuild Everything
```cmd
cd d:\Morning_Quiz-master
REBUILD_DOCKER.bat
```

This will:
- ✅ Clean up old containers/images
- ✅ Build fresh images
- ✅ Start all services
- ✅ Initialize database
- ✅ Verify everything works

### Step 4: Access Your System
```
Frontend:  http://localhost:3000
Backend:   http://localhost:8000
API Docs:  http://localhost:8000/docs
```

---

## 📋 What Gets Created

### Docker Containers
```
tvet_quiz-frontend-1  → Frontend (SvelteKit)
tvet_quiz-backend-1   → Backend (FastAPI)
tvet_quiz-db-1        → Database (PostgreSQL)
```

### Docker Images
```
morning_quiz-master-frontend  → Frontend image
morning_quiz-master-backend   → Backend image
postgres:15-alpine            → Database image
```

### Docker Volumes
```
morning_quiz-master_db_data   → Database storage
```

---

## 🔧 Common Commands

### Start System
```cmd
docker-compose up -d
```

### Stop System
```cmd
docker-compose down
```

### View Logs
```cmd
docker-compose logs -f
```

### Restart Services
```cmd
docker-compose restart
```

### Rebuild After Code Changes
```cmd
docker-compose up -d --build
```

### Check Status
```cmd
docker-compose ps
```

### Access Container Shell
```cmd
# Backend
docker exec -it tvet_quiz-backend-1 bash

# Database
docker exec -it tvet_quiz-db-1 psql -U quiz_user -d morning_quiz
```

---

## 🐛 Troubleshooting

### Problem: "Docker is not running"
**Solution:**
1. Open Docker Desktop
2. Wait for it to fully start
3. Try again

### Problem: "Port already in use"
**Solution:**
```cmd
# Stop any existing containers
docker-compose down

# Kill processes on ports
netstat -ano | findstr :3000
netstat -ano | findstr :8000
taskkill /PID [PID_NUMBER] /F

# Start again
docker-compose up -d
```

### Problem: "Build failed"
**Solution:**
```cmd
# Clean everything
docker system prune -af --volumes

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Problem: "Database connection error"
**Solution:**
```cmd
# Restart database
docker-compose restart db

# Wait 10 seconds
timeout /t 10

# Restart backend
docker-compose restart backend
```

### Problem: "Frontend not loading"
**Solution:**
```cmd
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

---

## 📊 Verify Everything Works

### 1. Check Containers
```cmd
docker-compose ps
```

Expected output:
```
NAME                    STATUS
tvet_quiz-backend-1     Up
tvet_quiz-db-1          Up
tvet_quiz-frontend-1    Up
```

### 2. Test Backend
```cmd
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "healthy",
  "service": "Morning Quiz API"
}
```

### 3. Test Frontend
Open browser: http://localhost:3000

Expected: Login page loads

### 4. Test Login
- Username: `admin`
- Password: `admin123`

Expected: Dashboard loads

---

## 🔄 Daily Usage

### Morning (Start System)
```cmd
cd d:\Morning_Quiz-master
docker-compose up -d
```

### Evening (Stop System)
```cmd
docker-compose down
```

### Check if Running
```cmd
CHECK_DOCKER.bat
```

---

## 💾 Data Persistence

Your data is stored in Docker volumes:
- Database data: `morning_quiz-master_db_data`
- Persists even when containers are stopped
- Only deleted with `docker-compose down -v`

### Backup Database
```cmd
docker exec tvet_quiz-db-1 pg_dump -U quiz_user morning_quiz > backup.sql
```

### Restore Database
```cmd
docker exec -i tvet_quiz-db-1 psql -U quiz_user morning_quiz < backup.sql
```

---

## 🚀 Performance Tips

### Allocate More Resources
1. Open Docker Desktop
2. Settings → Resources
3. Increase:
   - CPUs: 4
   - Memory: 4 GB
   - Disk: 20 GB

### Speed Up Builds
```cmd
# Use BuildKit
set DOCKER_BUILDKIT=1
docker-compose build
```

---

## 📱 Network Access (LAN)

### Find Your PC IP
```cmd
ipconfig
```
Look for "IPv4 Address"

### Access from Other Devices
```
Frontend: http://[YOUR-IP]:3000
Backend:  http://[YOUR-IP]:8000
```

### Enable Firewall Access
```cmd
# Run as Administrator
netsh advfirewall firewall add rule name="TVET Quiz Frontend" dir=in action=allow protocol=TCP localport=3000
netsh advfirewall firewall add rule name="TVET Quiz Backend" dir=in action=allow protocol=TCP localport=8000
```

---

## 🔐 Security Notes

### Change Default Passwords
Edit `docker-compose.yml`:
```yaml
environment:
  POSTGRES_PASSWORD: your-secure-password
  SECRET_KEY: your-secret-key
```

Then rebuild:
```cmd
docker-compose down
docker-compose up -d --build
```

---

## 📦 Container Details

### Frontend Container
- **Base**: Node 18 Alpine
- **Port**: 3000 → 5173
- **Hot Reload**: Enabled
- **Build Time**: ~2 minutes

### Backend Container
- **Base**: Python 3.11 Slim
- **Port**: 8000
- **Auto Reload**: Enabled
- **Build Time**: ~3 minutes

### Database Container
- **Base**: PostgreSQL 15 Alpine
- **Port**: 5432
- **User**: quiz_user
- **Database**: morning_quiz
- **Build Time**: ~30 seconds

---

## ✅ Complete Setup Checklist

- [ ] Docker Desktop installed
- [ ] Docker Desktop running
- [ ] Ran `REBUILD_DOCKER.bat`
- [ ] All 3 containers running
- [ ] Backend health check passes
- [ ] Frontend loads at localhost:3000
- [ ] Can login as admin
- [ ] Can create quiz
- [ ] Can view results

---

## 🆘 Emergency Recovery

### Nuclear Option (Start Fresh)
```cmd
# Stop everything
docker-compose down -v

# Remove all Docker data
docker system prune -af --volumes

# Rebuild from scratch
REBUILD_DOCKER.bat
```

**Warning**: This deletes ALL data including quizzes and students!

---

## 📞 Quick Reference

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

**Rebuild:**
```cmd
REBUILD_DOCKER.bat
```

**Check Status:**
```cmd
CHECK_DOCKER.bat
```

**Access URLs:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Default Login:**
- Admin: admin / admin123
- Teacher: teacher001 / teacher123
- Student: student001 / pass123

---

**Ready to start?** Run `REBUILD_DOCKER.bat` now!
