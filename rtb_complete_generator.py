#!/usr/bin/env python3
"""
Complete RTB Generator with all RTB standards and formatting
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

class CompleteRTBGenerator:
    def __init__(self):
        self.sectors = {
            "ICT & MULTIMEDIA": ["Software Development", "Network Administration", "Digital Media"],
            "ENGINEERING": ["Civil Engineering", "Mechanical Engineering", "Electrical Engineering"],
            "BUSINESS": ["Accounting", "Marketing", "Management"],
            "HOSPITALITY": ["Hotel Management", "Tourism", "Culinary Arts"]
        }
        
        self.facilitation_techniques = [
            "JIGSAW", "Think-Pair-Share", "Problem-based learning", "Case study method",
            "Demonstration and simulation", "Individual and group work", "Practical exercise",
            "Trainer guided", "Group discussion", "Project-based learning"
        ]
        
        self.learning_activities = [
            "Demonstration and simulation", "Individual and group work", "Practical exercise",
            "Individualized", "Trainer guided", "Group discussion", "Research activities",
            "Presentation", "Role playing", "Field work", "Laboratory work"
        ]
        
        self.assessment_types = [
            "Written assessment", "Practical assessment", "Written and practical assessment",
            "Oral assessment", "Portfolio assessment", "Project assessment", "Peer assessment"
        ]
        
        self.resources = [
            "Computers", "Projector", "Projection screen", "Printers", "Routers", "Blackboard",
            "Chalk", "Pen", "PPT", "Task sheets", "Assessment sheets", "Flipchart", "Markers",
            "Internet connection", "Software applications", "Laboratory equipment"
        ]

    def generate_complete_session_plan(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete RTB session plan with all sections"""
        
        # Enhanced input processing
        sector = user_input.get('sector', 'ICT & MULTIMEDIA')
        sub_sector = user_input.get('sub_sector', 'Software Development')
        trainer_name = user_input.get('trainer_name', 'Trainer Name')
        module_code = user_input.get('module_code', 'MOD301')
        module_name = user_input.get('module_name', 'Module Name')
        topic = user_input.get('topic', 'Session Topic')
        learning_outcome = user_input.get('learning_outcome', 'Learning Outcome')
        indicative_content = user_input.get('indicative_content', topic.split()[0])
        duration = int(user_input.get('duration', 40))
        num_learners = int(user_input.get('num_learners', 30))
        term = user_input.get('term', 'I')
        week = user_input.get('week', 'I')
        class_name = user_input.get('class', '1')
        
        # AI-generated enhanced content
        objectives = self._generate_enhanced_objectives(topic, learning_outcome, indicative_content)
        facilitation_technique = user_input.get('facilitation_technique') or random.choice(self.facilitation_techniques)
        range_content = self._generate_range_content(topic, indicative_content)
        
        # Calculate phase durations
        intro_duration = max(5, duration // 8)
        assessment_duration = 5
        evaluation_duration = 2
        body_duration = duration - intro_duration - assessment_duration - evaluation_duration
        
        return {
            "document_type": "RTB_SESSION_PLAN",
            "version": "2.0",
            "generated_date": datetime.now().isoformat(),
            "header_section": {
                "sector": f"Sector : {sector}",
                "sub_sector": f"Sub-sector: {sub_sector}",
                "date": f"Date : {datetime.now().strftime('%d/%m/%Y')}",
                "trainer_name": f"Lead Trainer's name : {trainer_name}",
                "term": f"TERM : {term}",
                "module": f"Module(Code&Name): {module_code} {module_name}",
                "week": f"Week : {week}",
                "num_learners": f"No. Learners: {num_learners}",
                "class": f"Class:{class_name}",
                "learning_outcome": learning_outcome,
                "indicative_contents": indicative_content,
                "topic": f"Topic of the session: {topic}",
                "range": range_content,
                "duration": f"Duration of the session: {duration}min",
                "objectives": self._format_objectives(objectives),
                "facilitation_technique": f"Facilitation technique(s): {facilitation_technique}"
            },
            "session_phases": {
                "introduction": {
                    "phase_name": "Introduction",
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
                "development_body": {
                    "phase_name": "Development/Body",
                    "duration": f"{body_duration}\nminutes",
                    "content": self._generate_detailed_body_content(facilitation_technique, topic, learning_outcome),
                    "resources": "Computer\nprojector\nPPT"
                },
                "conclusion": {
                    "phase_name": "CONCLUSION",
                    "summary": {
                        "duration": "3 minutes",
                        "trainer_activity": "The trainer involves the learners to summarize the session by asking questions reflecting on the learning objectives.",
                        "learner_activity": "The learners summarize the session by responding the asked questions.",
                        "resources": "Computer\nprojector"
                    },
                    "assessment": {
                        "duration": f"{assessment_duration} minutes",
                        "trainer_activity": "The trainer Instructs students details concerning assessment, assigns the Formative assessment questions to students, monitors how assessment is being done, and collects students' papers of assessment.",
                        "learner_activity": "Learners get assessment's instructions and asking for clarifications wherever needed, sits for assessment questions, works for Assessment questions given, and submits assessment papers.",
                        "resources": "Assessment sheets"
                    },
                    "evaluation": {
                        "duration": f"{evaluation_duration}minutes",
                        "trainer_activity": "Trainer involves learners in the evaluation of the session by asking some question like how was the session? Seeking for improvement in the next session and links the current to the next session.",
                        "learner_activity": "Learners evaluate the session by providing answers of asked questions and ask for clarification about the next topic of the session if any.",
                        "resources": "Self-assessment form"
                    }
                }
            },
            "appendices": {
                "references": "References:",
                "materials": [
                    "PowerPoint",
                    "Task Sheets", 
                    "Assessment sheet",
                    "Answer sheets"
                ],
                "reflection": "Reflection :"
            },
            "metadata": {
                "rtb_compliant": True,
                "format_version": "Official RTB 2024",
                "total_duration": duration,
                "learning_outcome_code": f"LO1.{week}",
                "assessment_method": random.choice(self.assessment_types)
            }
        }

    def _generate_enhanced_objectives(self, topic: str, learning_outcome: str, indicative_content: str) -> List[str]:
        """Generate comprehensive learning objectives"""
        return [
            f"Define clearly a term {indicative_content.lower()} as used in identifying {learning_outcome.lower()}.",
            f"Select properly 2 methods of {topic.split()[0].lower()} used in {indicative_content.lower()}.",
            f"Name appropriately 2 {indicative_content.lower()} Tools (both Traditional and online forms Peripherals) as used in {topic.lower()}."
        ]

    def _generate_range_content(self, topic: str, indicative_content: str) -> str:
        """Generate range content based on topic"""
        return f"Range:\nMethods of {indicative_content.lower()}\nDescription of {indicative_content.lower()} Tools (Traditional and online forms Peripherals)"

    def _format_objectives(self, objectives: List[str]) -> str:
        """Format objectives in RTB style"""
        formatted = "Objectives: By the end of this session every learner should be able to:\n"
        formatted += "\n".join(objectives)
        return formatted

    def _generate_detailed_body_content(self, technique: str, topic: str, learning_outcome: str) -> str:
        """Generate detailed body content based on facilitation technique"""
        if technique == "JIGSAW":
            return """Step 1: Forming groups (home group and expert group)
Trainer's activity:
Gives the instructions of how to form groups (by counting from 1 to 5)
Asks the learners to name their home group.
Asks learners who counted the same number to join together to form expert groups.
Learner's activity:
Follow the instructions about how to form groups by counting
Name their home groups
Those Who counted the same number join together
Step 2: Discussion and sharing in expert groups
Trainer's activity:
Distributes the task sheets to the expert groups.
Monitors the expert group discussion.
Reminds them the remaining time accordingly
Asks them to stop expert groups discussions
Asks learners to back to their home group
Learner's activity:
Receive task sheets within their expert group.
Discuss on their tasks within their expert group.
Became aware of remaining time and work accordingly.
Stop expert groups discussion
Re-join their home groups
Step 3: Sharing expertise in home groups
Trainer's activity:
Asks the learners to share what they learnt from expert teams
Monitors home group discussion and remind them the remaining time.
Declares the end of home groups discussions
Learner's activity:
Everyone explains to his/her group members what he/she learned in expert group.
Continue discussion accordingly to the remaining time
End home groups discussions"""
        else:
            return f"""Trainer's activity:
Introduces {topic} concepts and methodology
Demonstrates practical applications of {learning_outcome}
Guides learners through hands-on exercises
Monitors individual and group progress
Provides feedback and clarifications
Facilitates knowledge sharing among learners

Learner's activity:
Actively participate in {topic} activities
Engage in practical exercises related to {learning_outcome}
Collaborate with peers in group activities
Ask questions and seek clarifications
Apply learned concepts to real scenarios
Share insights and experiences with the class"""

# Export function for API use
def generate_complete_rtb_template(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """Main function to generate complete RTB templates"""
    generator = CompleteRTBGenerator()
    
    template_type = user_input.get('template_type', 'session_plan')
    
    if template_type == 'session_plan':
        return generator.generate_complete_session_plan(user_input)
    else:
        raise ValueError("Invalid template_type")

if __name__ == "__main__":
    # Test complete generation
    test_input = {
        "template_type": "session_plan",
        "sector": "ICT & MULTIMEDIA",
        "sub_sector": "Software Development",
        "trainer_name": "TUYISINGIZE Leonard",
        "module_code": "SWDPR301",
        "module_name": "Analyze project requirements",
        "topic": "Identification of requirements Gathering methodologies",
        "learning_outcome": "Identify customer needs",
        "indicative_content": "Data gathering",
        "duration": 40,
        "num_learners": 54,
        "facilitation_technique": "JIGSAW"
    }
    
    result = generate_complete_rtb_template(test_input)
    print("Complete RTB Session Plan Generated Successfully!")
    print(f"Topic: {result['header_section']['topic']}")
    print(f"Duration: {result['header_section']['duration']}")