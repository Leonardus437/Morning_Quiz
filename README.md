# TVET Quiz System

A complete offline-first quiz system for TVET/TSS schools running on local network (LAN).

## Quick Setup for Teachers

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
   - Default teacher login: `teacher001` / `teacher123`

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
```cmd
docker-compose down
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
