import hashlib
import secrets

def hash_password_simple(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

# Generate hash for UWIZERA001
password = "UWIZERA001"
hashed = hash_password_simple(password)
print(f"Password hash for '{password}': {hashed}")
