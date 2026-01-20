# AI Document Parser for Bulk Question Upload
# Supports: PDF, Word (.docx), Excel (.xlsx), Text files

import re
import json
from typing import List, Dict, Optional
from pathlib import Path
import PyPDF2
from docx import Document
import openpyxl

class AIDocumentParser:
    """
    Intelligent document parser that extracts questions from various file formats.
    Supports all question types: MCQ, True/False, Short Answer, Explain, Describe, Define, etc.
    """
    
    def __init__(self):
        self.question_patterns = {
            'mcq': r'(?:^|\n)\s*(\d+[\.\)])\s*(.+?)\n\s*(?:a[\.\)]|A[\.\)])\s*(.+?)\n\s*(?:b[\.\)]|B[\.\)])\s*(.+?)\n\s*(?:c[\.\)]|C[\.\)])\s*(.+?)\n\s*(?:d[\.\)]|D[\.\)])\s*(.+?)(?:\n\s*(?:answer|correct|ans)[:=\s]+([a-dA-D]))?',
            'true_false': r'(?:^|\n)\s*(\d+[\.\)])\s*(.+?)\s*\((?:true|false|T\/F|T or F)\)',
            'short_answer': r'(?:^|\n)\s*(\d+[\.\)])\s*(.+?)(?:\n\s*(?:answer|ans)[:=\s]+(.+?))?(?=\n\d+[\.\)]|\n\n|$)'
        }
    
    def parse_document(self, file_path: str) -> List[Dict]:
        """
        Parse document and extract questions
        Returns list of question dictionaries
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self._parse_pdf(file_path)
        elif file_ext == '.docx':
            return self._parse_docx(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            return self._parse_excel(file_path)
        elif file_ext == '.txt':
            return self._parse_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _parse_pdf(self, file_path: str) -> List[Dict]:
        """Extract questions from PDF"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        return self._extract_questions_from_text(text)
    
    def _parse_docx(self, file_path: str) -> List[Dict]:
        """Extract questions from Word document"""
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return self._extract_questions_from_text(text)
    
    def _parse_excel(self, file_path: str) -> List[Dict]:
        """
        Extract questions from Excel
        Expected format:
        Column A: Question Text
        Column B: Question Type (mcq/true_false/short_answer)
        Column C: Option A (for MCQ)
        Column D: Option B (for MCQ)
        Column E: Option C (for MCQ)
        Column F: Option D (for MCQ)
        Column G: Correct Answer
        Column H: Points (optional)
        """
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        
        questions = []
        for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip header
            if not row[0]:  # Skip empty rows
                continue
            
            question_text = str(row[0]).strip()
            question_type = str(row[1]).strip().lower() if row[1] else 'short_answer'
            
            question = {
                'question_text': question_text,
                'question_type': question_type,
                'points': int(row[7]) if row[7] else 1
            }
            
            if question_type == 'mcq':
                question['options'] = [
                    str(row[2]).strip() if row[2] else '',
                    str(row[3]).strip() if row[3] else '',
                    str(row[4]).strip() if row[4] else '',
                    str(row[5]).strip() if row[5] else ''
                ]
                question['correct_answer'] = str(row[6]).strip() if row[6] else ''
            elif question_type == 'true_false':
                question['correct_answer'] = str(row[6]).strip().lower() if row[6] else ''
            else:  # short_answer, explain, describe, define, etc.
                question['correct_answer'] = str(row[6]).strip() if row[6] else ''
            
            questions.append(question)
        
        return questions
    
    def _parse_text(self, file_path: str) -> List[Dict]:
        """Extract questions from plain text file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return self._extract_questions_from_text(text)
    
    def _extract_questions_from_text(self, text: str) -> List[Dict]:
        """
        Intelligent extraction of questions from text
        Supports multiple formats and question types
        """
        questions = []
        
        # Try to detect format and extract
        # Format 1: MCQ with options
        mcq_questions = self._extract_mcq(text)
        questions.extend(mcq_questions)
        
        # Format 2: True/False
        tf_questions = self._extract_true_false(text)
        questions.extend(tf_questions)
        
        # Format 3: Short answer / Explain / Describe / Define
        sa_questions = self._extract_short_answer(text)
        questions.extend(sa_questions)
        
        return questions
    
    def _extract_mcq(self, text: str) -> List[Dict]:
        """Extract MCQ questions"""
        questions = []
        
        # Pattern: Question followed by options a) b) c) d)
        pattern = r'(\d+[\.\)])\s*(.+?)\n\s*[aA][\.\)]\s*(.+?)\n\s*[bB][\.\)]\s*(.+?)\n\s*[cC][\.\)]\s*(.+?)\n\s*[dD][\.\)]\s*(.+?)(?:\n\s*(?:answer|correct|ans)[:=\s]+([a-dA-D]))?'
        
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            question = {
                'question_text': match.group(2).strip(),
                'question_type': 'mcq',
                'options': [
                    match.group(3).strip(),
                    match.group(4).strip(),
                    match.group(5).strip(),
                    match.group(6).strip()
                ],
                'correct_answer': match.group(7).strip().lower() if match.group(7) else '',
                'points': 1
            }
            questions.append(question)
        
        return questions
    
    def _extract_true_false(self, text: str) -> List[Dict]:
        """Extract True/False questions"""
        questions = []
        
        # Pattern: Question with (True/False) or (T/F)
        pattern = r'(\d+[\.\)])\s*(.+?)\s*\((?:true|false|T\/F|T or F)\)(?:\n\s*(?:answer|ans)[:=\s]+(true|false|t|f))?'
        
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            answer = match.group(3).strip().lower() if match.group(3) else ''
            if answer in ['t', 'true']:
                answer = 'true'
            elif answer in ['f', 'false']:
                answer = 'false'
            
            question = {
                'question_text': match.group(2).strip(),
                'question_type': 'true_false',
                'correct_answer': answer,
                'points': 1
            }
            questions.append(question)
        
        return questions
    
    def _extract_short_answer(self, text: str) -> List[Dict]:
        """Extract short answer questions (explain, describe, define, etc.)"""
        questions = []
        
        # Split by question numbers
        parts = re.split(r'\n\s*(\d+[\.\)])', text)
        
        for i in range(1, len(parts), 2):
            if i + 1 >= len(parts):
                break
            
            question_num = parts[i]
            content = parts[i + 1].strip()
            
            # Skip if already processed as MCQ or T/F
            if re.search(r'[aA][\.\)]\s*.+\n\s*[bB][\.\)]', content):
                continue
            if re.search(r'\((?:true|false|T\/F)\)', content, re.IGNORECASE):
                continue
            
            # Extract question and answer
            answer_match = re.search(r'\n\s*(?:answer|ans)[:=\s]+(.+?)(?=\n\d+[\.\)]|\n\n|$)', content, re.IGNORECASE | re.DOTALL)
            
            if answer_match:
                question_text = content[:answer_match.start()].strip()
                correct_answer = answer_match.group(1).strip()
            else:
                question_text = content.strip()
                correct_answer = ''
            
            # Detect question type from keywords
            q_type = self._detect_question_type(question_text)
            
            question = {
                'question_text': question_text,
                'question_type': 'short_answer',
                'correct_answer': correct_answer,
                'points': self._suggest_points(q_type),
                'detected_type': q_type  # For teacher reference
            }
            questions.append(question)
        
        return questions
    
    def _detect_question_type(self, question_text: str) -> str:
        """Detect question type from question text"""
        text_lower = question_text.lower()
        
        if any(word in text_lower for word in ['explain', 'why', 'how does', 'elaborate']):
            return 'explain'
        elif any(word in text_lower for word in ['describe', 'what are', 'list and describe']):
            return 'describe'
        elif any(word in text_lower for word in ['define', 'what is', 'meaning of']):
            return 'define'
        elif any(word in text_lower for word in ['analyze', 'examine', 'evaluate']):
            return 'analyze'
        elif any(word in text_lower for word in ['compare', 'contrast', 'difference', 'similarity']):
            return 'compare'
        else:
            return 'general'
    
    def _suggest_points(self, question_type: str) -> int:
        """Suggest points based on question complexity"""
        points_map = {
            'define': 2,
            'explain': 5,
            'describe': 4,
            'analyze': 6,
            'compare': 5,
            'general': 3
        }
        return points_map.get(question_type, 3)


# FastAPI integration function
def parse_question_document(file_path: str) -> Dict:
    """
    Parse uploaded document and extract questions
    
    Returns:
        {
            "success": True/False,
            "questions": [...],
            "count": int,
            "message": str
        }
    """
    try:
        parser = AIDocumentParser()
        questions = parser.parse_document(file_path)
        
        return {
            "success": True,
            "questions": questions,
            "count": len(questions),
            "message": f"Successfully extracted {len(questions)} questions"
        }
    except Exception as e:
        return {
            "success": False,
            "questions": [],
            "count": 0,
            "message": f"Error parsing document: {str(e)}"
        }


# Example usage
if __name__ == "__main__":
    # Test with sample text
    sample_text = """
    1. Explain what is a database management system (DBMS)
    Answer: A DBMS is software that manages databases, allowing users to create, read, update and delete data efficiently while ensuring data integrity and security.
    
    2. Define what is an algorithm
    Answer: An algorithm is a step-by-step procedure or set of rules for solving a problem or completing a task.
    
    3. What is the capital of France? (True/False)
    Answer: Paris
    
    4. Which of the following is a programming language?
    a) HTML
    b) Python
    c) CSS
    d) SQL
    Answer: b
    """
    
    parser = AIDocumentParser()
    questions = parser._extract_questions_from_text(sample_text)
    
    print("=" * 60)
    print("AI DOCUMENT PARSER TEST")
    print("=" * 60)
    print(f"\nExtracted {len(questions)} questions:\n")
    
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q['question_text']}")
        print(f"   Type: {q['question_type']}")
        print(f"   Answer: {q['correct_answer']}")
        print(f"   Points: {q['points']}")
        print()
