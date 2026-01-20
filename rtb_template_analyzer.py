import json
import os

def analyze_rtb_templates():
    """Analyze RTB template structures from extracted JSON data"""
    
    # Read the extracted template data
    try:
        with open('rtb_templates_extracted.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("rtb_templates_extracted.json not found")
        return
    
    print("=== RTB TEMPLATE STRUCTURE ANALYSIS ===\n")
    
    # Analyze each template
    for template_name, content in data.items():
        print(f"📄 TEMPLATE: {template_name}")
        print("-" * 50)
        
        if isinstance(content, dict):
            # Extract key sections
            sections = []
            fields = []
            
            for key, value in content.items():
                if isinstance(value, str):
                    if len(value) > 100:  # Likely a section
                        sections.append(key)
                    else:  # Likely a field
                        fields.append(f"{key}: {value}")
                elif isinstance(value, list):
                    sections.append(f"{key} (list with {len(value)} items)")
                elif isinstance(value, dict):
                    sections.append(f"{key} (nested structure)")
            
            print("📋 Key Sections:")
            for section in sections[:5]:  # Show first 5
                print(f"  • {section}")
            
            print("\n🏷️ Fields:")
            for field in fields[:5]:  # Show first 5
                print(f"  • {field}")
                
        elif isinstance(content, str):
            # Text content analysis
            lines = content.split('\n')
            print(f"📝 Text content: {len(lines)} lines")
            
            # Look for common RTB patterns
            patterns = ['objective', 'activity', 'assessment', 'resource', 'time', 'learning']
            found_patterns = []
            for pattern in patterns:
                if pattern.lower() in content.lower():
                    found_patterns.append(pattern)
            
            if found_patterns:
                print(f"🎯 RTB Elements found: {', '.join(found_patterns)}")
        
        print("\n" + "="*60 + "\n")

def extract_template_schema():
    """Extract a simplified schema for RTB templates"""
    
    try:
        with open('rtb_templates_extracted.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    
    schema = {}
    
    for template_name, content in data.items():
        template_schema = {
            'type': type(content).__name__,
            'structure': {}
        }
        
        if isinstance(content, dict):
            for key, value in content.items():
                template_schema['structure'][key] = {
                    'type': type(value).__name__,
                    'sample': str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                }
        
        schema[template_name] = template_schema
    
    # Save schema
    with open('rtb_template_schema.json', 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print("✅ Template schema saved to rtb_template_schema.json")
    return schema

if __name__ == "__main__":
    analyze_rtb_templates()
    extract_template_schema()