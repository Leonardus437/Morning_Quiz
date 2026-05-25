#!/usr/bin/env python3
"""
Migration script to add hierarchical school structure
Adds: Provinces, Districts, Schools, Trades, SchoolTrades tables
"""

import os
import sys
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://quiz_user:quiz_pass123@localhost:5432/morning_quiz")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# New Models
class Province(Base):
    __tablename__ = "provinces"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class District(Base):
    __tablename__ = "districts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    province_id = Column(Integer, ForeignKey("provinces.id"))
    code = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)

class School(Base):
    __tablename__ = "schools"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True)
    province_id = Column(Integer, ForeignKey("provinces.id"))
    district_id = Column(Integer, ForeignKey("districts.id"))
    sector = Column(String(100))
    school_type = Column(String(50))  # Public, Private, Government-Aided
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True)
    category = Column(String(100))  # Automotive, ICT, Construction, etc.
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class SchoolTrade(Base):
    __tablename__ = "school_trades"
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"))
    trade_id = Column(Integer, ForeignKey("trades.id"))
    levels_offered = Column(JSON)  # ["L1", "L3", "L4", "L5"]
    is_active = Column(Boolean, default=True)
    accredited_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

def migrate():
    """Run migration"""
    print("🔄 Starting migration...")
    
    try:
        # Create new tables
        Base.metadata.create_all(bind=engine)
        print("✅ New tables created successfully")
        
        # Add columns to existing users table
        from sqlalchemy import text
        db = SessionLocal()
        
        try:
            # Add school_id column
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS school_id INTEGER REFERENCES schools(id)"))
            print("✅ Added school_id column to users")
            
            # Add trade_id column
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS trade_id INTEGER REFERENCES trades(id)"))
            print("✅ Added trade_id column to users")
            
            db.commit()
        except Exception as e:
            print(f"⚠️  Column addition: {e}")
            db.rollback()
        finally:
            db.close()
        
        # Seed initial data
        seed_data()
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

