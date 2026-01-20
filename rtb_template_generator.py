"""
RTB (Rwanda Technical Board) Pedagogical Document Template Generator
Based on extracted template structures from actual RTB documents
"""

class RTBTemplateGenerator:
    
    def __init__(self):
        self.session_plan_structure = {
            'header_info': {
                'sector': 'ICT & MULTIMEDIA',
                'sub_sector': 'Software Development', 
                'trainer_name': '',
                'date': '',
                'term': '',
                'module_code': '',
                'week': '',
                'num_learners': '',
                'class': ''
            },
            'learning_details': {
                'learning_outcome': '',
                'indicative_contents': '',
                'topic': '',
                'range': '',
                'duration': '',
                'objectives': '',
                'facilitation_technique': ''
            },
            'session_phases': [
                {
                    'phase': 'Introduction',
                    'trainer_activity': '',
                    'learner_activity': '',
                    'resources': '',
                    'duration': '5 minutes'
                },
                {
                    'phase': 'Development/Body',
                    'trainer_activity': '',
                    'learner_activity': '',
                    'resources': '',
                    'duration': '25 minutes'
                },
                {
                    'phase': 'Conclusion',
                    'trainer_activity': '',
                    'learner_activity': '',
                    'resources': '',
                    'duration': '8 minutes'
                }
            ],
            'appendices': ['PowerPoint', 'Task Sheets', 'Assessment sheet', 'Answer sheets'],
            'references': [],
            'reflection': ''
        }
        
        self.scheme_of_work_structure = {
            'header_info': {
                'province': 'Southern province',
                'district': 'Kamonyi district', 
                'sector': 'Runda sector',
                'school': 'Runda TSS',
                'trainer_name': '',
                'terms': [1, 2, 3]
            },
            'table_headers': [
                'Weeks',
                'Learning outcome (LO)',
                'Duration', 
                'Indicative content (IC)',
                'Learning Activities',
                'Resources (Equipment, tools, and materials)',
                'Evidences of formative assessment',
                'Learning Place',
                'Observation'
            ],
            'learning_activities': [
                'Demonstration and simulation',
                'Individual and group work',
                'Practical exercise',
                'Individualized',
                'Trainer guided',
                'Group discussion'
            ],
            'resources': [
                'Computers',
                'Projector', 
                'Projection screen',
                'Printers',
                'Routers'
            ],
            'assessment_types': [
                'Written assessment',
                'Practical assessment',
                'Written and practical assessment'
            ],
            'learning_places': [
                'Class',
                'Computer lab',
                'Workshop'
            ]
        }

    def generate_session_plan_template(self, **kwargs):
        """Generate a session plan template with provided parameters"""
        
        template = f"""
=== RTB SESSION PLAN TEMPLATE ===

HEADER INFORMATION:
Sector: {kwargs.get('sector', 'ICT & MULTIMEDIA')}
Sub-sector: {kwargs.get('sub_sector', 'Software Development')}
Lead Trainer's name: {kwargs.get('trainer_name', '[TRAINER NAME]')}
Date: {kwargs.get('date', '[DATE]')}
Term: {kwargs.get('term', '[TERM]')}
Module (Code & Name): {kwargs.get('module_code', '[MODULE CODE & NAME]')}
Week: {kwargs.get('week', '[WEEK]')}
No. Learners: {kwargs.get('num_learners', '[NUMBER]')}
Class: {kwargs.get('class', '[CLASS]')}

LEARNING DETAILS:
Learning outcome: {kwargs.get('learning_outcome', '[LEARNING OUTCOME]')}
Indicative contents: {kwargs.get('indicative_contents', '[INDICATIVE CONTENTS]')}
Topic of the session: {kwargs.get('topic', '[SESSION TOPIC]')}
Range: {kwargs.get('range', '[RANGE/SCOPE]')}
Duration of the session: {kwargs.get('duration', '[DURATION]')}

Objectives: By the end of this session every learner should be able to:
{kwargs.get('objectives', '[LIST OF OBJECTIVES]')}

Facilitation technique(s): {kwargs.get('facilitation_technique', '[TECHNIQUE]')}

SESSION STRUCTURE:

1. INTRODUCTION (5 minutes)
Trainer's activity:
- Greets and Makes roll calls
- Involves the learners to set the ground rules
- Involves learners to review the previous session
- Announces the topic of the session
- Explains objectives of the session

Learner's activity:
- Greets and Reply to the roll call
- Participate and set the ground rules
- Participate in review the previous session
- Ask clarifications about the topic of the session
- Read and participate in explaining the objectives of the session

Resources: Attendance sheet, PPT, Projector, Computer, Blackboard, Chalk, pen

2. DEVELOPMENT/BODY (25 minutes)
{kwargs.get('development_activities', '[MAIN LEARNING ACTIVITIES]')}

Resources: Computer, projector, PPT

3. CONCLUSION (8 minutes)
Summary:
The trainer involves the learners to summarize the session by asking questions reflecting on the learning objectives.
The learners summarize the session by responding the asked questions.

Assessment/Assignment:
The trainer Instructs students details concerning assessment, assigns the Formative assessment questions to students, monitors how assessment is being done, and collects students' papers of assessment.

Evaluation of the session:
Trainer involves learners in the evaluation of the session by asking some question like how was the session? Seeking for improvement in the next session and links the current to the next session.

Resources: Computer projector, Assessment sheets, Self-assessment form

APPENDICES:
- PowerPoint
- Task Sheets  
- Assessment sheet
- Answer sheets

REFERENCES:
{kwargs.get('references', '[LIST REFERENCES]')}

REFLECTION:
{kwargs.get('reflection', '[TRAINER REFLECTION]')}
"""
        return template

    def generate_scheme_of_work_template(self, **kwargs):
        """Generate a scheme of work template"""
        
        template = f"""
=== RTB SCHEME OF WORK TEMPLATE ===

HEADER INFORMATION:
{kwargs.get('province', 'Southern province')}
{kwargs.get('district', 'Kamonyi district')}
{kwargs.get('sector', 'Runda sector')}
{kwargs.get('school', 'Runda TSS')}

Term: 1
Trainer's name and signature: {kwargs.get('trainer_name', '[TRAINER NAME]')}

Term: 2  
Trainer's name and signature: {kwargs.get('trainer_name', '[TRAINER NAME]')}

Term: 3
Prepared by: (Name, position and Signature) TRAINER: {kwargs.get('trainer_name', '[TRAINER NAME]')}
Verified by: (Name, position and Signature) DOS: {kwargs.get('dos_name', '[DOS NAME]')}
Approved by: (Name, position and Signature) SCHOOL MANAGER: {kwargs.get('manager_name', '[MANAGER NAME]')}

SCHEME OF WORK TABLE:

| Weeks | Learning Outcome (LO) | Duration | Indicative Content (IC) | Learning Activities | Resources | Assessment | Learning Place | Observation |
|-------|----------------------|----------|------------------------|-------------------|-----------|------------|----------------|-------------|
{self._generate_scheme_rows(**kwargs)}

LEARNING ACTIVITIES OPTIONS:
• Demonstration and simulation
• Individual and group work  
• Practical exercise
• Individualized
• Trainer guided
• Group discussion

STANDARD RESOURCES:
• Computers, Projector, Projection screen, Printers, routers

ASSESSMENT TYPES:
• Written assessment
• Practical assessment  
• Written and practical assessment

LEARNING PLACES:
• Class
• Computer lab
• Workshop
"""
        return template

    def _generate_scheme_rows(self, **kwargs):
        """Generate table rows for scheme of work"""
        
        learning_outcomes = kwargs.get('learning_outcomes', [
            'LO1: [Learning Outcome 1]',
            'LO2: [Learning Outcome 2]', 
            'LO3: [Learning Outcome 3]'
        ])
        
        rows = []
        for i, lo in enumerate(learning_outcomes, 1):
            row = f"""| Week {i} | {lo} | [DURATION] | IC{i}.1: [Indicative Content] | • Individual and group work\\n• Trainer guided\\n• Group discussion | Computers, Projector, Projection screen, Printers | Written and practical assessment | Class\\nComputer lab | |"""
            rows.append(row)
            
        # Add integrated assessment row
        rows.append("| | Integrated Assessment (for specific module) | | Integrated Assessment (for specific module) | Task | Consumables | | workshop | |")
        
        return '\n'.join(rows)

    def generate_quiz_questions_from_template(self, template_data):
        """Generate quiz questions based on RTB template content"""
        
        questions = []
        
        # Questions about learning outcomes
        if 'learning_outcome' in template_data:
            questions.append({
                'question': f"What is the main learning outcome for this session?",
                'type': 'multiple_choice',
                'options': [
                    template_data['learning_outcome'],
                    'Alternative outcome 1',
                    'Alternative outcome 2', 
                    'Alternative outcome 3'
                ],
                'correct_answer': 0
            })
        
        # Questions about facilitation techniques
        if 'facilitation_technique' in template_data:
            questions.append({
                'question': f"Which facilitation technique is used in this session?",
                'type': 'multiple_choice',
                'options': [
                    template_data['facilitation_technique'],
                    'Lecture method',
                    'Case study',
                    'Role play'
                ],
                'correct_answer': 0
            })
        
        # Questions about session duration
        if 'duration' in template_data:
            questions.append({
                'question': f"What is the total duration of this session?",
                'type': 'short_answer',
                'correct_answer': template_data['duration']
            })
        
        # Questions about resources
        questions.append({
            'question': "Which of the following are standard resources used in RTB sessions?",
            'type': 'multiple_choice',
            'options': [
                'Computer, projector, PPT',
                'Books and notebooks only',
                'Whiteboard only',
                'No resources needed'
            ],
            'correct_answer': 0
        })
        
        return questions

    def export_template(self, template_type, output_format='txt', **kwargs):
        """Export template in specified format"""
        
        if template_type == 'session_plan':
            content = self.generate_session_plan_template(**kwargs)
        elif template_type == 'scheme_of_work':
            content = self.generate_scheme_of_work_template(**kwargs)
        else:
            raise ValueError("Template type must be 'session_plan' or 'scheme_of_work'")
        
        filename = f"rtb_{template_type}_template.{output_format}"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filename

