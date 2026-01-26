"""
SUPER INTELLIGENT QUESTION PARSER
Extracts ALL questions from ANY document format
Handles: PDF, Word, Text, Images with text, Mixed formats
"""

import re
from typing import List, Dict, Optional

def extract_all_questions(text: str) -> List[Dict]:
    """
    SUPER PARSER - Extracts ALL questions regardless of format
    Returns: List of question dictionaries
    """
    questions = []
    
    # Clean text
    text = text.strip()
    if len(text) < 10:
        return []
    
    # Strategy 1: Split by question numbers (1., 2., 3., etc.)
    # Matches: "1.", "1)", "1:", "Q1.", "Question 1", etc.
    number_pattern = r'(?:^|\n)\s*(?:Q(?:uestion)?\.?\s*)?(\d+)[\s\.\)\:]+'
    splits = re.split(number_pattern, text, flags=re.MULTILINE)
    
    # Process numbered questions
    if len(splits) > 2:  # Found numbered questions
        for i in range(1, len(splits), 2):
            if i + 1 < len(splits):
                question_num = splits[i]
                question_content = splits[i + 1].strip()
                
                if len(question_content) >= 10:  # Valid question
                    parsed = parse_single_question(question_content)
                    if parsed:
                        questions.append(parsed)
    
    # Strategy 2: If no numbered questions, split by double newlines (paragraphs)
    if not questions:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        for para in paragraphs:
            if len(para) >= 15 and '?' in para:  # Looks like a question
                parsed = parse_single_question(para)
                if parsed:
                    questions.append(parsed)
    
    # Strategy 3: If still no questions, split by single newlines with question marks
    if not questions:
        lines = text.split('\n')
        current_question = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line starts a new question
            if re.match(r'^(?:Q(?:uestion)?\.?\s*)?\d+[\s\.\)\:]', line) or \
               (len(current_question) > 0 and '?' in line):
                # Save previous question
                if current_question:
                    q_text = ' '.join(current_question)
                    parsed = parse_single_question(q_text)
                    if parsed:
                        questions.append(parsed)
                current_question = [line]
            else:
                current_question.append(line)
        
        # Don't forget the last question
        if current_question:
            q_text = ' '.join(current_question)
            parsed = parse_single_question(q_text)
            if parsed:
                questions.append(parsed)
    
    # Strategy 4: Aggressive extraction - find anything with options
    if not questions:
        # Look for patterns like "A) ... B) ... C) ..."
        option_blocks = re.finditer(
            r'([^\n]+\?[^\n]*)\s*(?:[A-D][\)\.]?\s*[^\n]+\s*){2,}',
            text,
            re.IGNORECASE
        )
        for match in option_blocks:
            parsed = parse_single_question(match.group(0))
            if parsed:
                questions.append(parsed)
    
    return questions


def parse_single_question(text: str) -> Optional[Dict]:
    """
    Parse a single question text into structured format
    Handles ALL question types automatically
    """
    text = text.strip()
    if len(text) < 10:
        return None
    
    result = {
        'text': '',
        'type': 'short_answer',  # Default
        'options': [],
        'answer': ''
    }
    
    # Remove question number prefix if present
    text = re.sub(r'^(?:Q(?:uestion)?\.?\s*)?\d+[\s\.\)\:]+', '', text, flags=re.IGNORECASE)
    
    # Split by answer marker
    answer_patterns = [
        r'\s*(?:answer|ans|correct|solution|key)\s*:\s*',
        r'\s*\[answer\]\s*',
        r'\s*\(answer\)\s*'
    ]
    
    question_part = text
    answer_part = ''
    
    for pattern in answer_patterns:
        parts = re.split(pattern, text, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) == 2:
            question_part = parts[0].strip()
            answer_part = parts[1].strip()
            break
    
    # Extract options (A), B), C), etc.)
    options = extract_options(question_part)
    
    # Determine question type
    question_lower = question_part.lower()
    
    # Type 1: True/False
    if re.search(r'\b(true|false)\b', question_lower) and \
       (not options or len(options) == 2):
        result['type'] = 'true_false'
        result['options'] = ['True', 'False']
        result['text'] = re.sub(r'\s*\b(true|false)\b\s*', '', question_part, flags=re.IGNORECASE).strip()
        result['answer'] = 'True' if 'true' in answer_part.lower() else 'False'
    
    # Type 2: Multiple Choice (has options)
    elif options and len(options) >= 2:
        result['type'] = 'multiple_choice'
        result['options'] = options
        # Remove options from question text
        result['text'] = re.sub(r'[A-Z][\)\.]?\s*[^\n]+', '', question_part, flags=re.IGNORECASE).strip()
        
        # Map answer letter to option text
        if answer_part:
            letter_match = re.search(r'\b([A-Z])\b', answer_part, re.IGNORECASE)
            if letter_match:
                idx = ord(letter_match.group(1).upper()) - ord('A')
                result['answer'] = options[idx] if 0 <= idx < len(options) else options[0]
            else:
                result['answer'] = answer_part
        else:
            result['answer'] = options[0]
    
    # Type 3: Fill in the blanks
    elif re.search(r'_{3,}|\[blank\]|\(\s*\)', question_part):
        result['type'] = 'fill_blanks'
        result['text'] = question_part
        result['answer'] = answer_part or 'answer'
    
    # Type 4: Code/Programming
    elif re.search(r'\b(code|program|function|python|java|javascript|c\+\+)\b', question_lower):
        result['type'] = 'code_writing'
        result['text'] = question_part
        result['answer'] = answer_part or '// code'
    
    # Type 5: SQL
    elif re.search(r'\b(sql|query|select|database|table)\b', question_lower):
        result['type'] = 'sql_query'
        result['text'] = question_part
        result['answer'] = answer_part or 'SELECT *'
    
    # Type 6: Essay
    elif re.search(r'\b(essay|discuss|explain|describe|elaborate)\b', question_lower):
        result['type'] = 'essay'
        result['text'] = question_part
        result['answer'] = answer_part or 'Essay answer'
    
    # Type 7: Short Answer (default)
    else:
        result['type'] = 'short_answer'
        result['text'] = question_part
        result['answer'] = answer_part or 'Answer'
    
    # Validate
    if not result['text'] or len(result['text']) < 5:
        return None
    
    return result


def extract_options(text: str) -> List[str]:
    """
    Extract options from text
    Handles: A), a), A., a., (A), (a), etc.
    """
    options = []
    
    # Try different option patterns
    patterns = [
        r'([A-Z])[\)\.]?\s+([^\n]+?)(?=\s*[A-Z][\)\.]|\s*$)',  # A) Option
        r'([a-z])[\)\.]?\s+([^\n]+?)(?=\s*[a-z][\)\.]|\s*$)',  # a) Option
        r'\(([A-Z])\)\s+([^\n]+?)(?=\s*\([A-Z]\)|\s*$)',       # (A) Option
        r'\(([a-z])\)\s+([^\n]+?)(?=\s*\([a-z]\)|\s*$)',       # (a) Option
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches and len(matches) >= 2:
            # Extract just the option text (second group)
            options = [m[1].strip() if isinstance(m, tuple) else m.strip() for m in matches]
            break
    
    # Clean options
    options = [opt for opt in options if opt and len(opt) > 1]
    
    return options
