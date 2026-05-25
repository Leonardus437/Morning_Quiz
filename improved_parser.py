# Improved AI Document Parser - Handles all question types correctly

import re
from typing import Dict, List, Tuple

class ImprovedDocumentParser:
    """Enhanced parser that correctly extracts all question types"""
    
    def parse_text_file(self, file_path: str) -> List[Dict]:
        """Parse text file and extract all questions"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> List[Dict]:
        """Parse content and extract questions"""
        questions = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and headers
            if not line or line.startswith('=') or 'SECTION' in line or 'Module:' in line:
                i += 1
                continue
            
            # Check if line starts with a number (question number)
            match = re.match(r'^(\d+)\.\s+(.+)$', line)
            if match:
                question_num = match.group(1)
                question_text = match.group(2).strip()
                
                # Look ahead to determine question type
                i += 1
                options = []
                answer = None
                
                # Collect options and answer
                while i < len(lines):
                    next_line = lines[i].strip()
                    
                    # Stop if we hit next question
                    if re.match(r'^(\d+)\.\s+', next_line):
                        break
                    
                    # Skip empty lines
                    if not next_line:
                        i += 1
                        continue
                    
                    # Check for option (a), b), c), d))
                    opt_match = re.match(r'^([a-dA-D])\)\s+(.+)$', next_line)
                    if opt_match:
                        options.append(opt_match.group(2).strip())
                        i += 1
                        continue
                    
                    # Check for answer
                    ans_match = re.match(r'^Answer:\s*(.+)$', next_line, re.IGNORECASE)
                    if ans_match:
                        answer = ans_match.group(1).strip()
                        i += 1
                        break
                    
                    # If it's not an option or answer, it's part of question text
                    if not options and not answer:
                        question_text += ' ' + next_line
                        i += 1
                        continue
                    
                    i += 1
                
                # Determine question type and create question object
                if answer:
                    question = self._create_question(question_text, options, answer)
                    if question:
                        questions.append(question)
            else:
                i += 1
        
        return questions
    
    def _create_question(self, question_text: str, options: List[str], answer: str) -> Dict:
        """Create question object based on type"""
        
        # True/False detection
        if '(True/False)' in question_text or '(T/F)' in question_text:
            clean_text = question_text.replace('(True/False)', '').replace('(T/F)', '').strip()
            correct = 'True' if answer.lower() in ['true', 't', 'yes'] else 'False'
            return {
                'question_text': clean_text,
                'question_type': 'true_false',
                'options': ['True', 'False'],
                'correct_answer': correct,
                'points': 1
            }
        
        # MCQ detection (has options)
        if options and len(options) >= 2:
            # Map letter to option
            correct_answer = answer
            if len(answer) == 1 and answer.lower() in 'abcd':
                idx = ord(answer.lower()) - ord('a')
                if 0 <= idx < len(options):
                    correct_answer = options[idx]
            
            return {
                'question_text': question_text,
                'question_type': 'mcq',
                'options': options,
                'correct_answer': correct_answer,
                'points': 1
            }
        
        # Short answer / Explain / Describe / Define
        q_type = self._detect_type(question_text)
        points = self._get_points(q_type)
        
        return {
            'question_text': question_text,
            'question_type': 'short_answer',
            'options': [],
            'correct_answer': answer,
            'points': points,
            'detected_type': q_type
        }
    
    def _detect_type(self, question_text: str) -> str:
        """Detect question type from text"""
        text_lower = question_text.lower()
        
        if any(w in text_lower for w in ['explain', 'why', 'how does', 'elaborate']):
            return 'explain'
        elif any(w in text_lower for w in ['describe', 'what are', 'list']):
            return 'describe'
        elif any(w in text_lower for w in ['define', 'what is', 'meaning']):
            return 'define'
        elif any(w in text_lower for w in ['analyze', 'examine', 'evaluate']):
            return 'analyze'
        elif any(w in text_lower for w in ['compare', 'contrast', 'difference']):
            return 'compare'
        else:
            return 'general'
    
    def _get_points(self, q_type: str) -> int:
        """Get points based on question type"""
        points_map = {
            'define': 2,
            'explain': 5,
            'describe': 4,
            'analyze': 6,
            'compare': 5,
            'general': 3
        }
        return points_map.get(q_type, 3)


# Test the parser
if __name__ == "__main__":
    parser = ImprovedDocumentParser()
    
    # Test with sample content
    sample = """
1. What is an oscillator?
a) A device that converts AC to DC
b) A circuit that generates repetitive waveforms
c) A device that amplifies signals
d) A circuit that filters noise
Answer: b

2. Positive feedback increases stability (True/False)
Answer: False

3. Define what is an oscillator
Answer: An oscillator is an electronic circuit that generates repetitive waveforms without external input.

4. Explain the difference between positive and negative feedback
Answer: Positive feedback reinforces the input signal while negative feedback opposes it.
"""
    
    questions = parser.parse_content(sample)
    print(f"Parsed {len(questions)} questions:")
    for q in questions:
        print(f"  - {q['question_type']}: {q['question_text'][:50]}...")
