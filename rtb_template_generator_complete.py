#!/usr/bin/env python3
"""
Complete RTB Template Generator
Based on analyzed RTB template structures from Rwanda Technical Board
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random

class RTBTemplateGenerator:
    def __init__(self):
        self.facilitation_techniques = [
            "JIGSAW", "Demonstration and simulation", "Individual and group work",
            "Practical exercise", "Trainer guided", "Group discussion",
            "Think-Pair-Share", "Problem-based learning", "Case study method"
        ]
        
        self.assessment_types = [
            "Written assessment", "Practical assessment", 
            "Written and practical assessment", "Oral assessment",
            "Portfolio assessment", "Project-based assessment"
        ]
        
        self.learning_places = [
            "Class", "Computer lab", "Workshop", 
            "Computer system and architecture Workshop",
            "Library", "Field work", "Online platform"
        ]
        
        self.resources = [
            "Computers", "Projector", "Projection screen", "Printers",
            "Routers", "Blackboard", "Chalk", "Pen", "PPT",
            "Attendance sheet", "Task sheets", "Assessment sheets"
        ]

    def generate_session_plan(self, 
                            sector: str = "ICT & MULTIMEDIA",
                            sub_sector: str = "Software Development", 
                            trainer_name: str = "TUYISINGIZE Leonard",
                            module_code: str = "SWDPR301",
                            module_name: str = "Analyze project requirements",
                            learning_outcome: str = "Identify customer needs",
                            indicative_content: str = "Data gathering",
                            topic: str = "Identification of requirements gathering methodologies",
                            duration: int = 40,
                            num_learners: int = 54,
                            class_name: str = "1",
                            term: str = "I",
                            week: str = "I",
                            objectives: List[str] = None,
                            facilitation_technique: str = None) -> Dict[str, Any]:
        """Generate a complete RTB Session Plan"""
        
        if objectives is None:
            objectives = [
                f"Define clearly a term {topic.lower()} as used in {learning_outcome.lower()}",
                f"Select properly 2 methods related to {indicative_content.lower()}",
                f"Name appropriately 2 tools used in {indicative_content.lower()}"
            ]
        
        if facilitation_technique is None:
            facilitation_technique = random.choice(self.facilitation_techniques)
        
        # Calculate phase durations
        intro_duration = max(3, duration // 8)  # ~12.5% for introduction
        body_duration = duration - intro_duration - 5  # Main content
        conclusion_duration = 5  # Fixed 5 minutes for conclusion
        
        session_plan = {
            "template_type": "session_plan",
            "header_info": {
                "sector": sector,
                "sub_sector": sub_sector,
                "date": datetime.now().strftime("%d/%m/%Y"),
                "trainer_name": trainer_name,
                "term": term,
                "module": f"{module_code} {module_name}",
                "week": week,
                "num_learners": num_learners,
                "class": class_name,
                "learning_outcome": learning_outcome,
                "indicative_contents": indicative_content,
                "topic": topic,
                "range": f"Methods of {indicative_content.lower()}\nDescription of {indicative_content.lower()} tools",
                "duration": f"{duration}min",
                "objectives": objectives,
                "facilitation_technique": facilitation_technique
            },
            "session_phases": [
                {
                    "phase": "Introduction",
                    "duration": f"{intro_duration} minutes",
                    "trainer_activities": [
                        "Greets and makes roll calls",
                        "Involves the learners to set the ground rules",
                        "Involves learners to review the previous session",
                        "Announces the topic of the session",
                        "Explains objectives of the session"
                    ],
                    "learner_activities": [
                        "Greets and reply to the roll call",
                        "Participate and set the ground rules",
                        "Participate in review the previous session",
                        "Ask clarifications about the topic of the session",
                        "Read and participate in explaining the objectives of the session"
                    ],
                    "resources": ["Attendance sheet", "PPT", "Projector", "Computer", "Blackboard", "Chalk", "Pen"]
                },
                {
                    "phase": "Development/Body",
                    "duration": f"{body_duration} minutes",
                    "trainer_activities": self._generate_body_activities(facilitation_technique),
                    "learner_activities": self._generate_learner_body_activities(facilitation_technique),
                    "resources": ["Computer", "Projector", "PPT", "Task sheets"]
                },
                {
                    "phase": "Conclusion",
                    "duration": f"{conclusion_duration} minutes",
                    "trainer_activities": [
                        "Involves the learners to summarize the session by asking questions reflecting on the learning objectives",
                        "Instructs students details concerning assessment",
                        "Assigns formative assessment questions to students",
                        "Monitors how assessment is being done",
                        "Collects students' papers of assessment",
                        "Involves learners in the evaluation of the session",
                        "Links the current to the next session"
                    ],
                    "learner_activities": [
                        "Summarize the session by responding the asked questions",
                        "Get assessment's instructions and ask for clarifications wherever needed",
                        "Sit for assessment questions",
                        "Work for assessment questions given",
                        "Submit assessment papers",
                        "Evaluate the session by providing answers of asked questions"
                    ],
                    "resources": ["Computer", "Projector", "Assessment sheets", "Self-assessment form"]
                }
            ],
            "appendices": ["PowerPoint", "Task Sheets", "Assessment sheet", "Answer sheets"],
            "references": [],
            "reflection": ""
        }
        
        return session_plan

    def generate_scheme_of_work(self,
                               course_title: str = "Computer Programming",
                               module_code: str = "L4CSA",
                               province: str = "Southern province",
                               district: str = "Kamonyi district",
                               sector: str = "Runda sector",
                               school: str = "Runda TSS",
                               trainer_name: str = "TUYISINGIZE Leonard",
                               learning_outcomes: List[Dict] = None,
                               term: int = 1) -> Dict[str, Any]:
        """Generate a complete RTB Scheme of Work"""
        
        if learning_outcomes is None:
            learning_outcomes = [
                {
                    "code": "LO1",
                    "title": "Apply Computer programming Languages",
                    "duration": "30 hours",
                    "indicative_contents": [
                        "Identification of programming Language",
                        "Development of an algorithm", 
                        "Development of a flowchart"
                    ]
                },
                {
                    "code": "LO2", 
                    "title": "Write Programming codes",
                    "duration": "60 hours",
                    "indicative_contents": [
                        "Description of programming concepts",
                        "Description of program structure",
                        "Application of condition statements",
                        "Application of loops",
                        "Application of functions"
                    ]
                },
                {
                    "code": "LO3",
                    "title": "Perform Program Testing", 
                    "duration": "20 hours",
                    "indicative_contents": [
                        "Identification of errors",
                        "Compilation of the program",
                        "Test of the program"
                    ]
                }
            ]
        
        # Generate term dates
        start_date, end_date = self._generate_term_dates(term)
        
        scheme = {
            "template_type": "scheme_of_work",
            "course_info": {
                "course_title": course_title,
                "module_code": module_code,
                "province": province,
                "district": district,
                "sector": sector,
                "school": school,
                "trainer_name": trainer_name,
                "term": term,
                "start_date": start_date,
                "end_date": end_date
            },
            "weekly_breakdown": [],
            "assessment_schedule": []
        }
        
        # Generate weekly breakdown
        week_counter = 1
        for lo in learning_outcomes:
            for i, ic in enumerate(lo["indicative_contents"]):
                week_entry = {
                    "weeks": f"Week {week_counter}",
                    "date_range": self._calculate_week_dates(start_date, week_counter),
                    "learning_outcome": f"{lo['code']}: {lo['title']}",
                    "duration": lo["duration"] if i == 0 else "",
                    "indicative_content": f"IC{lo['code'][2:]}.{i+1}: {ic}",
                    "learning_activities": [
                        "Demonstration and simulation",
                        "Individual and group work", 
                        "Practical exercise",
                        "Individualized",
                        "Trainer guided",
                        "Group discussion"
                    ],
                    "resources": random.sample(self.resources, 4),
                    "assessment": random.choice(self.assessment_types),
                    "learning_place": random.choice(self.learning_places),
                    "observation": ""
                }
                scheme["weekly_breakdown"].append(week_entry)
                week_counter += 1
        
        # Add integrated assessments
        assessment_weeks = [len(scheme["weekly_breakdown"]) // 3, 
                          2 * len(scheme["weekly_breakdown"]) // 3,
                          len(scheme["weekly_breakdown"])]
        
        for week in assessment_weeks:
            assessment = {
                "weeks": f"Week {week}",
                "date_range": self._calculate_week_dates(start_date, week),
                "learning_outcome": "Integrated Assessment (for specific module)",
                "duration": "Integrated Assessment (for specific module)",
                "indicative_content": "Integrated Assessment (for specific module)",
                "learning_activities": ["Task"],
                "resources": ["Consumables"],
                "assessment": "Integrated Assessment",
                "learning_place": "Workshop",
                "observation": ""
            }
            scheme["assessment_schedule"].append(assessment)
        
        return scheme

    def _generate_body_activities(self, technique: str) -> List[str]:
        """Generate trainer activities based on facilitation technique"""
        if technique == "JIGSAW":
            return [
                "Step 1: Forming groups (home group and expert group)",
                "Gives the instructions of how to form groups (by counting from 1 to 5)",
                "Asks the learners to name their home group",
                "Asks learners who counted the same number to join together to form expert groups",
                "Step 2: Discussion and sharing in expert groups", 
                "Distributes the task sheets to the expert groups",
                "Monitors the expert group discussion",
                "Reminds them the remaining time accordingly",
                "Asks them to stop expert groups discussions",
                "Asks learners to back to their home group",
                "Step 3: Sharing expertise in home groups",
                "Asks the learners to share what they learnt from expert teams",
                "Monitors home group discussion and remind them the remaining time",
                "Declares the end of home groups discussions"
            ]
        elif technique == "Demonstration and simulation":
            return [
                "Demonstrates the key concepts using practical examples",
                "Shows step-by-step procedures",
                "Guides learners through simulation exercises",
                "Provides real-world scenarios for practice",
                "Monitors learner understanding during demonstration",
                "Corrects misconceptions immediately",
                "Encourages questions during demonstration"
            ]
        else:
            return [
                "Introduces the main topic and key concepts",
                "Facilitates group formation and task distribution", 
                "Monitors group activities and provides guidance",
                "Encourages active participation from all learners",
                "Provides feedback and clarifications as needed",
                "Summarizes key points from group presentations"
            ]

    def _generate_learner_body_activities(self, technique: str) -> List[str]:
        """Generate learner activities based on facilitation technique"""
        if technique == "JIGSAW":
            return [
                "Follow the instructions about how to form groups by counting",
                "Name their home groups",
                "Those who counted the same number join together",
                "Receive task sheets within their expert group",
                "Discuss on their tasks within their expert group",
                "Become aware of remaining time and work accordingly",
                "Stop expert groups discussion",
                "Re-join their home groups",
                "Everyone explains to his/her group members what he/she learned in expert group",
                "Continue discussion accordingly to the remaining time",
                "End home groups discussions"
            ]
        elif technique == "Demonstration and simulation":
            return [
                "Observe the demonstration carefully",
                "Take notes of key procedures and concepts",
                "Ask questions for clarification",
                "Participate in simulation exercises",
                "Practice the demonstrated procedures",
                "Apply learned concepts to given scenarios",
                "Share observations and experiences with peers"
            ]
        else:
            return [
                "Actively participate in group formation",
                "Engage in assigned group tasks and discussions",
                "Collaborate effectively with group members",
                "Present group findings to the class",
                "Ask questions and seek clarifications",
                "Take notes of important concepts and procedures"
            ]

    def _generate_term_dates(self, term: int) -> tuple:
        """Generate start and end dates for a term"""
        current_year = datetime.now().year
        
        if term == 1:
            start = datetime(current_year, 9, 8)  # September
            end = datetime(current_year, 12, 19)  # December
        elif term == 2:
            start = datetime(current_year + 1, 1, 5)  # January
            end = datetime(current_year + 1, 4, 3)   # April
        else:  # term 3
            start = datetime(current_year + 1, 4, 20)  # April
            end = datetime(current_year + 1, 7, 3)    # July
        
        return start.strftime("%B %d, %Y"), end.strftime("%B %d, %Y")

    def _calculate_week_dates(self, start_date_str: str, week_number: int) -> str:
        """Calculate date range for a specific week"""
        start_date = datetime.strptime(start_date_str, "%B %d, %Y")
        week_start = start_date + timedelta(weeks=week_number-1)
        week_end = week_start + timedelta(days=6)
        return f"{week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}"

    def generate_quiz_questions(self, template_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate quiz questions based on RTB template content"""
        questions = []
        
        if template_data["template_type"] == "session_plan":
            # Generate questions from session plan
            header = template_data["header_info"]
            
            # Multiple choice questions
            questions.append({
                "type": "multiple_choice",
                "question": f"What is the main learning outcome of this session on {header['topic']}?",
                "options": [
                    header["learning_outcome"],
                    "Complete all practical exercises",
                    "Attend the full session",
                    "Submit assignment on time"
                ],
                "correct_answer": 0,
                "explanation": f"The main learning outcome is: {header['learning_outcome']}"
            })
            
            # True/False questions
            questions.append({
                "type": "true_false", 
                "question": f"The facilitation technique used in this session is {header['facilitation_technique']}.",
                "correct_answer": True,
                "explanation": f"Yes, the facilitation technique is {header['facilitation_technique']}"
            })
            
            # Short answer questions
            for i, objective in enumerate(header["objectives"][:2]):
                questions.append({
                    "type": "short_answer",
                    "question": f"Based on the session objectives, {objective.lower()}",
                    "sample_answer": f"Students should be able to {objective.lower()}",
                    "keywords": objective.split()[:3]
                })
        
        elif template_data["template_type"] == "scheme_of_work":
            # Generate questions from scheme of work
            for entry in template_data["weekly_breakdown"][:3]:  # First 3 weeks
                if entry["learning_outcome"]:
                    questions.append({
                        "type": "multiple_choice",
                        "question": f"Which learning outcome covers {entry['indicative_content']}?",
                        "options": [
                            entry["learning_outcome"],
                            "LO1: Basic computer skills",
                            "LO2: Advanced programming",
                            "LO3: System administration"
                        ],
                        "correct_answer": 0,
                        "explanation": f"The correct learning outcome is: {entry['learning_outcome']}"
                    })
        
        return questions

    def export_to_json(self, template_data: Dict[str, Any], filename: str) -> str:
        """Export template data to JSON file"""
        filepath = f"c:/Users/PC/Music/Morning_Quiz/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
        return filepath

