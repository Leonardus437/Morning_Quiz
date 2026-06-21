# 15-PILOT TSS SCHOOLS - TVET Quiz System

A complete offline-first quiz system for 15-PILOT TSS schools running on local network (LAN).

## 📍 Pilot Coverage

This system covers **213 schools** across **12 districts** in Rwanda:

| District | Schools | Province |
|----------|---------|----------|
| Bugesera | 23 | Eastern Province |
| Gatsibo | 21 | Eastern Province |
| Gicumbi | 20 | Northern Province |
| Kicukiro | 20 | Kigali City |
| Gakenke | 19 | Northern Province |
| Huye | 19 | Southern Province |
| Kayonza | 19 | Eastern Province |
| Karongi | 18 | Western Province |
| Gasabo | 15 | Kigali City |
| Burera | 13 | Northern Province |
| Gisagara | 13 | Southern Province |
| Kamonyi | 13 | Southern Province |
| **TOTAL** | **213 schools** | **12 districts** |

## 🚀 Quick Deployment Options

### 🎯 NEW: "Netflix-Like" Installation (RECOMMENDED!)
**Students install ONCE, use forever!**

```bash
# 1. Start your system
./start-offline.sh

# 2. Generate QR code & poster
./generate-installation-materials.sh

# 3. Students scan QR → Install app → Done!
```

**Benefits:**
- ✅ Students tap app icon (no typing URLs)
- ✅ You create quiz → They refresh → See it instantly
- ✅ Works like Netflix, WhatsApp (professional!)
- ✅ Cross-platform (Android, iOS, Windows, Mac)
- ✅ 100% offline (no internet needed)

📖 **Full Guide**: See [ULTIMATE_DEPLOYMENT_GUIDE.md](ULTIMATE_DEPLOYMENT_GUIDE.md)  
📱 **PWA Guide**: See [PWA_INSTALLATION_GUIDE.md](PWA_INSTALLATION_GUIDE.md)

---

### Option 1: Linux Server with Portainer
**Best for: Schools with Linux server or dedicated PC**

```bash
# One-command deployment
sudo ./deploy-portainer.sh
```

📖 **Full Guide**: See [PORTAINER_SETUP_GUIDE.md](PORTAINER_SETUP_GUIDE.md)  
📋 **Quick Reference**: See [PORTAINER_QUICK_REFERENCE.md](PORTAINER_QUICK_REFERENCE.md)

### Option 2: Windows PC with Docker Desktop
**Best for: Teachers with Windows laptops**

## Quick Setup for Teachers (Windows)

### Prerequisites
- Windows PC with Docker Desktop installed
- Local network (LAN) access

### Installation Steps

1. **Download and Extract**
   - Extract this folder to `C:\TVETQuiz`

2. **Start the System**
   - Open Command Prompt as Administrator
   - Navigate to the project folder:
     ```cmd
     cd C:\TVETQuiz
     ```
   - Start the system:
     ```cmd
     docker-compose up -d
     ```

3. **Access the System**
   - Teacher Panel: `http://localhost:3000/teacher`
   - Student Access: `http://localhost:3000` or `http://[YOUR-PC-IP]:3000`
   - Question Types: `http://localhost:3000/teacher/question-types`
   - Default teacher login: `teacher001` / `teacher123`
   
   **Note:** Frontend runs on port 3000 externally (Vite uses 5173 internally in container)

4. **Find Your PC's IP Address**
   ```cmd
   ipconfig
   ```
   Look for "IPv4 Address" under your network adapter.

### Daily Usage

1. **Upload Students**: Login to teacher panel, upload student list, generate credentials
2. **Create Quiz**: Add questions, create quiz, set schedule
3. **Students Access**: Share `http://[YOUR-PC-IP]:3000` with students
4. **View Results**: Check leaderboard and export results from teacher panel

### Stopping the System

**Windows:**
```cmd
docker-compose down
```

**Linux/Portainer:**
```bash
sudo docker compose down
```

### Network Setup (IMPORTANT!)

**Quick Setup:**
1. Right-click `setup-network.bat` → Run as administrator
2. Share the displayed URL with students

**If students can't connect:**
- Public WiFi (like "ednet") often blocks device-to-device communication
- **Solution:** Use your phone hotspot OR buy a cheap WiFi router
- See `NETWORK-TROUBLESHOOTING.md` for detailed solutions

## Features

- ✅ **15-PILOT TSS SCHOOLS** (213 schools across 12 districts)
- ✅ **Hierarchical Login** (Province → District → School → Trade → Level)
- ✅ **100% Offline-first** (NO internet/data bundle required)
- ✅ **LAN-only operation** (works on local network)
- ✅ Mobile-friendly responsive design
- ✅ PWA support (installable)
- ✅ Automatic grading
- ✅ Real-time leaderboards
- ✅ Question randomization
- ✅ Timer support
- ✅ PDF/Excel export
- ✅ Role-based access (Teacher/Student)
- ✅ Student bulk upload (Excel/PDF/Word)
- ✅ Automatic credential generation
- ✅ Up to 50 concurrent users per PC
- ✅ **155 unique trades** with proper categorization
- ✅ **621 school-trade relationships** with level information (L1, L3-5)




## Default Accounts

**Teacher:**
- Username: `teacher001`
- Password: `teacher123`

**Sample Students:**
- `student001` / `pass123`

## Troubleshooting

**Students can't access the system:**
- Run `setup-network.bat` as Administrator
- If on public WiFi, use phone hotspot instead
- See `NETWORK-TROUBLESHOOTING.md` for full guide

**Port already in use:**
```cmd
docker-compose down
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F
```

**Database issues:**
```cmd
docker-compose down -v
docker-compose up -d
```

# Trigger rebuild 