def seed_data():
    """Seed initial provinces, districts, and sample data"""
    print("\n📊 Seeding initial data...")
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_provinces = db.query(Province).count()
        if existing_provinces > 0:
            print("⚠️  Data already exists, skipping seed")
            return
        
        # Add Provinces
        provinces_data = [
            {"name": "Kigali City", "code": "KGL"},
            {"name": "Eastern Province", "code": "EST"},
            {"name": "Northern Province", "code": "NTH"},
            {"name": "Southern Province", "code": "STH"},
            {"name": "Western Province", "code": "WST"}
        ]
        
        provinces = {}
        for prov_data in provinces_data:
            prov = Province(**prov_data)
            db.add(prov)
            db.flush()
            provinces[prov_data["code"]] = prov.id
            print(f"  ✅ Added province: {prov_data['name']}")
        
        # Add Sample Districts
        districts_data = [
            {"name": "Gasabo", "province_id": provinces["KGL"], "code": "GSB"},
            {"name": "Kicukiro", "province_id": provinces["KGL"], "code": "KCK"},
            {"name": "Nyarugenge", "province_id": provinces["KGL"], "code": "NYR"},
            {"name": "Bugesera", "province_id": provinces["EST"], "code": "BGS"},
            {"name": "Kayonza", "province_id": provinces["EST"], "code": "KYZ"},
            {"name": "Musanze", "province_id": provinces["NTH"], "code": "MSZ"},
            {"name": "Gicumbi", "province_id": provinces["NTH"], "code": "GCM"},
            {"name": "Huye", "province_id": provinces["STH"], "code": "HYE"},
            {"name": "Muhanga", "province_id": provinces["STH"], "code": "MHG"},
            {"name": "Rusizi", "province_id": provinces["WST"], "code": "RSZ"},
            {"name": "Rubavu", "province_id": provinces["WST"], "code": "RBV"}
        ]
        
        districts = {}
        for dist_data in districts_data:
            dist = District(**dist_data)
            db.add(dist)
            db.flush()
            districts[dist_data["code"]] = dist.id
            print(f"  ✅ Added district: {dist_data['name']}")
        
        # Add Sample Schools
        schools_data = [
            {
                "name": "IPRC Kigali",
                "code": "IPRC-KGL",
                "province_id": provinces["KGL"],
                "district_id": districts["GSB"],
                "sector": "Kacyiru",
                "school_type": "Public"
            },
            {
                "name": "IPRC Musanze",
                "code": "IPRC-MSZ",
                "province_id": provinces["NTH"],
                "district_id": districts["MSZ"],
                "sector": "Muhoza",
                "school_type": "Public"
            },
            {
                "name": "IPRC Huye",
                "code": "IPRC-HYE",
                "province_id": provinces["STH"],
                "district_id": districts["HYE"],
                "sector": "Ngoma",
                "school_type": "Public"
            }
        ]
        
        schools = {}
        for school_data in schools_data:
            school = School(**school_data)
            db.add(school)
            db.flush()
            schools[school_data["code"]] = school.id
            print(f"  ✅ Added school: {school_data['name']}")
        
        # Add Sample Trades
        trades_data = [
            {"name": "Software Development", "code": "SWD", "category": "ICT & Computing"},
            {"name": "Computer System and Architecture", "code": "CSA", "category": "ICT & Computing"},
            {"name": "Networking", "code": "NET", "category": "ICT & Computing"},
            {"name": "Automotive Engine Technology", "code": "AET", "category": "Automotive"},
            {"name": "Auto Electricity and Electronics", "code": "AEE", "category": "Automotive"},
            {"name": "Building Construction", "code": "BDC", "category": "Construction"},
            {"name": "Masonry", "code": "MSN", "category": "Construction"},
            {"name": "Carpentry", "code": "CRP", "category": "Construction"},
            {"name": "Domestic Electricity", "code": "DEL", "category": "Electrical & Electronics"},
            {"name": "Industrial Electricity", "code": "IEL", "category": "Electrical & Electronics"},
            {"name": "Culinary Arts", "code": "CUL", "category": "Hospitality & Culinary"},
            {"name": "Hotel Management", "code": "HTL", "category": "Hospitality & Culinary"},
            {"name": "Welding", "code": "WLD", "category": "Metal Work"},
            {"name": "Plumbing", "code": "PLM", "category": "Construction"},
            {"name": "Fashion Design", "code": "FSD", "category": "Fashion & Textiles"}
        ]
        
        trades = {}
        for trade_data in trades_data:
            trade = Trade(**trade_data)
            db.add(trade)
            db.flush()
            trades[trade_data["code"]] = trade.id
            print(f"  ✅ Added trade: {trade_data['name']}")
        
        # Map trades to schools
        school_trades_data = [
            # IPRC Kigali
            {"school_id": schools["IPRC-KGL"], "trade_id": trades["SWD"], "levels_offered": ["L3", "L4", "L5"]},
            {"school_id": schools["IPRC-KGL"], "trade_id": trades["CSA"], "levels_offered": ["L3", "L4", "L5"]},
            {"school_id": schools["IPRC-KGL"], "trade_id": trades["NET"], "levels_offered": ["L4", "L5"]},
            {"school_id": schools["IPRC-KGL"], "trade_id": trades["DEL"], "levels_offered": ["L1", "L3"]},
            
            # IPRC Musanze
            {"school_id": schools["IPRC-MSZ"], "trade_id": trades["AET"], "levels_offered": ["L3", "L4", "L5"]},
            {"school_id": schools["IPRC-MSZ"], "trade_id": trades["AEE"], "levels_offered": ["L4", "L5"]},
            {"school_id": schools["IPRC-MSZ"], "trade_id": trades["BDC"], "levels_offered": ["L3", "L4"]},
            {"school_id": schools["IPRC-MSZ"], "trade_id": trades["WLD"], "levels_offered": ["L1", "L3"]},
            
            # IPRC Huye
            {"school_id": schools["IPRC-HYE"], "trade_id": trades["CUL"], "levels_offered": ["L3", "L4", "L5"]},
            {"school_id": schools["IPRC-HYE"], "trade_id": trades["HTL"], "levels_offered": ["L4", "L5"]},
            {"school_id": schools["IPRC-HYE"], "trade_id": trades["FSD"], "levels_offered": ["L3", "L4"]},
            {"school_id": schools["IPRC-HYE"], "trade_id": trades["CRP"], "levels_offered": ["L1", "L3"]}
        ]
        
        for st_data in school_trades_data:
            school_trade = SchoolTrade(**st_data)
            db.add(school_trade)
        
        print(f"  ✅ Mapped trades to schools")
        
        db.commit()
        print("\n✅ Initial data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
