# TVET Quiz System - Complete Setup Guide

## After Formatting Your Computer

Since you've formatted your computer, here's exactly what you need to install to get your TVET Quiz System working again:

## 🔧 Required Dependencies

### 1. Docker Desktop (CRITICAL - Required)
- **Download**: https://www.docker.com/products/docker-desktop/
- **Version**: Latest stable version
- **Why needed**: Your entire system runs in Docker containers
- **After installation**: Restart your computer

### 2. Windows Subsystem for Linux (WSL2) - Usually auto-installed with Docker
- Docker Desktop will prompt you to install this if needed
- Follow the prompts during Docker installation

## 🚀 Quick Setup Steps

### Step 1: Install Docker Desktop
1. Download Docker Desktop from the link above
2. Run the installer as Administrator
3. Follow installation prompts
4. **IMPORTANT**: Restart your computer after installation
5. Start Docker Desktop from Start menu

### Step 2: Verify Installation
1. Right-click `setup-dependencies.bat` → "Run as administrator"
2. This will check all dependencies and guide you

### Step 3: Start Your System
```cmd
# Navigate to your project folder
cd "f:\SIDE HUSTLE\Morning_Quiz"

# Start the system
docker-compose up -d
```

## 🔍 What Each Component Does

### Docker Containers in Your System:
- **PostgreSQL Database** (Port 5432): Stores all quiz data
- **Python Backend** (Port 8000): FastAPI server with all quiz logic
- **Svelte Frontend** (Port 3000): Web interface for teachers and students

### Your System Architecture:
```
Frontend (Svelte/Node.js) → Backend (Python/FastAPI) → Database (PostgreSQL)
```

## 📋 Optional Dependencies (For Development)

### Python 3.9+ (Optional)
- **Download**: https://www.python.org/downloads/
- **Why**: Only needed if you want to modify backend code locally
- **Note**: Not required for normal operation (runs in Docker)

### Node.js 18+ (Optional)
- **Download**: https://nodejs.org/
- **Why**: Only needed if you want to modify frontend code locally
- **Note**: Not required for normal operation (runs in Docker)

## 🛠️ Troubleshooting Common Issues

### "Docker is not running"
```cmd
# Start Docker Desktop from Start menu
# Wait for it to fully start (whale icon in system tray)
```

### "Port already in use"
```cmd
# Stop any existing containers
docker-compose down

# Kill processes using ports
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F
```

### "Permission denied"
```cmd
# Always run as Administrator
# Right-click Command Prompt → "Run as administrator"
```

## ✅ Verification Checklist

After installation, verify everything works:

- [ ] Docker Desktop is installed and running
- [ ] `docker --version` shows version info
- [ ] `docker-compose --version` shows version info
- [ ] Ports 3000, 8000, 5432 are available
- [ ] `docker-compose up -d` starts without errors
- [ ] Can access http://localhost:3000/teacher
- [ ] Can login with teacher001/teacher123

## 🎯 Quick Commands Reference

```cmd
# Check dependencies
setup-dependencies.bat

# Start system
docker-compose up -d

# Stop system
docker-compose down

# View logs
docker-compose logs

# Restart system
docker-compose restart

# Full rebuild (if needed)
docker-compose down -v
docker-compose up -d --build
```

## 📞 If You Need Help

1. Run `setup-dependencies.bat` first
2. Check the output for specific error messages
3. Most issues are resolved by:
   - Installing Docker Desktop
   - Running as Administrator
   - Restarting computer after Docker installation

Your system is designed to be 100% offline-first, so once Docker is installed, everything else is self-contained!