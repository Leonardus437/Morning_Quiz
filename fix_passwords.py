import bcrypt
import psycopg2
import sys

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def fix_passwords():
    try:
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="morning_quiz",
            user="quiz_user",
            password="quiz_pass123"
        )
        cursor = conn.cursor()
        
        # Generate correct hash for "pass123"
        correct_hash = hash_password("pass123")
        print(f"Generated hash: {correct_hash}")
        
        # Update all users with correct password hash
        cursor.execute("UPDATE users SET password_hash = %s", (correct_hash,))
        
        # Commit changes
        conn.commit()
        
        # Verify update
        cursor.execute("SELECT username, role FROM users")
        users = cursor.fetchall()
        
        print(f"✅ Updated passwords for {len(users)} users:")
        for username, role in users:
            print(f"  - {username} ({role})")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Password fix complete! All users now use password: pass123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_passwords()