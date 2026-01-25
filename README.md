# TVET Quiz System

A complete offline-first quiz system for TVET/TSS schools running on local network (LAN).

## 🎉 NEW: Phase 1 - Advanced Question Types (JUST COMPLETED!)

### 🚀 What's New?
Your quiz system now supports **12 question types** (up from 4) - **MORE THAN GOOGLE FORMS!**

#### Basic Types
1. ✅ Multiple Choice
2. ✅ True/False
3. ✅ Short Answer
4. ✅ Essay

#### NEW Advanced Types
5. 🆕 **Multiple Select** - Checkboxes with partial credit
6. 🆕 **Dropdown Select** - Clean dropdown menu
7. 🆕 **Fill in the Blanks** - Multiple blanks in one question
8. 🆕 **Matching Pairs** - Drag & drop matching
9. 🆕 **Drag & Drop Ordering** - Arrange items in sequence
10. 🆕 **Linear Scale** - 1-10 rating questions
11. 🆕 **Code Writing** - Python, Java, C++, JavaScript, C
12. 🆕 **SQL Query** - Database query questions

### 📊 Comparison
| Feature | Google Forms | Our System | Winner |
|---------|--------------|------------|--------|
| Question Types | 9 | 12 | 🏆 US |
| Code Assessment | ❌ | ✅ | 🏆 US |
| SQL Queries | ❌ | ✅ | 🏆 US |
| Partial Credit | ❌ | ✅ | 🏆 US |
| Offline-First | ❌ | ✅ | 🏆 US |
| Drag & Drop | ❌ | ✅ | 🏆 US |
| Fill-in-Blanks | ❌ | ✅ | 🏆 US |

## 🌐 LIVE DEMO

**🚀 Try it now**: https://tsskwizi.pages.dev

- **Student Login**: `student001` / `pass123`
- **Teacher Panel**: https://tsskwizi.pages.dev/teacher
- **Teacher Login**: `teacher001` / `teacher123`

### 🎯 Quick Start (5 Minutes)

```bash
# 1. Start backend (auto-migration)
cd backend
python main.py
# Look for: "✅ Database migration complete"

# 2. Create test questions
cd ..
python test_advanced_questions.py
# Creates 10 sample questions

# 3. Test in browser
# https://tsskwizi.pages.dev/teacher
# Login: teacher001 / teacher123
# Create quiz with new question types!
```

### 📚 Documentation
- **[QUICKSTART_PHASE1.md](QUICKSTART_PHASE1.md)** - 5-minute setup guide
- **[PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md)** - Technical details
- **[BEFORE_VS_AFTER.md](BEFORE_VS_AFTER.md)** - Visual comparison
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Deployment guide
- **[DELIVERY_SUMMARY.md](DELIVERY_SUMMARY.md)** - Complete package overview

---

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
