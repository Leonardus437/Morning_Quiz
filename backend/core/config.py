"""
Centralized configuration with feature flags
"""
import os

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/exam_local.db")
    OFFLINE_MODE: bool = os.getenv("OFFLINE_MODE", "false").lower() == "true"
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "./data/exam_local.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Proctoring (Pillar C)
    PROCTORING_ENABLED: bool = os.getenv("PROCTORING_ENABLED", "true").lower() == "true"
    FORBIDDEN_PROCESSES: list = os.getenv("FORBIDDEN_PROCESSES", "chrome,firefox,teams,discord").split(",")
    KIOSK_MODE_ENABLED: bool = os.getenv("KIOSK_MODE_ENABLED", "false").lower() == "true"
    
    # Offline seeding
    SEED_ADMIN_EMAIL: str = os.getenv("SEED_ADMIN_EMAIL", "admin@offline.local")
    SEED_ADMIN_PASSWORD: str = os.getenv("SEED_ADMIN_PASSWORD", "admin123")
    
    # Tauri
    TAURI_BUILD: bool = os.getenv("TAURI_BUILD", "false").lower() == "true"
    
    @classmethod
    def is_offline_mode(cls):
        return cls.OFFLINE_MODE
    
    @classmethod
    def is_proctoring_enabled(cls):
        return cls.PROCTORING_ENABLED

settings = Settings()

# Alias for backward compatibility
Config = Settings
