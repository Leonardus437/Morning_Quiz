#!/usr/bin/env python3
"""
Complete RTB Scheme of Work Generator
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

class CompleteSchemeGenerator:
    def __init__(self):
        self.learning_activities = [
            "Demonstration and simulation", "Individual and group work", "Practical exercise",
            "Individualized", "Trainer guided", "Group discussion", "Research activities",
            "Presentation", "Role playing", "Field work", "Laboratory work", "Case studies"
        ]
        
        self.assessment_types = [
            "Written assessment", "Practical assessment", "Written and practical assessment",
            "Oral assessment", "Portfolio assessment", "Project assessment"
        ]
        
        self.learning_places = [
            "Class", "Computer lab", "Workshop", "Computer system and architecture Workshop",
            "Library", "Field work", "Laboratory", "Online platform"
        ]

    def generate_complete_scheme_of_work(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete RTB scheme of work"""
        
        # Extract inputs
        course_title = user_input.get('course_title', 'Course Title')
        module_code = user_input.get('module_code', 'MOD301')
        trainer_name = user_input.get('trainer_name', 'Trainer Name')
        province = user_input.get('province', 'Southern province')
        district = user_input.get('district', 'Kamonyi district')
        sector = user_input.get('sector', 'Runda sector')
        school = user_input.get('school', 'Runda TSS')
        term = int(user_input.get('term', 1))
        
        # Generate learning outcomes if not provided
        learning_outcomes = user_input.get('learning_outcomes') or self._generate_learning_outcomes(course_title)
        
        # Generate term dates
        start_date, end_date = self._generate_term_dates(term)
        
        return {
            "document_type": "RTB_SCHEME_OF_WORK",
            "version": "2.0",
            "generated_date": datetime.now().isoformat(),
            "header_info": {
                "province": province,
                "district": district,
                "sector": sector,
                "school": school,
                "course_title": course_title,
                "module_code": module_code,
                "term_info": {
                    "term_1": {
                        "label": "Term: 1",
                        "trainer": f"Trainer's name and signature: {trainer_name}",
                        "period": f"{start_date} - {end_date}" if term == 1 else ""
                    },
                    "term_2": {
                        "label": "Term: 2", 
                        "trainer": f"Trainer's name and signature: {trainer_name}",
                        "period": f"{start_date} - {end_date}" if term == 2 else ""
                    },
                    "term_3": {
                        "label": "Term: 3",
                        "trainer": f"Trainer's name and signature: {trainer_name}",
                        "period": f"{start_date} - {end_date}" if term == 3 else ""
                    }
                },
                "approval_section": {
                    "prepared_by": f"Prepared by: (Name, position and Signature) TRAINER: {trainer_name}",
                    "verified_by": "Verified by: (Name, position and Signature) DOS :",
                    "approved_by": "Approved by: (Name, position and Signature) SCHOOL MANAGER: "
                }
            },
            "table_structure": {
                "headers": {
                    "row_1": [
                        "Weeks", "Competence code and name", "Competence code and name", 
                        "Competence code and name", "Learning Activities", 
                        "Resources (Equipment, tools, and materials)", 
                        "Evidences of formative assessment", "Learning Place", "Observation"
                    ],
                    "row_2": [
                        "Weeks", "Learning outcome (LO)", "Duration", "Indicative content (IC)",
                        "Learning Activities", "Resources (Equipment, tools, and materials)",
                        "Evidences of formative assessment", "Learning Place", "Observation"
                    ]
                }
            },
            "weekly_breakdown": self._generate_weekly_breakdown(learning_outcomes, start_date, term),
            "assessment_schedule": self._generate_assessment_schedule(learning_outcomes, term),
            "metadata": {
                "rtb_compliant": True,
                "format_version": "Official RTB 2024",
                "total_learning_outcomes": len(learning_outcomes),
                "term": term,
                "academic_year": datetime.now().year
            }
        }

    def _generate_learning_outcomes(self, course_title: str) -> List[Dict]:
        """Generate comprehensive learning outcomes"""
        base_topics = course_title.split()
        main_topic = base_topics[0] if base_topics else "Subject"
        
        return [
            {
                "code": "LO1",
                "title": f"Apply {main_topic} fundamentals",
                "duration": "30 hours",
                "indicative_contents": [
                    f"Identification of {main_topic.lower()} concepts",
                    f"Description of {main_topic.lower()} principles", 
                    f"Application of basic {main_topic.lower()} techniques"
                ]
            },
            {
                "code": "LO2",
                "title": f"Implement {main_topic} solutions",
                "duration": "40 hours", 
                "indicative_contents": [
                    f"Development of {main_topic.lower()} projects",
                    f"Testing and validation of {main_topic.lower()} systems",
                    f"Documentation and reporting"
                ]
            },
            {
                "code": "LO3",
                "title": f"Evaluate {main_topic} performance",
                "duration": "20 hours",
                "indicative_contents": [
                    f"Assessment of {main_topic.lower()} effectiveness",
                    f"Quality assurance procedures",
                    f"Continuous improvement methods"
                ]
            }
        ]

    def _generate_weekly_breakdown(self, learning_outcomes: List[Dict], start_date: str, term: int) -> List[Dict]:
        """Generate detailed weekly breakdown"""
        weekly_entries = []
        
        for lo_index, lo in enumerate(learning_outcomes):
            for ic_index, ic in enumerate(lo["indicative_contents"]):
                # Calculate week dates
                week_number = len(weekly_entries) + 1
                week_dates = self._calculate_week_dates(start_date, week_number, term)
                
                entry = {
                    "weeks": week_dates,
                    "learning_outcome": f"{lo['code']}: {lo['title']}" if ic_index == 0 else "",
                    "duration": lo["duration"] if ic_index == 0 else "",
                    "indicative_content": f"IC{lo_index + 1}.{ic_index + 1}: {ic}",
                    "learning_activities": "● " + "\n● ".join(random.sample(self.learning_activities, 6)),
                    "resources": "Computers, Projector, Projection screen, Printers,\nrouters",
                    "assessment": random.choice(self.assessment_types),
                    "learning_place": random.choice(self.learning_places),
                    "observation": ""
                }
                weekly_entries.append(entry)
        
        return weekly_entries

    def _generate_assessment_schedule(self, learning_outcomes: List[Dict], term: int) -> List[Dict]:
        """Generate integrated assessment schedule"""
        assessments = []
        
        # Add integrated assessments after each learning outcome
        for i, lo in enumerate(learning_outcomes):
            assessment = {
                "weeks": "",
                "learning_outcome": "Integrated Assessment (for specific module)",
                "duration": "Integrated Assessment (for specific module)",
                "indicative_content": "Integrated Assessment (for specific module)",
                "learning_activities": "Task",
                "resources": "Consumables",
                "assessment": "",
                "learning_place": "workshop",
                "observation": ""
            }
            assessments.append(assessment)
        
        return assessments

    def _generate_term_dates(self, term: int) -> tuple:
        """Generate term start and end dates"""
        current_year = datetime.now().year
        
        if term == 1:
            start = datetime(current_year, 9, 8)
            end = datetime(current_year, 12, 19)
        elif term == 2:
            start = datetime(current_year + 1, 1, 5)
            end = datetime(current_year + 1, 4, 3)
        else:  # term 3
            start = datetime(current_year + 1, 4, 20)
            end = datetime(current_year + 1, 7, 3)
        
        return start.strftime("%B %d, %Y"), end.strftime("%B %d, %Y")

    def _calculate_week_dates(self, start_date_str: str, week_number: int, term: int) -> str:
        """Calculate specific week date ranges"""
        try:
            start_date = datetime.strptime(start_date_str, "%B %d, %Y")
        except:
            # Fallback date calculation
            current_year = datetime.now().year
            if term == 1:
                start_date = datetime(current_year, 9, 8)
            elif term == 2:
                start_date = datetime(current_year + 1, 1, 5)
            else:
                start_date = datetime(current_year + 1, 4, 20)
        
        week_start = start_date + timedelta(weeks=week_number-1)
        week_end = week_start + timedelta(days=6)
        
        return f"{week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}"

# Export function
def generate_complete_scheme(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """Generate complete RTB scheme of work"""
    generator = CompleteSchemeGenerator()
    return generator.generate_complete_scheme_of_work(user_input)

if __name__ == "__main__":
    # Test scheme generation
    test_input = {
        "course_title": "Computer Programming",
        "module_code": "L4CSA",
        "trainer_name": "TUYISINGIZE Leonard",
        "term": 1
    }
    
    result = generate_complete_scheme(test_input)
    print("Complete RTB Scheme of Work Generated!")
    print(f"Course: {result['header_info']['course_title']}")
    print(f"Weekly entries: {len(result['weekly_breakdown'])}")