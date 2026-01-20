# 🖥️ Desktop Application Build Guide

## Prerequisites
- Node.js 18+ installed
- Python 3.9+ installed
- Git installed

## Quick Build (Automated)

```bash
# 1. Install desktop dependencies
npm install

# 2. Install Python desktop requirements
pip install -r requirements-desktop.txt

# 3. Build everything automatically
python build-desktop.py
```

## Manual Build Steps

### Step 1: Install Dependencies
```bash
# Node.js dependencies
npm install

# Python dependencies  
pip install -r requirements-desktop.txt
```

### Step 2: Build Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### Step 3: Build Backend Executable
```bash
pyinstaller --onefile --distpath dist/backend backend/main_desktop.py
```

### Step 4: Build Desktop App
```bash
npm run build:electron
```

## Output Files
- **Installer**: `dist/installers/Quiz System Setup.exe`
- **Portable**: `dist/win-unpacked/Quiz System.exe`

## Installation Size
- Installer: ~80-120MB
- Installed: ~200-300MB

## Features Included
✅ Complete offline functionality
✅ All user roles (Admin/Teacher/Student)
✅ Question shuffling & anti-cheating
✅ File upload/processing (PDF/Excel)
✅ Export capabilities (PDF/Excel)
✅ Local database (SQLite)
✅ No internet required

## Distribution
- Share the installer file with users
- Single-click installation
- Desktop shortcut created automatically
- Uninstaller included