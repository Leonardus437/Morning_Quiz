#!/usr/bin/env python3
"""
Final population script using parsed JSON
"""
import json
import sys

# Load parsed data
with open('/app/schools_parsed.json', 'r') as f:
    data = json.load(f)

def generate_trade_code(trade_name, existing_codes):
    words = trade_name.upper().split()
    if len(words) == 1:
        base_code = words[0][:10]
    else:
        base_code = '_'.join([w[:8] for w in words[:2]])
    
    code = base_code[:20]
    # Handle duplicates
    counter = 1
    while code in existing_codes:
        suffix = f"_{counter}"
        code = base_code[:20-len(suffix)] + suffix
        counter += 1
    
    return code

def assign_category(trade_name):
    trade_lower = trade_name.lower()
    
    if any(x in trade_lower for x in ['computer', 'software', 'network', 'ict', 'information', 'cyber', 'data']):
        return 'ICT & Computing'
    elif any(x in trade_lower for x in ['building', 'construction', 'masonry', 'plumbing', 'carpentry workshop']):
        return 'Construction'
    elif any(x in trade_lower for x in ['electrical', 'electronic', 'electricity', 'telecommunication']):
        return 'Electrical & Electronics'
    elif any(x in trade_lower for x in ['hotel', 'tourism', 'culinary', 'food and beverage', 'hospitality']):
        return 'Hospitality & Tourism'
    elif any(x in trade_lower for x in ['fashion', 'tailoring', 'textile', 'garment']):
        return 'Fashion & Textiles'
    elif any(x in trade_lower for x in ['hairdressing', 'beauty', 'cosmetology', 'salon']):
        return 'Beauty & Wellness'
    elif any(x in trade_lower for x in ['welding', 'metal', 'fabrication']):
        return 'Metal Work'
    elif any(x in trade_lower for x in ['wood', 'carpentry', 'joinery', 'furniture']) and 'workshop' not in trade_lower:
        return 'Wood Work'
    elif any(x in trade_lower for x in ['agriculture', 'farming', 'agri']):
        return 'Agriculture'
    elif any(x in trade_lower for x in ['automobile', 'automotive', 'motor']):
        return 'Automotive'
    elif any(x in trade_lower for x in ['manufacturing']):
        return 'Manufacturing'
    elif any(x in trade_lower for x in ['survey']):
        return 'Surveying'
    elif any(x in trade_lower for x in ['food processing']):
        return 'Food Processing'
    else:
        return 'General'

# Generate SQL
sql_statements = []

# 1. Insert provinces
province_ids = {}
pid = 1
for province_name in data['provinces'].keys():
    code = province_name.split()[0][:3].upper()
    sql_statements.append(f"INSERT INTO provinces (id, name, code) VALUES ({pid}, '{province_name}', '{code}');")
    province_ids[province_name] = pid
    pid += 1

# 2. Insert districts
district_ids = {}
did = 1
for province_name, districts in data['provinces'].items():
    for district_name in districts:
        code = district_name[:3].upper()
        sql_statements.append(f"INSERT INTO districts (id, name, code, province_id) VALUES ({did}, '{district_name}', '{code}', {province_ids[province_name]});")
        district_ids[district_name.upper()] = did
        did += 1

# 3. Collect all unique trades
all_trades = {}
for school_name, school_data in data['schools'].items():
    for trade in school_data['trades']:
        trade_name = trade['name']
        if trade_name not in all_trades:
            all_trades[trade_name] = {
                'category': assign_category(trade_name)
            }

# 4. Insert trades
trade_ids = {}
tid = 1
existing_codes = set()
for trade_name, trade_info in sorted(all_trades.items()):
    code = generate_trade_code(trade_name, existing_codes)
    existing_codes.add(code)
    code = code.replace("'", "''")
    name = trade_name.replace("'", "''")
    category = trade_info['category'].replace("'", "''")
    sql_statements.append(f"INSERT INTO trades (id, name, code, category) VALUES ({tid}, '{name}', '{code}', '{category}');")
    trade_ids[trade_name] = tid
    tid += 1

# 5. Insert schools
school_ids = {}
sid = 1
existing_school_codes = set()
for school_name, school_data in sorted(data['schools'].items()):
    district_key = school_data['district'].upper()
    if district_key not in district_ids:
        print(f"WARNING: District not found: {district_key}", file=sys.stderr)
        continue
    
    name = school_name.replace("'", "''")
    base_code = ''.join([c[0] for c in school_name.split()[:3]]).upper()[:10]
    code = base_code
    counter = 1
    while code in existing_school_codes:
        suffix = str(counter)
        code = base_code[:10-len(suffix)] + suffix
        counter += 1
    existing_school_codes.add(code)
    
    school_type = school_data['type']
    district_id = district_ids[district_key]
    
    sql_statements.append(f"INSERT INTO schools (id, name, code, district_id, school_type, is_active) VALUES ({sid}, '{name}', '{code}', {district_id}, '{school_type}', true);")
    school_ids[school_name] = sid
    sid += 1

# 6. Insert school-trade relationships
stid = 1
for school_name, school_data in sorted(data['schools'].items()):
    if school_name not in school_ids:
        continue
    
    school_id = school_ids[school_name]
    
    # Group trades by name to collect levels
    trade_levels = {}
    for trade in school_data['trades']:
        trade_name = trade['name']
        level = trade['level']
        if trade_name not in trade_levels:
            trade_levels[trade_name] = set()
        trade_levels[trade_name].add(level)
    
    # Insert relationships
    for trade_name, levels in trade_levels.items():
        if trade_name not in trade_ids:
            continue
        
        trade_id = trade_ids[trade_name]
        levels_json = json.dumps(sorted(list(levels))).replace("'", "''")
        
        sql_statements.append(f"INSERT INTO school_trades (id, school_id, trade_id, levels_offered, is_active) VALUES ({stid}, {school_id}, {trade_id}, '{levels_json}', true);")
        stid += 1

# Write SQL file
with open('/app/populate_all.sql', 'w') as f:
    f.write("-- Complete database population\n")
    f.write("-- Generated from DOCX file\n\n")
    f.write("BEGIN;\n\n")
    for stmt in sql_statements:
        f.write(stmt + "\n")
    f.write("\nCOMMIT;\n")

print(f"Generated SQL with:")
print(f"  - {len(province_ids)} provinces")
print(f"  - {len(district_ids)} districts")
print(f"  - {len(school_ids)} schools")
print(f"  - {len(trade_ids)} trades")
print(f"  - {stid-1} school-trade relationships")
print(f"\nSQL saved to /app/populate_all.sql")
