"""
RTB Integration Script for Morning Quiz System
Integrates RTB pedagogical templates with the existing quiz system
"""

import os
import sys
import shutil
from pathlib import Path

def integrate_rtb_with_morning_quiz():
    """Integrate RTB functionality with the existing Morning Quiz system"""
    
    print("[SETUP] Starting RTB Integration with Morning Quiz System...")
    
    # Check if we're in the right directory
    if not os.path.exists('docker-compose.yml'):
        print("[ERROR] Please run this script from the Morning Quiz root directory")
        return False
    
    # 1. Update main.py to include RTB endpoints
    print("[UPDATE] Updating backend main.py...")
    update_main_py()
    
    # 2. Add RTB route to frontend
    print("[WEB] Adding RTB interface route...")
    add_rtb_frontend_route()
    
    # 3. Update navigation
    print("[NAV] Updating navigation...")
    update_navigation()
    
    # 4. Create RTB database tables
    print("[DB] Setting up RTB database tables...")
    setup_rtb_database()
    
    # 5. Add RTB to Docker setup
    print("[DOCKER] Updating Docker configuration...")
    update_docker_config()
    
    print("[SUCCESS] RTB Integration completed successfully!")
    print("\n[NEXT] Next steps:")
    print("1. Restart the system: docker-compose down && docker-compose up -d")
    print("2. Access RTB interface at: http://localhost:3000/rtb")
    print("3. Admin panel now includes RTB management")
    
    return True

def update_main_py():
    """Update the main.py file to include RTB endpoints"""
    
    main_py_path = Path('backend/main.py')
    
    if not main_py_path.exists():
        print("❌ backend/main.py not found")
        return
    
    # Read current main.py
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add RTB imports at the top
    rtb_imports = """
# RTB Integration
from rtb_api_endpoints import RTBAPIEndpoints
"""
    
    # Add RTB initialization after app creation
    rtb_init = """
# Initialize RTB endpoints
rtb_endpoints = RTBAPIEndpoints(app, 'quiz.db')
"""
    
    # Check if RTB is already integrated
    if 'RTBAPIEndpoints' in content:
        print("[INFO] RTB already integrated in main.py")
        return
    
    # Find the right place to add imports (after existing imports)
    import_section = content.find('from flask import')
    if import_section != -1:
        # Find the end of imports
        lines = content.split('\n')
        insert_line = 0
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                insert_line = i + 1
        
        lines.insert(insert_line, rtb_imports.strip())
        content = '\n'.join(lines)
    
    # Find where to add RTB initialization (after app creation)
    app_creation = content.find("app = Flask(__name__)")
    if app_creation != -1:
        # Find the next line after app configuration
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'app.secret_key' in line or 'app.config' in line:
                lines.insert(i + 1, rtb_init.strip())
                break
        content = '\n'.join(lines)
    
    # Write updated content
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[SUCCESS] Updated main.py with RTB endpoints")

def add_rtb_frontend_route():
    """Add RTB interface route to the frontend"""
    
    # Copy RTB interface to frontend static directory
    frontend_static = Path('frontend/static')
    if frontend_static.exists():
        shutil.copy('rtb_interface.html', frontend_static / 'rtb.html')
        print("[SUCCESS] Added RTB interface to frontend")
    
    # Update main.py to serve RTB interface
    main_py_path = Path('backend/main.py')
    
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    rtb_route = """
@app.route('/rtb')
def rtb_interface():
    return send_from_directory('../frontend/static', 'rtb.html')
"""
    
    if '@app.route(\'/rtb\')' not in content:
        # Add the route before the main block
        if 'if __name__ == \'__main__\':' in content:
            content = content.replace('if __name__ == \'__main__\':', rtb_route + '\nif __name__ == \'__main__\':')
        else:
            content += rtb_route
        
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("[SUCCESS] Added RTB route to backend")