def main():
    """Demo function to show RTB template generation"""
    generator = RTBTemplateGenerator()
    
    print("=== RTB Template Generator Demo ===\n")
    
    # Generate Session Plan
    print("1. Generating Session Plan...")
    session_plan = generator.generate_session_plan(
        topic="Introduction to Database Design",
        learning_outcome="Design database schemas",
        indicative_content="Entity-Relationship modeling",
        duration=45,
        facilitation_technique="JIGSAW"
    )
    
    session_file = generator.export_to_json(session_plan, "sample_session_plan.json")
    print(f"   Session Plan saved to: {session_file}")
    
    # Generate Scheme of Work
    print("\n2. Generating Scheme of Work...")
    scheme = generator.generate_scheme_of_work(
        course_title="Database Management Systems",
        module_code="DBMS301"
    )
    
    scheme_file = generator.export_to_json(scheme, "sample_scheme_of_work.json")
    print(f"   Scheme of Work saved to: {scheme_file}")
    
    # Generate Quiz Questions
    print("\n3. Generating Quiz Questions...")
    questions = generator.generate_quiz_questions(session_plan)
    
    quiz_data = {
        "template_source": "session_plan",
        "topic": session_plan["header_info"]["topic"],
        "questions": questions
    }
    
    quiz_file = generator.export_to_json(quiz_data, "sample_quiz_questions.json")
    print(f"   Quiz Questions saved to: {quiz_file}")
    
    print(f"\n   Generated {len(questions)} quiz questions from the session plan")
    
    print("\n=== RTB Template Generation Complete ===")
    return generator

if __name__ == "__main__":
    main()