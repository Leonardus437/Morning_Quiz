# 🌐 ENABLE LAN ACCESS FOR STUDENTS

## Quick Setup (3 Steps)

### Step 1: Run the Script as Administrator
1. **Right-click** on `enable-lan-access.bat`
2. Select **"Run as administrator"**
3. Click **"Yes"** when Windows asks for permission

This will:
- ✅ Open port 3000 in Windows Firewall
- ✅ Open port 8000 in Windows Firewall
- ✅ Show your PC's IP address
- ✅ Verify Docker containers are running

---

### Step 2: Get Your IP Address
After running the script, you'll see:
```
Your PC IP: 10.11.248.208
```

**Student Access URL:**
```
http://10.11.248.208:3000
```

---

### Step 3: Share with Students
1. **Write the URL on the board:** `http://10.11.248.208:3000`
2. **Students connect to same WiFi** as your PC
3. **Students open browser** and enter the URL
4. **Students login** with their credentials

---

## Manual Firewall Setup (If Script Fails)

### Option 1: Windows Defender Firewall GUI
1. Press `Windows + R`
2. Type: `wf.msc` and press Enter
3. Click **"Inbound Rules"** → **"New Rule"**
4. Select **"Port"** → Next
5. Select **"TCP"** → Enter port: `3000` → Next
6. Select **"Allow the connection"** → Next
7. Check all boxes (Domain, Private, Public) → Next
8. Name: `TVET Quiz System` → Finish
9. **Repeat for port 8000**

### Option 2: Command Prompt (Run as Admin)
```cmd
netsh advfirewall firewall add rule name="TVET Quiz System" dir=in action=allow protocol=TCP localport=3000
netsh advfirewall firewall add rule name="TVET Quiz Backend" dir=in action=allow protocol=TCP localport=8000
```

---

## Troubleshooting

### Students Can't Access
1. **Check same network:**
   - Your PC and student devices must be on **same WiFi**
   - Check WiFi name on both devices

2. **Check firewall:**
   - Run `enable-lan-access.bat` as administrator
   - Or manually add firewall rules (see above)

3. **Check IP address:**
   - Run: `ipconfig` in Command Prompt
   - Look for "IPv4 Address" under your WiFi adapter
   - Use that IP in the URL

4. **Test from your phone:**
   - Connect phone to same WiFi
   - Open browser on phone
   - Go to: `http://10.11.248.208:3000`
   - Should see login page

5. **Check Docker:**
   - Run: `docker ps`
   - All 3 containers should be "Up"

### Port Already in Use
```cmd
docker-compose down
docker-compose up -d
```

### Containers Not Running
```cmd
cd C:\TVETQuiz
docker-compose up -d
```

---

## Network Requirements

### Minimum:
- ✅ Local WiFi router
- ✅ Your PC connected to WiFi
- ✅ Students connected to **same WiFi**
- ✅ No internet required!

### Capacity:
- ✅ Up to **50 concurrent students**
- ✅ Works on **any local network**
- ✅ **100% offline** (no internet needed)

---

## Access URLs

### For Students (LAN):
```
http://10.11.248.208:3000
```

### For Teacher (This PC):
```
http://localhost:3000/teacher
http://localhost:3000/admin
```

### For DOS/Admin (This PC):
```
http://localhost:3000/admin
```

---

## Default Credentials

### Teacher:
- Username: `teacher001`
- Password: `teacher123`

### Sample Student:
- Username: `student001`
- Password: `pass123`

---

## Quick Test

1. **On your PC:**
   - Open browser → `http://localhost:3000`
   - Should see login page ✅

2. **On your phone:**
   - Connect to same WiFi
   - Open browser → `http://10.11.248.208:3000`
   - Should see login page ✅

3. **If both work:**
   - ✅ System is ready!
   - ✅ Share URL with students!

---

## Support

If students still can't access:
1. Check Windows Firewall is not blocking
2. Check antivirus is not blocking
3. Check router allows local connections
4. Try disabling Windows Firewall temporarily to test

---

**Last Updated:** 2025-11-26
**Status:** ✅ READY FOR LAN ACCESS
