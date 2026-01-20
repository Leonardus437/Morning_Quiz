#!/usr/bin/env python3
"""
DOS Teacher Registration System
"""

import sqlite3
import hashlib
import json
from datetime import datetime

class DOSTeacherRegistration:
    def __init__(self, db_path="backend/quiz.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with DOS registration tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create DOS registration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dos_teacher_registration (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                school_name TEXT NOT NULL,
                district TEXT NOT NULL,
                sector TEXT NOT NULL,
                subject_specialization TEXT NOT NULL,
                qualification TEXT NOT NULL,
                experience_years INTEGER,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                approved_by TEXT,
                approval_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create DOS admin if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, role, full_name, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            'dos_admin',
            hashlib.sha256('dos123'.encode()).hexdigest(),
            'admin',
            'DOS Administrator',
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        print("✅ DOS registration database initialized")
    
    def register_teacher(self, teacher_data):
        """Register new teacher through DOS system"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Generate teacher ID
            teacher_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Insert into DOS registration
            cursor.execute('''
                INSERT INTO dos_teacher_registration 
                (teacher_id, full_name, email, phone, school_name, district, sector, 
                 subject_specialization, qualification, experience_years)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                teacher_id,
                teacher_data['full_name'],
                teacher_data['email'],
                teacher_data.get('phone', ''),
                teacher_data['school_name'],
                teacher_data['district'],
                teacher_data['sector'],
                teacher_data['subject_specialization'],
                teacher_data['qualification'],
                teacher_data.get('experience_years', 0)
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Teacher registered successfully with ID: {teacher_id}")
            return {"success": True, "teacher_id": teacher_id}
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"❌ Registration failed: {e}")
            return {"success": False, "error": str(e)}
    
    def approve_teacher(self, teacher_id, approved_by="dos_admin"):
        """Approve teacher and create user account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get teacher registration data
            cursor.execute('''
                SELECT * FROM dos_teacher_registration WHERE teacher_id = ?
            ''', (teacher_id,))
            
            teacher = cursor.fetchone()
            if not teacher:
                return {"success": False, "error": "Teacher not found"}
            
            # Create username from email
            email = teacher[3]  # email column
            username = email.split('@')[0]
            
            # Generate default password
            default_password = f"{teacher_id}123"
            hashed_password = hashlib.sha256(default_password.encode()).hexdigest()
            
            # Insert into users table
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (username, password, role, full_name, email, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                username,
                hashed_password,
                'teacher',
                teacher[2],  # full_name
                email,
                datetime.now().isoformat()
            ))
            
            # Update registration status
            cursor.execute('''
                UPDATE dos_teacher_registration 
                SET status = 'approved', approved_by = ?, approval_date = ?
                WHERE teacher_id = ?
            ''', (approved_by, datetime.now().isoformat(), teacher_id))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Teacher {teacher_id} approved and account created")
            return {
                "success": True,
                "username": username,
                "password": default_password,
                "teacher_id": teacher_id
            }
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"❌ Approval failed: {e}")
            return {"success": False, "error": str(e)}
    
    def list_pending_registrations(self):
        """List all pending teacher registrations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT teacher_id, full_name, email, school_name, district, 
                   subject_specialization, registration_date
            FROM dos_teacher_registration 
            WHERE status = 'pending'
            ORDER BY registration_date DESC
        ''')
        
        registrations = cursor.fetchall()
        conn.close()
        
        return registrations

def demo_dos_registration():
    """Demo DOS teacher registration system"""
    print("=== DOS TEACHER REGISTRATION DEMO ===\n")
    
    dos = DOSTeacherRegistration()
    
    # Sample teacher registration
    teacher_data = {
        "full_name": "Jean Baptiste UWIMANA",
        "email": "j.uwimana@school.rw",
        "phone": "+250788123456",
        "school_name": "Runda TSS",
        "district": "Kamonyi",
        "sector": "Runda",
        "subject_specialization": "ICT & MULTIMEDIA",
        "qualification": "Bachelor in Computer Science",
        "experience_years": 5
    }
    
    # Register teacher
    print("1. Registering new teacher...")
    result = dos.register_teacher(teacher_data)
    
    if result["success"]:
        teacher_id = result["teacher_id"]
        
        # List pending registrations
        print("\n2. Checking pending registrations...")
        pending = dos.list_pending_registrations()
        print(f"   Found {len(pending)} pending registrations")
        
        # Approve teacher
        print(f"\n3. Approving teacher {teacher_id}...")
        approval = dos.approve_teacher(teacher_id)
        
        if approval["success"]:
            print(f"   ✅ Login credentials created:")
            print(f"   Username: {approval['username']}")
            print(f"   Password: {approval['password']}")
        
    print("\n=== DOS REGISTRATION DEMO COMPLETE ===")

if __name__ == "__main__":
    demo_dos_registration()