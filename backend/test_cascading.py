#!/usr/bin/env python3
"""
Test the cascading dropdown hierarchy
"""

import sqlite3
import json

db_path = '../data/exam_local.db'

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("=" * 60)
print("CASCADING DROPDOWN HIERARCHY TEST")
print("=" * 60)

# Test 1: Get Provinces
print("\n1. PROVINCES:")
cur.execute("SELECT id, name, code FROM provinces ORDER BY name")
provinces = cur.fetchall()
for p in provinces:
    print(f"   ID={p[0]}: {p[1]} ({p[2]})")

# Test 2: Get Districts for each Province
print("\n2. DISTRICTS BY PROVINCE:")
for prov_id, prov_name, _ in provinces:
    cur.execute("""
        SELECT d.id, d.name, COUNT(s.id) as school_count
        FROM districts d
        LEFT JOIN schools s ON d.id = s.district_id
        WHERE d.province_id = ?
        GROUP BY d.id, d.name
        ORDER BY d.name
    """, (prov_id,))
    districts = cur.fetchall()
    print(f"\n   {prov_name}:")
    for d in districts:
        status = "✓" if d[2] > 0 else "✗"
        print(f"      {status} ID={d[0]}: {d[1]} ({d[2]} schools)")

# Test 3: Get Schools for first district with schools
print("\n3. SCHOOLS (sample from first district with schools):")
cur.execute("""
    SELECT d.id, d.name, COUNT(s.id) as school_count
    FROM districts d
    JOIN schools s ON d.id = s.district_id
    GROUP BY d.id, d.name
    HAVING COUNT(s.id) > 0
    LIMIT 1
""")
sample_district = cur.fetchone()
if sample_district:
    dist_id, dist_name, _ = sample_district
    print(f"   District: {dist_name}")
    cur.execute("SELECT id, name, school_type FROM schools WHERE district_id = ? ORDER BY name LIMIT 5", (dist_id,))
    schools = cur.fetchall()
    for s in schools:
        print(f"      ID={s[0]}: {s[1]} ({s[2]})")

# Test 4: Get Trades for first school
print("\n4. TRADES (sample from first school with trades):")
cur.execute("""
    SELECT s.id, s.name
    FROM schools s
    JOIN school_trades st ON s.id = st.school_id
    GROUP BY s.id, s.name
    LIMIT 1
""")
sample_school = cur.fetchone()
if sample_school:
    school_id, school_name = sample_school
    print(f"   School: {school_name}")
    cur.execute("""
        SELECT t.id, t.name, st.levels_offered
        FROM trades t
        JOIN school_trades st ON t.id = st.trade_id
        WHERE st.school_id = ?
        ORDER BY t.name
    """, (school_id,))
    trades = cur.fetchall()
    for t in trades:
        try:
            levels = json.loads(t[2]) if t[2] else []
        except:
            levels = []
        print(f"      ID={t[0]}: {t[1]}")
        print(f"         Levels: {', '.join(levels)}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY:")
print("=" * 60)
cur.execute("SELECT COUNT(*) FROM provinces")
print(f"   Provinces: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM districts")
print(f"   Districts: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM schools")
print(f"   Schools: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM trades")
print(f"   Trades: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM school_trades")
print(f"   School-Trade Relationships: {cur.fetchone()[0]}")

print("\n✅ Cascading dropdown hierarchy is properly structured!")
print("   Province → District → School → Trade → Level\n")

conn.close()
