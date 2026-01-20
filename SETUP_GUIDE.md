# Morning Quiz System - Complete Setup Guide

## 🎯 Quick Start (For Teachers)

### Step 1: Install Docker Desktop
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Install and restart your computer
3. Start Docker Desktop (wait for it to fully load)

### Step 2: Start the Quiz System
1. Double-click `start.bat` in this folder
2. Wait for "✅ Morning Quiz System started successfully!" message
3. Note your PC's IP address shown in the output

### Step 3: Access the System
- **Admin Panel**: http://localhost:3000/admin
- **Student Access**: http://[YOUR-PC-IP]:3000
- **Default Login**: admin / admin123

### Step 4: Create Your First Quiz
1. Login to admin panel
2. Go to "Add Question" tab
3. Create 5-10 questions
4. Go to "Create Quiz" tab
5. Select questions and set schedule
6. Go to "Quizzes" tab and click "Activate"

### Step 5: Share with Students
Share this URL with students: `http://[YOUR-PC-IP]:3000`

## 📱 Student Instructions

1. Open browser and go to: `http://[TEACHER-PC-IP]:3000`
2. Login with your student ID and password
3. Click "Start Quiz" when available
4. Complete quiz within time limit
5. View your results and leaderboard

## 🔧 Advanced Configuration

### Change Default Passwords
Edit `backend/init.sql` and rebuild:
```cmd
docker-compose down
docker-compose build
docker-compose up -d
```

### Backup Data
```cmd
docker-compose exec db pg_dump -U quiz_user morning_quiz > backup.sql
```

### Restore Data
```cmd
docker-compose exec -T db psql -U quiz_user morning_quiz < backup.sql
```

### View Logs
```cmd
docker-compose logs -f
```

## 🌐 Network Setup

### For School LAN Access
1. Find your PC's IP: Run `ipconfig` in Command Prompt
2. Share this URL: `http://[YOUR-IP]:3000`
3. Ensure Windows Firewall allows port 3000

### Custom Domain (Optional)
1. Set up local DNS or hosts file entries
2. Point `quiz.local` to your PC's IP
3. Students can access via `http://quiz.local`

## 📊 Features Overview

### Teacher/Admin Features
- ✅ Create multiple choice, true/false, and short answer questions
- ✅ Schedule quizzes with time limits
- ✅ Activate/deactivate quizzes
- ✅ View real-time results and leaderboards
- ✅ Export results (basic functionality)
- ✅ Question bank management

### Student Features
- ✅ Mobile-friendly interface
- ✅ PWA support (installable as app)
- ✅ Randomized question order
- ✅ Timer with auto-submit
- ✅ Immediate results and leaderboard
- ✅ One attempt per quiz

### System Features
- ✅ Completely offline (no internet required)
- ✅ Runs on local network only
- ✅ Docker containerized for easy deployment
- ✅ PostgreSQL database for reliability
- ✅ Responsive design for all devices

## 🚨 Troubleshooting

### "Docker is not running"
- Start Docker Desktop
- Wait for it to fully load (whale icon in system tray)

### "Port already in use"
```cmd
docker-compose down
netstat -ano | findstr :3000
taskkill /PID [PID_NUMBER] /F
```

### Students can't access
- Check Windows Firewall settings
- Verify PC's IP address
- Ensure all devices are on same network

### Database issues
```cmd
docker-compose down -v
docker-compose up -d
```

### Reset everything
```cmd
docker-compose down -v
docker system prune -f
docker-compose up -d
```

## 📞 Support

For technical issues:
1. Check the troubleshooting section above
2. View logs: `docker-compose logs`
3. Restart system: `stop.bat` then `start.bat`

## 🔒 Security Notes

- System runs on local network only
- Default passwords should be changed for production
- No external internet access required
- All data stored locally on your PC