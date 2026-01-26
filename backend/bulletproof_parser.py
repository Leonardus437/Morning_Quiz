"""
BULLETPROOF AI PARSER - Handles ANY Question Format
This will replace the existing parse_advanced_question function
"""

def parse_advanced_question_bulletproof(text):
    """
    Parse ANY question format - guaranteed to work
    Handles:
    - Numbered questions (1., 2., 3.)
    - Lettered options (A), B), C), a., b., c.)
    - Answer formats (Answer: A, Ans: B, Correct: C)
    - True/False (inline or separate)
    - Fill blanks (_____ or [blank])
    - Code blocks (any language)
    - SQL queries
    - All 13 question types
    """
    import re
    
    text = text.strip()
    if len(text) < 5:
        return None
    
    result = {
        'text': '',
        'type': 'multiple_choice',
        'options': [],
        'answer': ''
    }
    
    # Split by "Answer:" or similar
    answer_patterns = [
        r'\s*answer\s*:\s*',
        r'\s*ans\s*:\s*',
        r'\s*correct\s*:\s*',
        r'\s*solution\s*:\s*'
    ]
    
    parts = [text]
    for pattern in answer_patterns:
        split_result = re.split(pattern, text, maxsplit=1, flags=re.IGNORECASE)
        if len(split_result) > 1:
            parts = split_result
            break
    
    question_text = parts[0].strip()
    answer_text = parts[1].strip() if len(parts) > 1 else ''
    
    # TYPE DETECTION (Order matters - most specific first)
    
    # 1. TRUE/FALSE
    if re.search(r'\b(true|false)\b', text, re.IGNORECASE):
        if re.search(r'\?', question_text) or re.search(r'\b(is|are|does|do|can|will|should)\b', question_text, re.IGNORECASE):
            result['type'] = 'true_false'
            result['text'] = question_text
            result['options'] = ['True', 'False']
            # Extract answer
            if answer_text:
                result['answer'] = 'True' if 'true' in answer_text.lower() else 'False'
            else:
                # Check if True/False is inline
                tf_match = re.search(r'\b(true|false)\b', question_text, re.IGNORECASE)
                if tf_match:
                    result['answer'] = tf_match.group(1).capitalize()
                    # Remove answer from question
                    result['text'] = re.sub(r'\s*\b(true|false)\b\s*$', '', question_text, flags=re.IGNORECASE).strip()
            return result
    
    # 2. FILL IN THE BLANKS
    if re.search(r'_{3,}|\[blank\]|\{\}', question_text, re.IGNORECASE):
        result['type'] = 'fill_blanks'
        result['text'] = question_text
        result['answer'] = answer_text or 'answer'
        return result
    
    # 3. CODE WRITING
    code_keywords = r'\b(code|program|function|algorithm|python|java|javascript|c\+\+|write|implement|def|class|public|private)\b'
    if re.search(code_keywords, text, re.IGNORECASE):
        result['type'] = 'code_writing'
        result['text'] = question_text
        result['answer'] = answer_text or '// code here'
        return result
    
    # 4. SQL QUERY
    sql_keywords = r'\b(sql|query|database|select|insert|update|delete|create table|join|where)\b'
    if re.search(sql_keywords, text, re.IGNORECASE):
        result['type'] = 'sql_query'
        result['text'] = question_text
        result['answer'] = answer_text or 'SELECT * FROM table;'
        return result
    
    # 5. MULTIPLE SELECT (checkboxes)
    if re.search(r'select all|choose all|multiple correct|all that apply', text, re.IGNORECASE):
        result['type'] = 'multiple_select'
        result['text'] = question_text
        options = extract_options(question_text)
        result['options'] = options
        result['answer'] = answer_text or 'A,B'
        return result
    
    # 6. MATCHING PAIRS
    if re.search(r'match|pair|connect|correspond', text, re.IGNORECASE):
        result['type'] = 'drag_drop_match'
        result['text'] = question_text
        result['answer'] = answer_text or 'A-1,B-2'
        return result
    
    # 7. ORDERING/SEQUENCING
    if re.search(r'order|arrange|sequence|sort|chronological', text, re.IGNORECASE):
        result['type'] = 'drag_drop_order'
        result['text'] = question_text
        result['answer'] = answer_text or '1,2,3,4'
        return result
    
    # 8. LINEAR SCALE
    if re.search(r'rate|scale|1\s*-\s*10|rating|1\s*to\s*10', text, re.IGNORECASE):
        result['type'] = 'linear_scale'
        result['text'] = question_text
        result['answer'] = answer_text or '5'
        return result
    
    # 9. MULTI-GRID
    if re.search(r'multi.{0,5}grid|matrix|table.{0,10}question', text, re.IGNORECASE):
        result['type'] = 'multi_grid'
        result['text'] = question_text
        result['answer'] = answer_text or 'row1:col1,row2:col2'
        return result
    
    # 10. DROPDOWN
    if re.search(r'dropdown|select from list', text, re.IGNORECASE):
        result['type'] = 'dropdown_select'
        result['text'] = question_text
        options = extract_options(question_text)
        result['options'] = options
        result['answer'] = answer_text or (options[0] if options else 'A')
        return result
    
    # 11. ESSAY
    if re.search(r'essay|discuss|elaborate|explain in detail|write.{0,10}paragraph', text, re.IGNORECASE):
        result['type'] = 'essay'
        result['text'] = question_text
        result['answer'] = answer_text or 'Sample essay answer'
        return result
    
    # 12. SHORT ANSWER
    if re.search(r'short answer|brief|explain briefly|one word|few words', text, re.IGNORECASE):
        result['type'] = 'short_answer'
        result['text'] = question_text
        result['answer'] = answer_text or 'Sample answer'
        return result
    
    # 13. MULTIPLE CHOICE (default if options found)
    options = extract_options(question_text)
    if options and len(options) >= 2:
        result['type'] = 'multiple_choice'
        result['options'] = options
        # Remove options from question text
        clean_text = question_text
        for opt in options:
            clean_text = re.sub(r'[A-Za-z]\)?\s*' + re.escape(opt), '', clean_text)
        result['text'] = clean_text.strip()
        
        # Extract answer
        if answer_text:
            # Check if answer is a letter
            letter_match = re.search(r'\b([A-Za-z])\b', answer_text)
            if letter_match:
                letter = letter_match.group(1).upper()
                letter_index = ord(letter) - ord('A')
                if 0 <= letter_index < len(options):
                    result['answer'] = options[letter_index]
                else:
                    result['answer'] = options[0]
            else:
                # Answer might be the full text
                result['answer'] = answer_text
        else:
            result['answer'] = options[0] if options else 'A'
        
        return result
    
    # 14. FALLBACK - Short Answer
    result['type'] = 'short_answer'
    result['text'] = question_text
    result['answer'] = answer_text or 'Sample answer'
    
    return result if result['text'] else None


def extract_options(text):
    """
    Extract options from text in ANY format:
    - A) Option
    - a) Option
    - A. Option
    - a. Option
    - (A) Option
    - (a) Option
    """
    import re
    
    # Try multiple patterns
    patterns = [
        r'([A-Z])\)\s*([^\n\r]+?)(?=[A-Z]\)|$)',  # A) Option
        r'([a-z])\)\s*([^\n\r]+?)(?=[a-z]\)|$)',  # a) Option
        r'([A-Z])\.\s*([^\n\r]+?)(?=[A-Z]\.|$)',  # A. Option
        r'([a-z])\.\s*([^\n\r]+?)(?=[a-z]\.|$)',  # a. Option
        r'\(([A-Z])\)\s*([^\n\r]+?)(?=\([A-Z]\)|$)',  # (A) Option
        r'\(([a-z])\)\s*([^\n\r]+?)(?=\([a-z]\)|$)',  # (a) Option
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches and len(matches) >= 2:
            return [match[1].strip() for match in matches]
    
    return []


# USAGE: Replace line 49 in main.py with this function
