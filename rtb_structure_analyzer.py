#!/usr/bin/env python3
"""
RTB Template Structure Analyzer
Analyzes extracted RTB template data to understand key structures
"""

import json
from typing import Dict, List, Any

class RTBStructureAnalyzer:
    def __init__(self, extracted_data_path: str):
        with open(extracted_data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def analyze_session_plan_structure(self) -> Dict[str, Any]:
        """Analyze SESSION PLAN.docx structure"""
        session_plan = self.data.get("SESSION PLAN.docx", {})
        tables = session_plan.get("tables", [])
        
        if not tables:
            return {"error": "No tables found in session plan"}
        
        # Main table structure
        main_table = tables[0]
        rows = main_table.get("rows", [])
        
        structure = {
            "header_info": {},
            "learning_details": {},
            "session_phases": []
        }
        
        # Extract header information (rows 1-9)
        if len(rows) > 9:
            structure["header_info"] = {
                "sector": self._extract_cell_text(rows[1], 0),
                "sub_sector": self._extract_cell_text(rows[1], 1),
                "date": self._extract_cell_text(rows[1], 4),
                "trainer_name": self._extract_cell_text(rows[2], 0),
                "term": self._extract_cell_text(rows[2], 4),
                "module": self._extract_cell_text(rows[3], 0),
                "week": self._extract_cell_text(rows[3], 1),
                "num_learners": self._extract_cell_text(rows[3], 3),
                "class": self._extract_cell_text(rows[3], 4),
                "learning_outcome": self._extract_cell_text(rows[4], 1),
                "indicative_contents": self._extract_cell_text(rows[5], 1),
                "topic": self._extract_cell_text(rows[6], 0),
                "range": self._extract_cell_text(rows[7], 0),
                "duration": self._extract_cell_text(rows[7], 1),
                "objectives": self._extract_cell_text(rows[8], 0),
                "facilitation_technique": self._extract_cell_text(rows[9], 0)
            }
        
        # Extract session phases (Introduction, Development/Body, Conclusion)
        phase_rows = {
            "Introduction": 11,
            "Development/Body": 13,
            "Conclusion": 17
        }
        
        for phase_name, row_idx in phase_rows.items():
            if len(rows) > row_idx:
                structure["session_phases"].append({
                    "phase": phase_name,
                    "activities": self._extract_cell_text(rows[row_idx], 0),
                    "resources": self._extract_cell_text(rows[row_idx], 2),
                    "duration": self._extract_cell_text(rows[row_idx], 5)
                })
        
        return structure
    
    def analyze_scheme_of_work_structure(self) -> Dict[str, Any]:
        """Analyze Scheme of Work structures"""
        schemes = {}
        
        for filename, data in self.data.items():
            if "scheme" in filename.lower() and filename != "SESSION PLAN.docx":
                schemes[filename] = self._analyze_single_scheme(data)
        
        return schemes
    
    def _analyze_single_scheme(self, scheme_data: Dict) -> Dict[str, Any]:
        """Analyze a single scheme of work"""
        tables = scheme_data.get("tables", [])
        
        structure = {
            "course_info": {},
            "weekly_breakdown": [],
            "assessment_schedule": []
        }
        
        # Extract course information from paragraphs
        paragraphs = scheme_data.get("paragraphs", [])
        if paragraphs:
            structure["course_info"] = {
                "province": paragraphs[0].get("text", "") if len(paragraphs) > 0 else "",
                "district": paragraphs[1].get("text", "") if len(paragraphs) > 1 else "",
                "sector": paragraphs[2].get("text", "") if len(paragraphs) > 2 else "",
                "school": paragraphs[3].get("text", "") if len(paragraphs) > 3 else "",
                "trainer": paragraphs[5].get("text", "") if len(paragraphs) > 5 else ""
            }
        
        # Analyze tables for weekly breakdown
        for table in tables:
            rows = table.get("rows", [])
            if len(rows) > 2:  # Skip header rows
                for row in rows[2:]:  # Start from data rows
                    cells = row.get("cells", [])
                    if len(cells) >= 9 and cells[0].get("text", "").strip():
                        week_data = {
                            "weeks": self._extract_cell_text(row, 0),
                            "learning_outcome": self._extract_cell_text(row, 1),
                            "duration": self._extract_cell_text(row, 2),
                            "indicative_content": self._extract_cell_text(row, 3),
                            "learning_activities": self._extract_cell_text(row, 4),
                            "resources": self._extract_cell_text(row, 5),
                            "assessment": self._extract_cell_text(row, 6),
                            "learning_place": self._extract_cell_text(row, 7),
                            "observation": self._extract_cell_text(row, 8)
                        }
                        
                        if "Integrated Assessment" in week_data["learning_outcome"]:
                            structure["assessment_schedule"].append(week_data)
                        else:
                            structure["weekly_breakdown"].append(week_data)
        
        return structure
    
    def _extract_cell_text(self, row: Dict, cell_index: int) -> str:
        """Extract text from a specific cell"""
        cells = row.get("cells", [])
        if len(cells) > cell_index:
            return cells[cell_index].get("text", "").strip()
        return ""
    
    def generate_template_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive template summary"""
        summary = {
            "session_plan": self.analyze_session_plan_structure(),
            "schemes_of_work": self.analyze_scheme_of_work_structure(),
            "key_patterns": self._identify_key_patterns()
        }
        
        return summary
    
    def _identify_key_patterns(self) -> Dict[str, List[str]]:
        """Identify key patterns across all templates"""
        patterns = {
            "common_fields": [
                "Sector", "Sub-sector", "Trainer Name", "Date", "Term", "Week",
                "Module", "Learning Outcome", "Indicative Content", "Duration",
                "Learning Activities", "Resources", "Assessment", "Learning Place"
            ],
            "session_phases": [
                "Introduction", "Development/Body", "Conclusion"
            ],
            "facilitation_techniques": [
                "JIGSAW", "Demonstration and simulation", "Individual and group work",
                "Practical exercise", "Trainer guided", "Group discussion"
            ],
            "assessment_types": [
                "Written assessment", "Practical assessment", "Written and practical assessment",
                "Integrated Assessment"
            ],
            "learning_places": [
                "Class", "Computer lab", "Workshop", "Computer system and architecture Workshop"
            ]
        }
        
        return patterns

def main():
    """Main function to analyze RTB structures"""
    analyzer = RTBStructureAnalyzer("c:/Users/PC/Music/Morning_Quiz/backend/rtb_templates_extracted.json")
    
    print("=== RTB Template Structure Analysis ===\n")
    
    # Generate comprehensive summary
    summary = analyzer.generate_template_summary()
    
    # Display Session Plan Structure
    print("1. SESSION PLAN STRUCTURE:")
    session_plan = summary["session_plan"]
    
    print("\n   Header Information Fields:")
    for key, value in session_plan.get("header_info", {}).items():
        print(f"   - {key}: {value[:50]}..." if len(str(value)) > 50 else f"   - {key}: {value}")
    
    print("\n   Session Phases:")
    for phase in session_plan.get("session_phases", []):
        print(f"   - {phase['phase']}: {phase['duration']}")
    
    # Display Schemes of Work
    print("\n2. SCHEMES OF WORK STRUCTURES:")
    schemes = summary["schemes_of_work"]
    
    for filename, scheme in schemes.items():
        print(f"\n   {filename}:")
        print(f"   - Weekly entries: {len(scheme['weekly_breakdown'])}")
        print(f"   - Assessment entries: {len(scheme['assessment_schedule'])}")
        
        if scheme['weekly_breakdown']:
            sample = scheme['weekly_breakdown'][0]
            print(f"   - Sample LO: {sample['learning_outcome'][:60]}...")
    
    # Display Key Patterns
    print("\n3. KEY PATTERNS IDENTIFIED:")
    patterns = summary["key_patterns"]
    
    for pattern_type, items in patterns.items():
        print(f"\n   {pattern_type.replace('_', ' ').title()}:")
        for item in items[:5]:  # Show first 5 items
            print(f"   - {item}")
        if len(items) > 5:
            print(f"   ... and {len(items) - 5} more")
    
    # Save detailed analysis
    output_file = "c:/Users/PC/Music/Morning_Quiz/rtb_structure_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Detailed analysis saved to: {output_file}")
    
    return summary

if __name__ == "__main__":
    main()