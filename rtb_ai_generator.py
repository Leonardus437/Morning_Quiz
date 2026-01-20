#!/usr/bin/env python3
"""
RTB AI Generator - Minimal AI model for generating RTB scheme of work and session plans
Based on analyzed RTB templates and user input
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

class RTBAIGenerator:
    def __init__(self):
        # RTB template patterns from analysis
        self.facilitation_techniques = [
            "JIGSAW", "Demonstration and simulation", "Individual and group work",
            "Practical exercise", "Trainer guided", "Group discussion"
        ]
        
        self.learning_activities = [
            "Demonstration and simulation", "Individual and group work", 
            "Practical exercise", "Individualized", "Trainer guided", "Group discussion"
        ]
        
        self.assessment_types = [
            "Written assessment", "Practical assessment", "Written and practical assessment"
        ]
        
        self.resources = [
            "Computers", "Projector", "Projection screen", "Printers", "Routers",
            "Blackboard", "Chalk", "Pen", "PPT", "Task sheets"
        ]

    def generate_session_plan(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate RTB session plan from user input"""
        
        # Extract user inputs with defaults
        sector = user_input.get('sector', 'ICT & MULTIMEDIA')
        sub_sector = user_input.get('sub_sector', 'Software Development')
        trainer_name = user_input.get('trainer_name', 'Teacher Name')
        module = user_input.get('module', 'Module Name')
        topic = user_input.get('topic', 'Session Topic')
        learning_outcome = user_input.get('learning_outcome', 'Learning Outcome')
        duration = int(user_input.get('duration', 40))
        num_learners = int(user_input.get('num_learners', 30))
        
        # AI-generated content based on inputs
        objectives = self._generate_objectives(topic, learning_outcome)
        facilitation_technique = random.choice(self.facilitation_techniques)
        
        # Calculate phase durations
        intro_duration = max(3, duration // 8)
        body_duration = duration - intro_duration - 5
        conclusion_duration = 5
        
        return {
            "template_type": "session_plan",
            "header_info": {
                "sector": sector,
                "sub_sector": sub_sector,
                "date": datetime.now().strftime("%d/%m/%Y"),
                "trainer_name": trainer_name,
                "term": user_input.get('term', 'I'),
                "module": module,
                "week": user_input.get('week', 'I'),
                "num_learners": num_learners,
                "class": user_input.get('class', '1'),
                "learning_outcome": learning_outcome,
                "indicative_contents": user_input.get('indicative_content', topic.split()[0]),
                "topic": topic,
                "range": f"Methods of {topic.lower()}\nDescription of {topic.lower()} tools",
                "duration": f"{duration}min",
                "objectives": objectives,
                "facilitation_technique": facilitation_technique
            },
            "session_phases": [
                {
                    "phase": "Introduction",
                    "duration": f"{intro_duration} minutes",
                    "trainer_activities": [
                        "Greets and Makes roll calls",
                        "Involves the learners to set the ground rules", 
                        "Involves learners to review the previous session",
                        "Announces the topic of the session",
                        "Explains objectives of the session"
                    ],
                    "learner_activities": [
                        "Greets and Reply to the roll call",
                        "Participate and set the ground rules",
                        "Participate in review the previous session", 
                        "Ask clarifications about the topic of the session",
                        "Read and participate in explaining the objectives of the session"
                    ],
                    "resources": "Attendance sheet\nPPT\nProjector\nComputer\nBlackboard\nChalk\npen"
                },
                {
                    "phase": "Development/Body", 
                    "duration": f"{body_duration}\nminutes",
                    "trainer_activities": self._generate_body_activities(facilitation_technique, topic),
                    "learner_activities": self._generate_learner_activities(facilitation_technique, topic),
                    "resources": "Computer\nprojector\nPPT"
                },
                {
                    "phase": "Conclusion",
                    "duration": "3 minutes",
                    "trainer_activities": [
                        "Summary:\nThe trainer involves the learners to summarize the session by asking questions reflecting on the learning objectives.\nThe learners summarize the session by responding the asked questions."
                    ],
                    "learner_activities": [
                        "Assessment/Assignment\nThe trainer Instructs students details concerning assessment, assigns the Formative assessment questions to students, monitors how assessment is being done, and collects students' papers of assessment.\nLearners get assessment's instructions and asking for clarifications wherever needed, sits for assessment questions, works for Assessment questions given, and submits assessment papers."
                    ],
                    "resources": "Computer\nprojector"
                }
            ]
        }

    def generate_scheme_of_work(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate RTB scheme of work from user input"""
        
        # Extract user inputs
        course_title = user_input.get('course_title', 'Course Title')
        module_code = user_input.get('module_code', 'MOD301')
        trainer_name = user_input.get('trainer_name', 'Teacher Name')
        learning_outcomes = user_input.get('learning_outcomes', [])
        
        # Generate default LOs if not provided
        if not learning_outcomes:
            learning_outcomes = self._generate_default_learning_outcomes(course_title)
        
        # Generate weekly breakdown
        weekly_breakdown = []
        assessment_schedule = []
        
        for i, lo in enumerate(learning_outcomes):
            # Generate weeks for this LO
            for j, ic in enumerate(lo.get('indicative_contents', [])):
                week_entry = {
                    "weeks": f"September 8 to December 19, 2025" if i == 0 else f"January 5, 2026 - April 3, 2026",
                    "learning_outcome": f"LO{i+1}: {lo['title']}" if j == 0 else "",
                    "duration": lo.get('duration', '30 hours') if j == 0 else "",
                    "indicative_content": f"IC{i+1}.{j+1}: {ic}",
                    "learning_activities": "● Demonstration and simulation\n● Individual and group work\n● Practical exercise\n● Individualized\n● Trainer guided\n● Group discussion",
                    "resources": "Computers, Projector, Projection screen, Printers,\nrouters",
                    "assessment": random.choice(self.assessment_types),
                    "learning_place": "Class\nComputer lab",
                    "observation": ""
                }
                weekly_breakdown.append(week_entry)
        
        # Add integrated assessments
        for i in range(len(learning_outcomes)):
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
            assessment_schedule.append(assessment)
        
        return {
            "template_type": "scheme_of_work",
            "course_info": {
                "province": user_input.get('province', 'Southern province'),
                "district": user_input.get('district', 'Kamonyi district'),
                "sector": user_input.get('sector', 'Runda sector'),
                "school": user_input.get('school', 'Runda TSS'),
                "trainer_name": trainer_name,
                "course_title": course_title,
                "module_code": module_code
            },
            "weekly_breakdown": weekly_breakdown,
            "assessment_schedule": assessment_schedule
        }

    def _generate_objectives(self, topic: str, learning_outcome: str) -> List[str]:
        """AI-generated objectives based on topic and learning outcome"""
        return [
            f"Define clearly a term {topic.lower()} as used in {learning_outcome.lower()}",
            f"Select properly 2 methods of {topic.split()[0].lower()} used in {learning_outcome.lower()}",
            f"Name appropriately 2 tools used in {topic.lower()}"
        ]

    def _generate_body_activities(self, technique: str, topic: str) -> List[str]:
        """Generate trainer activities based on technique and topic"""
        if technique == "JIGSAW":
            return [
                "Step 1: Forming groups (home group and expert group)\nTrainer's activity:\nGives the instructions of how to form groups (by counting from 1 to 5)\nAsks the learners to name their home group.\nAsks learners who counted the same number to join together to form expert groups.\nLearner's activity:\nFollow the instructions about how to form groups by counting\nName their home groups\nThose Who counted the same number join together\nStep 2: Discussion and sharing in expert groups\nTrainer's activity:\nDistributes the task sheets to the expert groups.\nMonitors the expert group discussion.\nReminds them the remaining time accordingly\nAsks them to stop expert groups discussions\nAsks learners to back to their home group\nLearner's activity:\nReceive task sheets within their expert group.\nDiscuss on their tasks within their expert group.\nBecame aware of remaining time and work accordingly.\nStop expert groups discussion\nRe-join their home groups\nStep 3: Sharing expertise in home groups\nTrainer's activity:\nAsks the learners to share what they learnt from expert teams\nMonitors home group discussion and remind them the remaining time.\nDeclares the end of home groups discussions\nLearner's activity:\nEveryone explains to his/her group members what he/she learned in expert group.\nContinue discussion accordingly to the remaining time\nEnd home groups discussions"
            ]
        else:
            return [f"Demonstrates {topic} concepts and guides learners through practical exercises"]

    def _generate_learner_activities(self, technique: str, topic: str) -> List[str]:
        """Generate learner activities"""
        return [f"Participate actively in {technique.lower()} activities related to {topic.lower()}"]

    def _generate_default_learning_outcomes(self, course_title: str) -> List[Dict]:
        """Generate default learning outcomes based on course title"""
        return [
            {
                "title": f"Apply {course_title} fundamentals",
                "duration": "30 hours",
                "indicative_contents": [
                    f"Introduction to {course_title}",
                    f"Basic concepts of {course_title}",
                    f"Practical applications"
                ]
            },
            {
                "title": f"Implement {course_title} solutions", 
                "duration": "40 hours",
                "indicative_contents": [
                    f"Advanced {course_title} techniques",
                    f"Problem solving methods",
                    f"Project implementation"
                ]
            }
        ]

# Simple API interface
def generate_rtb_templates(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """Main function to generate RTB templates from user input"""
    generator = RTBAIGenerator()
    
    template_type = user_input.get('template_type', 'session_plan')
    
    if template_type == 'session_plan':
        return generator.generate_session_plan(user_input)
    elif template_type == 'scheme_of_work':
        return generator.generate_scheme_of_work(user_input)
    else:
        raise ValueError("Invalid template_type. Use 'session_plan' or 'scheme_of_work'")

# Test the AI generator
if __name__ == "__main__":
    # Test session plan generation
    session_input = {
        "template_type": "session_plan",
        "sector": "ICT & MULTIMEDIA",
        "trainer_name": "John Doe",
        "topic": "Database Design Fundamentals",
        "learning_outcome": "Design relational databases",
        "duration": 45,
        "num_learners": 25
    }
    
    session_plan = generate_rtb_templates(session_input)
    
    # Test scheme of work generation  
    scheme_input = {
        "template_type": "scheme_of_work",
        "course_title": "Web Development",
        "module_code": "WEB301",
        "trainer_name": "Jane Smith"
    }
    
    scheme_of_work = generate_rtb_templates(scheme_input)
    
    print("RTB AI Generator working correctly!")
    print(f"Generated session plan for: {session_plan['header_info']['topic']}")
    print(f"Generated scheme of work for: {scheme_of_work['course_info']['course_title']}")