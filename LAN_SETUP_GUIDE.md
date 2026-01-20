# 🌐 LAN Setup Guide - Morning Quiz System

## Quick Setup for Teachers (5 Minutes)

### Step 1: Find Your PC's IP Address

**Windows:**
```cmd
ipconfig
```
Look for **IPv4 Address** (e.g., `192.168.1.100`)

**Example Output:**
```
Wireless LAN adapter Wi-Fi:
   IPv4 Address. . . . . . . . . . . : 192.168.1.100
```

### Step 2: Configure Firewall

**Allow ports 3000 and 8000:**
```cmd
netsh advfirewall firewall add rule name="Morning Quiz Frontend" dir=in action=allow protocol=TCP localport=3000
netsh advfirewall firewall add rule name="Morning Quiz Backend" dir=in action=allow protocol=TCP localport=8000
```

### Step 3: Start the System

```cmd
cd C:\MorningQuiz
docker-compose up -d
```

### Step 4: Share Access URL with Students

**Your Access URL:** `http://192.168.1.100:3000`
(Replace with your actual IP address)

---

## 📱 Student Access Instructions

### On Smartphones/Tablets:
1. Connect to the **same WiFi network** as teacher's PC
2. Open browser (Chrome/Safari)
3. Enter: `http://[TEACHER-IP]:3000`
4. Login with your credentials

### On School Computers:
1. Ensure connected to **same LAN**
2. Open browser
3. Enter: `http://[TEACHER-IP]:3000`
4. Login and start quiz

---

## ✅ Verification Checklist

- [ ] Docker containers running (`docker ps`)
- [ ] Firewall rules added
- [ ] Students on same network
- [ ] Can access `http://localhost:3000` from teacher PC
- [ ] Can access `http://[TEACHER-IP]:3000` from student device

---

## 🔧 Troubleshooting

### Students Can't Connect:
1. **Check same network**: All devices must be on same WiFi/LAN
2. **Verify IP**: Run `ipconfig` again, IP may have changed
3. **Firewall**: Temporarily disable to test, then re-enable with rules
4. **Docker**: Ensure containers running: `docker ps`

### System Slow:
- Normal for LAN operation
- Check network speed
- Reduce number of simultaneous users

### "Cannot connect to server":
```cmd
# Restart system
docker-compose down
docker-compose up -d
```

---

## 🎯 Network Requirements

- **Minimum**: 10 Mbps LAN
- **Recommended**: 100 Mbps LAN
- **Internet**: NOT REQUIRED ✅
- **Devices**: Up to 50 students per teacher PC

---

## 📊 Performance Tips

1. **Use wired connection** for teacher PC (more stable)
2. **Close unnecessary apps** on teacher PC
3. **Ensure good WiFi signal** for wireless students
4. **Limit to 30-40 students** per session for best performance
