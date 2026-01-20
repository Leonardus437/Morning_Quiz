from backend.main import SessionLocal, User, hash_password_simple

db = SessionLocal()

# Get admin user
admin = db.query(User).filter(User.username == "admin").first()

if admin:
    # Reset password to pass123
    admin.password_hash = hash_password_simple("pass123")
    db.commit()
    print("✅ Admin password reset to 'pass123'")
    print(f"Username: {admin.username}")
    print(f"Role: {admin.role}")
else:
    print("❌ Admin user not found")

db.close()
