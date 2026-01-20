# 🚀 Morning Quiz System - Quick Start Guide

## ⚡ 3-Minute Setup

### 1. Start the System
```cmd
# Open Command Prompt as Administrator
cd C:\Users\PC\Music\Morning_Quiz
docker-compose up -d
```

### 2. Access Admin Panel
- Open browser: **http://localhost:3000/admin**
- Login: `admin` / `admin123`

### 3. Upload Students
1. Click **"Students"** in admin panel
2. Click **"Upload Students"** button
3. Select your Excel/CSV/Text file
4. Click **"Upload"**
5. ✅ Students are automatically created!

### 4. Share with Students
- Find your PC's IP: `ipconfig`
- Share: **http://[YOUR-IP]:3000**
- Students login with generated usernames and password: `student123`

---

## 📁 Supported File Formats

### Excel Files (.xlsx, .xls)
```
Column A: S/N (optional)
Column B: Student Names
```

### CSV Files (.csv)
```csv
Name,Department,Level
John Doe,Software Development,Level 4
Jane Smith,Computer System and Architecture,Level 5
```

### Text Files (.txt)
```
1. John Doe
2. Jane Smith
3. Alice Johnson
```

---

## 🎯 Test Files Available

Use these files to test the system:
- `test_students.csv` (5 students)
- `test_students.txt` (10 students)

---

## ✅ What Happens Automatically

1. **Username Generation**: "John Doe" → "johndoe"
2. **Default Password**: All students get "student123"
3. **Department Assignment**: "Software Development" (default)
4. **Level Assignment**: "Level 4" (default)
5. **Account Creation**: Ready to login immediately

---

## 🔧 Quick Commands

### Start System
```cmd
docker-compose up -d
```

### Stop System
```cmd
docker-compose down
```

### Check Status
```cmd
docker-compose ps
```

### View Logs
```cmd
docker-compose logs -f
```

---

## 🌐 Access URLs

- **Admin Panel**: http://localhost:3000/admin
- **Student Portal**: http://localhost:3000
- **API Health**: http://localhost:8000/health

---

## 👥 Default Accounts

### Admin
- Username: `admin`
- Password: `admin123`

### Teachers
- Username: `teacher001`, `teacher002`, `teacher003`
- Password: `pass123`

### Students (after upload)
- Username: Generated from name (e.g., "johndoe")
- Password: `student123`

---

## 🚨 Troubleshooting

### System Won't Start
```cmd
docker-compose down
docker-compose up -d
```

### Port Conflict
```cmd
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F
```

### Upload Issues
- Check file format (Excel/CSV/Text only)
- Ensure file has student names
- File size must be < 10MB

---

## 📞 Need Help?

1. **Check System Status**: Run `verify_system.bat`
2. **View Complete Guide**: Read `COMPLETE_SETUP_GUIDE.md`
3. **Test Upload**: Use provided test files

---

**🎉 You're Ready to Go!**

The student upload system is verified working and ready for production use.