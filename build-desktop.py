#!/usr/bin/env python3
"""
Desktop build script for Quiz System
Creates standalone executable with all dependencies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run command and handle errors"""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    print(f"✅ Success: {result.stdout}")
    return True

def build_desktop_app():
    """Build complete desktop application"""
    root_dir = Path(__file__).parent
    
    print("🚀 Building Quiz System Desktop Application...")
    
    # Step 1: Install Node.js dependencies
    print("\n📦 Installing Node.js dependencies...")
    if not run_command("npm install", cwd=root_dir):
        return False
    
    # Step 2: Build frontend
    print("\n🎨 Building frontend...")
    if not run_command("npm run build", cwd=root_dir / "frontend"):
        return False
    
    # Step 3: Install Python dependencies
    print("\n🐍 Installing Python dependencies...")
    if not run_command("pip install -r requirements.txt", cwd=root_dir / "backend"):
        return False
    
    # Step 4: Build backend executable
    print("\n⚙️ Building backend executable...")
    backend_cmd = f"pyinstaller --onefile --distpath {root_dir}/dist/backend --workpath {root_dir}/build/backend {root_dir}/backend/main_desktop.py"
    if not run_command(backend_cmd):
        return False
    
    # Step 5: Build Electron app
    print("\n🖥️ Building Electron application...")
    if not run_command("npm run build:electron", cwd=root_dir):
        return False
    
    print("\n🎉 Desktop application built successfully!")
    print(f"📁 Installer location: {root_dir}/dist/installers/")
    
    return True

if __name__ == "__main__":
    success = build_desktop_app()
    sys.exit(0 if success else 1)