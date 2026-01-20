# 🔧 Network Access Fix - ERR_CONNECTION_TIMED_OUT

## ⚠️ Problem
Cannot access `http://192.168.183.61:3000` from browser
Error: `ERR_CONNECTION_TIMED_OUT`

## ✅ SOLUTION (3 Steps)

### Step 1: Add Firewall Rules (Run as Administrator)

**Right-click Command Prompt → Run as Administrator**

```cmd
netsh advfirewall firewall add rule name="Morning Quiz Frontend" dir=in action=allow protocol=TCP localport=3000

netsh advfirewall firewall add rule name="Morning Quiz Backend" dir=in action=allow protocol=TCP localport=8000
```

### Step 2: Test Local Access

```cmd
curl http://localhost:3000
```

Should show HTML content (not error)

### Step 3: Test Network Access

From another device on same network:
```
http://192.168.183.61:3000
```

---

## 🚀 QUICK FIX (If Above Doesn't Work)

### Option 1: Temporarily Disable Firewall (Testing Only)

1. Open **Windows Security**
2. Go to **Firewall & network protection**
3. Click your active network (Private/Public)
4. Turn **OFF** Windows Defender Firewall
5. Test access: `http://192.168.183.61:3000`
6. **Turn firewall back ON** after testing

### Option 2: Use Localhost (On Same PC)

```
http://localhost:3000
http://localhost:3000/admin
```

---

## 🔍 DIAGNOSIS

### Check 1: Containers Running?
```cmd
docker ps
```
Should show 3 containers: frontend, backend, db

### Check 2: Frontend Responding Locally?
```cmd
curl http://localhost:3000
```
Should return HTML (not error)

### Check 3: Port 3000 Listening?
```cmd
netstat -ano | findstr :3000
```
Should show: `0.0.0.0:3000` or `[::]:3000`

### Check 4: Same Network?
- PC and device must be on **same WiFi/LAN**
- Check WiFi name on both devices

---

## 🛠️ TROUBLESHOOTING

### Issue: Firewall Blocking

**Solution:**
```cmd
# Run as Administrator
netsh advfirewall firewall add rule name="Morning Quiz" dir=in action=allow protocol=TCP localport=3000,8000
```

### Issue: Wrong IP Address

**Get Current IP:**
```cmd
ipconfig
```
Look for **IPv4 Address** under your active network adapter

**Use New IP:**
```
http://[NEW-IP]:3000
```

### Issue: Containers Not Running

**Restart:**
```cmd
docker-compose restart
```

### Issue: Port Already in Use

**Check:**
```cmd
netstat -ano | findstr :3000
```

**Kill Process:**
```cmd
taskkill /PID [PID_NUMBER] /F
docker-compose restart frontend
```

---

## ✅ VERIFICATION STEPS

### 1. Local Access (Same PC)
```
✓ http://localhost:3000 - Should work
✓ http://127.0.0.1:3000 - Should work
```

### 2. Network Access (Other Devices)
```
✓ http://192.168.183.61:3000 - Should work
✓ Devices on same WiFi
✓ Firewall rules added
```

### 3. Admin Panel
```
✓ http://localhost:3000/admin
✓ Login: admin / admin123
```

---

## 🎯 COMPLETE FIX PROCEDURE

### Step-by-Step:

1. **Open Command Prompt as Administrator**
   - Press `Win + X`
   - Select "Command Prompt (Admin)" or "PowerShell (Admin)"

2. **Add Firewall Rules**
   ```cmd
   netsh advfirewall firewall add rule name="Morning Quiz Frontend" dir=in action=allow protocol=TCP localport=3000
   netsh advfirewall firewall add rule name="Morning Quiz Backend" dir=in action=allow protocol=TCP localport=8000
   ```

3. **Verify Rules Added**
   ```cmd
   netsh advfirewall firewall show rule name="Morning Quiz Frontend"
   ```

4. **Test Local Access**
   ```cmd
   curl http://localhost:3000
   ```

5. **Get Your IP**
   ```cmd
   ipconfig | findstr IPv4
   ```

6. **Test from Another Device**
   - Connect to same WiFi
   - Open browser
   - Go to: `http://[YOUR-IP]:3000`

---

## 🔥 EMERGENCY FIX (If Nothing Works)

### Temporarily Disable All Firewalls:

1. **Windows Firewall:**
   - Windows Security → Firewall → Turn OFF

2. **Antivirus Firewall:**
   - Check your antivirus settings
   - Temporarily disable firewall

3. **Test Access:**
   - Try `http://192.168.183.61:3000`

4. **If Works:**
   - Problem is firewall
   - Add proper rules
   - Re-enable firewall

5. **If Still Doesn't Work:**
   - Check network connection
   - Verify same WiFi/LAN
   - Restart router

---

## 📱 ACCESS FROM PHONE/TABLET

### Requirements:
1. ✅ Phone connected to **same WiFi** as PC
2. ✅ Firewall rules added on PC
3. ✅ Docker containers running

### Steps:
1. **Turn OFF mobile data** on phone
2. **Connect to same WiFi** as PC
3. **Open browser** (Chrome/Safari)
4. **Enter:** `http://192.168.183.61:3000`
5. **Should load** Morning Quiz homepage

---

## 🎯 FINAL CHECKLIST

Before accessing from network:
- [ ] Docker containers running (`docker ps`)
- [ ] Firewall rules added (as Administrator)
- [ ] Local access works (`http://localhost:3000`)
- [ ] Correct IP address (`ipconfig`)
- [ ] Same WiFi/LAN network
- [ ] Mobile data OFF (on phone)

---

## 💡 QUICK COMMANDS

### Check Everything:
```cmd
# Containers
docker ps

# Local access
curl http://localhost:3000

# IP address
ipconfig | findstr IPv4

# Port listening
netstat -ano | findstr :3000

# Firewall rules
netsh advfirewall firewall show rule name=all | findstr "Morning Quiz"
```

### Fix Everything:
```cmd
# As Administrator
netsh advfirewall firewall add rule name="Morning Quiz" dir=in action=allow protocol=TCP localport=3000,8000

# Restart
docker-compose restart

# Test
curl http://localhost:3000
```

---

## ✅ SUCCESS CRITERIA

System is accessible when:
1. ✅ `http://localhost:3000` works on PC
2. ✅ `http://192.168.183.61:3000` works from phone
3. ✅ No firewall errors
4. ✅ No timeout errors
5. ✅ Login page loads

---

## 🆘 STILL NOT WORKING?

### Last Resort:

1. **Restart Everything:**
   ```cmd
   docker-compose down
   docker-compose up -d
   ```

2. **Restart PC**

3. **Check Router:**
   - Ensure devices can communicate
   - Check AP isolation is OFF
   - Verify same subnet

4. **Use Localhost:**
   - Access only from PC: `http://localhost:3000`
   - Share screen with students (temporary)

---

## 📞 SUPPORT

If still having issues, check:
1. Windows Firewall settings
2. Antivirus firewall settings
3. Router configuration
4. Network adapter settings
5. Docker network settings

**Most Common Fix: Add firewall rules as Administrator!** ✅