def update_navigation():
    """Update navigation to include RTB link"""
    
    # Find and update navigation files
    nav_files = [
        'frontend/src/routes/admin/+layout.svelte',
        'frontend/src/routes/+layout.svelte'
    ]
    
    for nav_file in nav_files:
        nav_path = Path(nav_file)
        if nav_path.exists():
            with open(nav_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add RTB link to navigation
            rtb_nav = '<a href="/rtb" class="nav-link">RTB Templates</a>'
            
            if 'RTB Templates' not in content:
                # Find navigation section and add RTB link
                if '<nav' in content and '</nav>' in content:
                    nav_end = content.find('</nav>')
                    content = content[:nav_end] + f'    {rtb_nav}\n' + content[nav_end:]
                    
                    with open(nav_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"[SUCCESS] Updated navigation in {nav_file}")

def setup_rtb_database():
    """Setup RTB database tables"""
    
    setup_script = """
import sqlite3
import sys
import os

# Add backend to path
sys.path.append('backend')

try:
    from rtb_quiz_integration import RTBQuizIntegration
    
    # Initialize RTB integration (this will create tables)
    rtb_integration = RTBQuizIntegration('backend/quiz.db')
    print("[SUCCESS] RTB database tables created successfully")
    
except Exception as e:
    print(f"[ERROR] Error setting up RTB database: {e}")
"""
    
    # Write and execute setup script
    with open('setup_rtb_db.py', 'w') as f:
        f.write(setup_script)
    
    os.system('python setup_rtb_db.py')
    os.remove('setup_rtb_db.py')

def update_docker_config():
    """Update Docker configuration for RTB"""
    
    # Check if docker-compose.yml needs RTB-specific updates
    docker_compose_path = Path('docker-compose.yml')
    
    if docker_compose_path.exists():
        with open(docker_compose_path, 'r') as f:
            content = f.read()
        
        # Add RTB volume mapping if needed
        rtb_volume = '      - ./rtb_templates:/app/rtb_templates'
        
        if 'rtb_templates' not in content:
            # Find backend service volumes section
            if 'backend:' in content and 'volumes:' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'volumes:' in line and i > 0:
                        # Check if this is under backend service
                        for j in range(i-1, -1, -1):
                            if 'backend:' in lines[j]:
                                lines.insert(i+1, rtb_volume)
                                break
                        break
                
                content = '\n'.join(lines)
                
                with open(docker_compose_path, 'w') as f:
                    f.write(content)
                
                print("[SUCCESS] Updated Docker configuration")
    
    # Create RTB templates directory
    rtb_templates_dir = Path('rtb_templates')
    rtb_templates_dir.mkdir(exist_ok=True)
    
    # Create sample templates
    create_sample_templates()

def create_sample_templates():
    """Create sample RTB templates"""
    
    sample_session_plan = """
# Sample RTB Session Plan Template

**Sector:** ICT & MULTIMEDIA
**Sub-sector:** Software Development
**Lead Trainer's name:** [TRAINER NAME]
**Date:** [DATE]
**Term:** [TERM]
**Module:** [MODULE CODE & NAME]
**Week:** [WEEK]
**No. Learners:** [NUMBER]
**Class:** [CLASS]

## Learning Details
- **Learning outcome:** [LEARNING OUTCOME]
- **Indicative contents:** [INDICATIVE CONTENTS]
- **Topic of the session:** [SESSION TOPIC]
- **Duration:** [DURATION]
- **Facilitation technique:** [TECHNIQUE]

## Session Structure

### 1. Introduction (5 minutes)
**Trainer's activity:**
- Greets and makes roll calls
- Involves learners to set ground rules
- Reviews previous session
- Announces session topic
- Explains objectives

**Learner's activity:**
- Participates in roll call
- Sets ground rules
- Reviews previous session
- Asks clarifications
- Reads objectives

### 2. Development/Body (25 minutes)
[MAIN LEARNING ACTIVITIES]

### 3. Conclusion (8 minutes)
**Summary & Assessment**
- Session summary
- Formative assessment
- Session evaluation

## Resources
- Computer, projector, PPT
- Assessment sheets
- Self-assessment forms

## Appendices
- PowerPoint presentations
- Task sheets
- Assessment materials
- Answer sheets
"""
    
    sample_scheme = """
# Sample RTB Scheme of Work Template

**Province:** Southern province
**District:** Kamonyi district
**Sector:** Runda sector
**School:** Runda TSS

## Learning Outcomes Structure

| Weeks | Learning Outcome (LO) | Duration | Indicative Content (IC) | Learning Activities | Resources | Assessment | Learning Place |
|-------|----------------------|----------|------------------------|-------------------|-----------|------------|----------------|
| Week 1 | [LO1] | [DURATION] | [IC1.1] | Group work, Discussion | Computers, Projector | Written & Practical | Class, Lab |
| Week 2 | [LO2] | [DURATION] | [IC2.1] | Demonstration, Practice | Computers, Projector | Written & Practical | Class, Lab |

## Standard Elements

**Learning Activities:**
- Demonstration and simulation
- Individual and group work
- Practical exercises
- Trainer guided activities
- Group discussions

**Resources:**
- Computers, Projector, Projection screen
- Printers, Routers
- Workshop materials

**Assessment Types:**
- Written assessment
- Practical assessment
- Integrated assessment

**Learning Places:**
- Classroom
- Computer laboratory
- Workshop
"""
    
    # Write sample templates
    templates_dir = Path('rtb_templates')
    
    with open(templates_dir / 'sample_session_plan.md', 'w', encoding='utf-8') as f:
        f.write(sample_session_plan)
    
    with open(templates_dir / 'sample_scheme_of_work.md', 'w', encoding='utf-8') as f:
        f.write(sample_scheme)
    
    print("[SUCCESS] Created sample RTB templates")

def main():
    """Main integration function"""
    
    print("[RTB] RTB Integration for Morning Quiz System")
    print("=" * 50)
    
    try:
        success = integrate_rtb_with_morning_quiz()
        
        if success:
            print("\n[SUCCESS] RTB Integration completed successfully!")
            print("\n[FEATURES] RTB Features Added:")
            print("- Session Plan template management")
            print("- Scheme of Work template management") 
            print("- Automatic quiz generation from templates")
            print("- RTB-specific question types")
            print("- Progress tracking for RTB assessments")
            print("- Comprehensive reporting")
            print("- Web interface at /rtb")
            
            print("\n[ACCESS] Access Points:")
            print("- RTB Interface: http://localhost:3000/rtb")
            print("- Admin Panel: http://localhost:3000/admin (now includes RTB)")
            print("- API Endpoints: /api/rtb/*")
            
            print("\n[IMPORTANT] Important:")
            print("- Restart the system to apply changes")
            print("- RTB templates are stored in ./rtb_templates/")
            print("- Database includes new RTB tables")
            
        else:
            print("\n[ERROR] RTB Integration failed. Please check the errors above.")
            
    except Exception as e:
        print(f"\n[ERROR] Integration error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()