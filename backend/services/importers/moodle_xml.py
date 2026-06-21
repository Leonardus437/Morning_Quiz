"""
Pillar D: Moodle XML Importer
Allows schools to migrate from Moodle
"""
import xml.etree.ElementTree as ET
from typing import List, Dict

def parse_moodle_xml(xml_content: str) -> List[Dict]:
    """Parse Moodle XML question format"""
    questions = []
    
    try:
        root = ET.fromstring(xml_content)
        
        for question_elem in root.findall('.//question'):
            q_type = question_elem.get('type')
            
            # Extract question text
            q_text_elem = question_elem.find('.//questiontext/text')
            q_text = q_text_elem.text if q_text_elem is not None else ""
            
            # Map Moodle types to our types
            type_map = {
                'multichoice': 'multiple_choice',
                'truefalse': 'true_false',
                'shortanswer': 'short_answer',
                'essay': 'essay',
                'matching': 'matching_pairs'
            }
            
            our_type = type_map.get(q_type, 'multiple_choice')
            
            # Extract options and correct answer
            options = []
            correct_answer = ""
            
            if q_type == 'multichoice':
                for answer in question_elem.findall('.//answer'):
                    text_elem = answer.find('text')
                    if text_elem is not None:
                        option_text = text_elem.text
                        options.append(option_text)
                        
                        # Check if correct
                        fraction = answer.get('fraction', '0')
                        if float(fraction) > 0:
                            correct_answer = option_text
            
            elif q_type == 'truefalse':
                options = ['True', 'False']
                for answer in question_elem.findall('.//answer'):
                    fraction = answer.get('fraction', '0')
                    if float(fraction) > 0:
                        text_elem = answer.find('text')
                        correct_answer = text_elem.text if text_elem is not None else ""
            
            elif q_type in ['shortanswer', 'essay']:
                # Get first answer as correct
                answer_elem = question_elem.find('.//answer/text')
                if answer_elem is not None:
                    correct_answer = answer_elem.text
            
            questions.append({
                'text': q_text.strip(),
                'type': our_type,
                'options': options,
                'answer': correct_answer,
                'points': 1
            })
    
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return []
    
    return questions

def import_from_moodle_file(file_content: bytes) -> Dict:
    """Import questions from Moodle XML file"""
    try:
        xml_str = file_content.decode('utf-8')
        questions = parse_moodle_xml(xml_str)
        
        return {
            'success': True,
            'questions': questions,
            'count': len(questions),
            'message': f"Successfully imported {len(questions)} questions from Moodle"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': "Failed to import Moodle XML"
        }