# Example usage and testing
if __name__ == "__main__":
    generator = RTBTemplateGenerator()
    
    # Generate session plan example
    session_plan = generator.generate_session_plan_template(
        trainer_name="TUYISINGIZE Leonard",
        module_code="SWDPR301 Analyze project requirements",
        topic="Identification of requirements Gathering methodologies",
        learning_outcome="1.Identify customer needs",
        indicative_contents="1.1 Data gathering",
        duration="40min",
        facilitation_technique="JIGSAW",
        objectives="Define clearly a term gathering methodologies as used in identifying customer needs.\\nSelect properly 2 methods of collecting data used in data gathering.\\nName appropriately 2 data collection Tools (both Traditional and online forms Peripherals) as used in data gathering."
    )
    
    print("=== SESSION PLAN TEMPLATE ===")
    print(session_plan)
    
    print("\n" + "="*80 + "\n")
    
    # Generate scheme of work example  
    scheme_of_work = generator.generate_scheme_of_work_template(
        trainer_name="TUYISINGIZE Leonard",
        learning_outcomes=[
            "LO1: Apply Computer programming Languages",
            "LO2: Write C Programming codes", 
            "LO3: Perform Program Testing"
        ]
    )
    
    print("=== SCHEME OF WORK TEMPLATE ===")
    print(scheme_of_work)
    
    # Generate quiz questions
    template_data = {
        'learning_outcome': '1.Identify customer needs',
        'facilitation_technique': 'JIGSAW',
        'duration': '40min'
    }
    
    questions = generator.generate_quiz_questions_from_template(template_data)
    
    print("\n=== GENERATED QUIZ QUESTIONS ===")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q['question']}")
        if q['type'] == 'multiple_choice':
            for j, option in enumerate(q['options']):
                print(f"   {chr(65+j)}. {option}")
        print()