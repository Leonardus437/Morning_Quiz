import os
import sys
from sqlalchemy import create_engine, text
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import secrets
import hashlib

# Database connection
DATABASE_URL = "postgresql://quiz_user:QuizSecure2025!Rwanda@db:5432/morning_quiz"
engine = create_engine(DATABASE_URL)

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def generate_username(school_name: str, school_id: int) -> str:
    """Generate username from school name"""
    # Remove special characters and get first letters
    words = school_name.upper().replace("TSS", "").replace("VTC", "").replace("IPRC", "").split()
    
    # Take first 3 letters of first word and first 2 of second word if exists
    if len(words) >= 2:
        username = f"{words[0][:3]}{words[1][:2]}".lower()
    elif len(words) == 1:
        username = words[0][:5].lower()
    else:
        username = f"school{school_id}"
    
    # Add DOS suffix
    username = f"dos_{username}"
    
    return username

def generate_password() -> str:
    """Generate secure random password"""
    # Format: DOS2025 + 4 random chars
    random_part = secrets.token_urlsafe(4)[:4].upper()
    return f"DOS2025{random_part}"

def generate_dos_credentials():
    """Generate DOS credentials for all schools"""
    print("🔐 Generating School DOS Credentials...")
    
    with engine.connect() as conn:
        # Get all schools organized by district
        result = conn.execute(text("""
            SELECT 
                p.name as province_name,
                d.name as district_name,
                s.id as school_id,
                s.name as school_name,
                s.code as school_code,
                s.school_type
            FROM schools s
            JOIN districts d ON s.district_id = d.id
            JOIN provinces p ON s.province_id = p.id
            WHERE s.is_active = true
            ORDER BY p.name, d.name, s.name
        """))
        
        schools = []
        for row in result:
            username = generate_username(row[3], row[2])
            password = generate_password()
            
            schools.append({
                'province': row[0],
                'district': row[1],
                'school_id': row[2],
                'school_name': row[3],
                'school_code': row[4],
                'school_type': row[5],
                'username': username,
                'password': password,
                'password_hash': hash_password(password)
            })
        
        print(f"✅ Generated credentials for {len(schools)} schools")
        
        # Insert DOS accounts into database
        print("💾 Inserting DOS accounts into database...")
        for school in schools:
            # Check if user already exists
            existing = conn.execute(text("""
                SELECT id FROM users WHERE username = :username
            """), {'username': school['username']}).first()
            
            if not existing:
                conn.execute(text("""
                    INSERT INTO users (username, password_hash, role, full_name, school_id)
                    VALUES (:username, :password_hash, 'admin', :full_name, :school_id)
                """), {
                    'username': school['username'],
                    'password_hash': school['password_hash'],
                    'full_name': f"DOS - {school['school_name']}",
                    'school_id': school['school_id']
                })
        
        conn.commit()
        print("✅ DOS accounts created in database")
        
        return schools

def create_pdf(schools):
    """Create PDF with all DOS credentials organized by district"""
    print("📄 Creating PDF document...")
    
    filename = "SCHOOL_DOS_CREDENTIALS_ALL_DISTRICTS.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a5490'),
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    district_header_style = ParagraphStyle(
        'DistrictHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    warning_style = ParagraphStyle(
        'Warning',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.red,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    # Title page
    elements.append(Paragraph("🇷🇼 RWANDA TVET QUIZ SYSTEM", title_style))
    elements.append(Paragraph("School DOS Credentials - All Districts", subtitle_style))
    elements.append(Paragraph("⚠️ CONFIDENTIAL - FOR AUTHORIZED PERSONNEL ONLY", warning_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary info
    total_schools = len(schools)
    districts = {}
    for school in schools:
        district = school['district']
        if district not in districts:
            districts[district] = []
        districts[district].append(school)
    
    summary_data = [
        ['Total Schools:', str(total_schools)],
        ['Total Districts:', str(len(districts))],
        ['Document Date:', '2025-01-13'],
        ['System:', 'Rwanda TVET Quiz System']
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
    ]))
    
    elements.append(summary_table)
    elements.append(PageBreak())
    
    # Credentials by district
    for district_name in sorted(districts.keys()):
        district_schools = districts[district_name]
        province_name = district_schools[0]['province']
        
        # District header
        elements.append(Paragraph(f"{district_name} District - {province_name} Province ({len(district_schools)} schools)", district_header_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Table header
        data = [['#', 'School Name', 'Type', 'Username', 'Password']]
        
        # Add schools
        for idx, school in enumerate(sorted(district_schools, key=lambda x: x['school_name']), 1):
            data.append([
                str(idx),
                school['school_name'][:35],  # Truncate long names
                school['school_type'],
                school['username'],
                school['password']
            ])
        
        # Create table
        table = Table(data, colWidths=[0.4*inch, 2.8*inch, 0.6*inch, 1.3*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Center # column
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Footer instructions
    elements.append(PageBreak())
    elements.append(Paragraph("📋 INSTRUCTIONS FOR SCHOOL DOS", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    instructions = [
        "1. Each School DOS account has full administrative access to their school",
        "2. DOS can create and manage Trainer (Teacher) accounts",
        "3. DOS can upload and manage Trainee (Student) lists",
        "4. DOS can view all quiz results and performance reports",
        "5. Keep these credentials secure and confidential",
        "6. Change password after first login (recommended)",
        "7. Access the system at: http://[SERVER-IP]:3000/hierarchical-login",
        "8. Select 'School DOS' role during login"
    ]
    
    for instruction in instructions:
        elements.append(Paragraph(instruction, styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(elements)
    print(f"✅ PDF created: {filename}")
    return filename

if __name__ == "__main__":
    try:
        # Generate credentials
        schools = generate_dos_credentials()
        
        # Create PDF
        pdf_file = create_pdf(schools)
        
        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print(f"📄 PDF File: {pdf_file}")
        print(f"🏫 Total Schools: {len(schools)}")
        print(f"🔐 All DOS accounts created in database")
        print("\n⚠️  IMPORTANT: Keep this PDF secure and confidential!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
