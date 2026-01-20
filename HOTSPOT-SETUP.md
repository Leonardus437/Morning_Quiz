# Phone Hotspot Setup Guide

## Why Students Can't Connect

Even on phone hotspot, students need:
1. ✅ Windows Firewall rules (MOST COMMON ISSUE)
2. ✅ Correct IP address
3. ✅ All devices on same hotspot
4. ✅ Hotspot settings configured correctly

## Quick Fix (Do This Now)

### Step 1: Run Diagnostic Tool
1. Right-click `diagnose-and-fix.bat`
2. Select **"Run as administrator"**
3. Wait for it to complete
4. Copy the URL it shows

### Step 2: Test on Teacher PC
1. Open browser on your PC
2. Go to the URL from Step 1 (e.g., `http://192.168.61.61:3000`)
3. If you see the quiz page → Good! Continue to Step 3
4. If you DON'T see it → Docker is not running, restart Docker Desktop

### Step 3: Configure Phone Hotspot
**On your phone:**
1. Go to Settings → Hotspot/Tethering
2. Enable "Allow all devices" or "Maximum compatibility mode"
3. Disable "AP Isolation" if you see this option
4. Note the hotspot name and password

### Step 4: Connect All Devices
1. Connect teacher PC to your phone hotspot
2. Connect all student devices to the SAME hotspot
3. Wait 10 seconds for connections to stabilize

### Step 5: Share URL with Students
Give students the URL from Step 1:
```
http://192.168.61.61:3000
```
(Your actual IP may be different)

## Common Issues & Solutions

### Issue 1: "This site can't be reached"
**Cause:** Windows Firewall blocking ports
**Fix:** Run `diagnose-and-fix.bat` as Administrator

### Issue 2: Students see the page but can't login
**Cause:** Backend port (8000) is blocked
**Fix:** Run `diagnose-and-fix.bat` as Administrator

### Issue 3: IP address keeps changing
**Cause:** Switching between networks
**Fix:** 
- Stay on ONE network (hotspot)
- Run `diagnose-and-fix.bat` after switching networks
- Share the NEW URL with students

### Issue 4: Works on teacher PC but not on student devices
**Possible causes:**
1. Students typing wrong URL (check for typos)
2. Students on different network
3. Student device has VPN enabled
4. Antivirus blocking connection

**Fix:**
- Double-check URL (no spaces, correct IP)
- Verify all on same hotspot
- Disable VPN on student devices
- Temporarily disable antivirus

### Issue 5: Some students can connect, others can't
**Cause:** Mixed network connections
**Fix:**
- Disconnect ALL devices from other networks
- Connect ONLY to your phone hotspot
- Restart student devices if needed

## Phone Hotspot Settings

### Android
1. Settings → Network & Internet → Hotspot & Tethering
2. Enable "Wi-Fi hotspot"
3. Tap "Advanced" or "Configure"
4. Set "AP Band" to 2.4 GHz (better compatibility)
5. Disable "Turn off hotspot automatically"

### iPhone
1. Settings → Personal Hotspot
2. Enable "Allow Others to Join"
3. Set "Maximize Compatibility" to ON
4. Keep the Settings screen open while students connect

## Testing Checklist

Before students arrive:
- [ ] Docker Desktop is running
- [ ] Run `diagnose-and-fix.bat` as Administrator
- [ ] Phone hotspot is enabled
- [ ] Teacher PC connected to hotspot
- [ ] Test URL works on teacher PC
- [ ] Write URL on whiteboard for students

During class:
- [ ] Students connect to hotspot (one at a time)
- [ ] Students type URL exactly as shown
- [ ] Students can see login page
- [ ] Students can login successfully

## Manual Firewall Configuration

If `diagnose-and-fix.bat` doesn't work, add rules manually:

1. Open Command Prompt as Administrator
2. Run these commands:

```cmd
netsh advfirewall firewall add rule name="TVET Quiz Port 3000" dir=in action=allow protocol=TCP localport=3000

netsh advfirewall firewall add rule name="TVET Quiz Port 8000" dir=in action=allow protocol=TCP localport=8000
```

## Verify Firewall Rules

Check if rules are active:
```cmd
netsh advfirewall firewall show rule name="TVET Quiz Port 3000"
netsh advfirewall firewall show rule name="TVET Quiz Port 8000"
```

Should show "Enabled: Yes" and "Action: Allow"

## Network Diagram

```
[Your Phone Hotspot]
        |
        |--- [Teacher PC] (192.168.61.61)
        |         |
        |         +--- Docker (Quiz System)
        |
        |--- [Student 1 Phone/Laptop]
        |--- [Student 2 Phone/Laptop]
        |--- [Student 3 Phone/Laptop]
        ...
```

All devices must be connected to YOUR phone hotspot!

## Data Usage

Don't worry about data usage:
- Quiz system is 100% offline
- No internet connection needed
- Only local network communication
- Typical usage: < 1MB per student per quiz

## Maximum Students

Phone hotspot limits:
- Android: Usually 10-15 devices
- iPhone: Usually 5-10 devices

If you have more students:
- Use a WiFi router instead
- Or run multiple quiz sessions

## Still Not Working?

1. Restart Docker Desktop
2. Restart your PC
3. Run `diagnose-and-fix.bat` again
4. Test on teacher PC first
5. If teacher PC works, issue is with student devices

## Contact Info

If nothing works, check:
- Docker Desktop is running (green icon in system tray)
- All containers are running: `docker ps`
- You can access `http://localhost:3000` on teacher PC
