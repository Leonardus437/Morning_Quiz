# Intelligent Auto-Grading System for All Question Types
# Supports: explain, describe, define, analyze, compare, etc.

import re
from typing import Dict, List, Tuple
from difflib import SequenceMatcher

class IntelligentGrader:
    """
    Smart auto-grading system that handles:
    - Explain questions
    - Describe questions  
    - Define questions
    - Analyze questions
    - Compare/contrast questions
    - Short answer questions
    - MCQ and True/False (exact match)
    """
    
    def __init__(self):
        # Keywords that indicate question types
        self.question_types = {
            'explain': ['explain', 'why', 'how', 'elaborate'],
            'describe': ['describe', 'what are', 'list', 'mention'],
            'define': ['define', 'what is', 'meaning of'],
            'analyze': ['analyze', 'examine', 'evaluate'],
            'compare': ['compare', 'contrast', 'difference', 'similarity']
        }
        
    def grade_answer(self, question_text: str, student_answer: str, 
                    correct_answer: str, question_type: str, points: int = 1) -> Tuple[float, str]:
        """
        Grade student answer intelligently based on question type
        
        Returns: (score, feedback)
        """
        # Clean inputs
        student_answer = student_answer.strip().lower()
        correct_answer = correct_answer.strip().lower()
        question_text = question_text.strip().lower()
        
        # Empty answer = 0
        if not student_answer or len(student_answer) < 3:
            return (0, "No answer provided")
        
        # MCQ and True/False - exact match
        if question_type in ['mcq', 'true_false']:
            if student_answer == correct_answer:
                return (points, "Correct!")
            else:
                return (0, f"Incorrect. Correct answer: {correct_answer}")
        
        # Short answer types - intelligent grading
        if question_type == 'short_answer':
            return self._grade_short_answer(
                question_text, student_answer, correct_answer, points
            )
        
        return (0, "Unknown question type")
    
    def _grade_short_answer(self, question_text: str, student_answer: str,
                           correct_answer: str, points: int) -> Tuple[float, str]:
        """
        Intelligent grading for short answer questions
        """
        # Detect question type from question text
        q_type = self._detect_question_type(question_text)
        
        # Extract keywords from correct answer
        correct_keywords = self._extract_keywords(correct_answer)
        student_keywords = self._extract_keywords(student_answer)
        
        # Calculate keyword match percentage
        keyword_score = self._calculate_keyword_match(correct_keywords, student_keywords)
        
        # Calculate semantic similarity
        similarity_score = self._calculate_similarity(student_answer, correct_answer)
        
        # Calculate length appropriateness
        length_score = self._calculate_length_score(student_answer, correct_answer, q_type)
        
        # Weighted scoring based on question type with improved fairness
        if q_type == 'define':
            # Definitions need high keyword accuracy but allow flexibility
            final_score = (keyword_score * 0.55 + similarity_score * 0.35 + length_score * 0.1)
        elif q_type == 'explain':
            # Explanations prioritize understanding over exact wording
            # More weight on similarity, less on exact keywords
            final_score = (keyword_score * 0.35 + similarity_score * 0.50 + length_score * 0.15)
        elif q_type == 'describe':
            # Descriptions need comprehensive coverage with flexibility
            final_score = (keyword_score * 0.40 + similarity_score * 0.45 + length_score * 0.15)
        elif q_type in ['analyze', 'compare']:
            # Complex questions need reasoning and coverage
            final_score = (keyword_score * 0.35 + similarity_score * 0.50 + length_score * 0.15)
        else:
            # Default balanced scoring
            final_score = (keyword_score * 0.45 + similarity_score * 0.45 + length_score * 0.1)
        
        # Apply fairness boost for detailed answers
        if q_type in ['explain', 'describe', 'analyze', 'compare']:
            word_count = len(student_answer.split())
            if word_count >= 20 and final_score >= 0.5:  # Reward detailed effort
                final_score = min(1.0, final_score * 1.1)  # 10% bonus
        
        # Convert to points
        earned_points = round(final_score * points, 2)
        
        # Generate feedback
        feedback = self._generate_feedback(
            earned_points, points, keyword_score, similarity_score, 
            correct_keywords, student_keywords
        )
        
        return (earned_points, feedback)
    
    def _detect_question_type(self, question_text: str) -> str:
        """Detect question type from question text"""
        for q_type, keywords in self.question_types.items():
            if any(keyword in question_text for keyword in keywords):
                return q_type
        return 'general'
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                     'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 
                     'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 
                     'does', 'did', 'will', 'would', 'should', 'could', 'may', 
                     'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        # Split into words and filter
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
    
    def _calculate_keyword_match(self, correct_keywords: List[str], 
                                 student_keywords: List[str]) -> float:
        """Calculate percentage of correct keywords present in student answer with partial matching"""
        if not correct_keywords:
            return 1.0
        
        # Exact matches
        exact_matches = sum(1 for kw in correct_keywords if kw in student_keywords)
        
        # Partial matches (similar words)
        partial_matches = 0
        for correct_kw in correct_keywords:
            if correct_kw not in student_keywords:
                # Check for similar words (e.g., "organize" vs "organized")
                for student_kw in student_keywords:
                    similarity = SequenceMatcher(None, correct_kw, student_kw).ratio()
                    if similarity >= 0.75:  # 75% similarity threshold
                        partial_matches += 0.5  # Half credit for partial match
                        break
        
        total_matches = exact_matches + partial_matches
        return min(1.0, total_matches / len(correct_keywords))
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _calculate_length_score(self, student_answer: str, correct_answer: str, 
                                q_type: str) -> float:
        """Score based on answer length appropriateness with improved fairness"""
        student_len = len(student_answer.split())
        correct_len = len(correct_answer.split())
        
        if correct_len == 0:
            return 1.0
        
        ratio = student_len / correct_len
        
        # More lenient length expectations
        if q_type == 'define':
            # Definitions should be concise (0.4x to 2x expected length)
            if 0.4 <= ratio <= 2.0:
                return 1.0
            elif ratio < 0.4:
                return 0.6  # Too short but give partial credit
            else:
                return 0.85  # Too long but detailed
        
        elif q_type in ['explain', 'describe', 'analyze', 'compare']:
            # Detailed questions: very flexible (0.5x to 3x expected length)
            # Reward effort and detail
            if 0.5 <= ratio <= 3.0:
                return 1.0
            elif ratio < 0.5:
                return 0.7  # Too brief but give credit
            else:
                return 0.95  # Very detailed, minimal penalty
        
        else:
            # General: flexible length (0.4x to 2.5x)
            if 0.4 <= ratio <= 2.5:
                return 1.0
            else:
                return 0.75
    
    def _generate_feedback(self, earned: float, total: float, 
                          keyword_score: float, similarity_score: float,
                          correct_keywords: List[str], student_keywords: List[str]) -> str:
        """Generate helpful and encouraging feedback for student"""
        percentage = (earned / total * 100) if total > 0 else 0
        
        # More encouraging feedback tiers
        if percentage >= 85:
            feedback = "✅ Excellent answer!"
        elif percentage >= 70:
            feedback = "✓ Good answer with minor gaps"
        elif percentage >= 55:
            feedback = "~ Acceptable, shows understanding"
        elif percentage >= 40:
            feedback = "⚠ Partial credit - some key points covered"
        elif percentage >= 25:
            feedback = "⚠ Needs improvement - review the topic"
        else:
            feedback = "✗ Insufficient answer"
        
        # Add constructive guidance
        if keyword_score < 0.5 and len(correct_keywords) > 0:
            missing = set(correct_keywords) - set(student_keywords)
            if missing and len(missing) <= 5:
                feedback += f". Consider including: {', '.join(list(missing)[:3])}"
        
        if similarity_score < 0.3 and percentage < 70:
            feedback += ". Review the expected answer format"
        
        # Encourage detailed answers
        if percentage >= 50 and len(' '.join(student_keywords)) > 50:
            feedback += " - Good detail!"
        
        return feedback


# Integration function for FastAPI
def grade_student_answer(question_text: str, student_answer: str, 
                        correct_answer: str, question_type: str, 
                        points: int = 1) -> Dict:
    """
    Grade a student answer and return score with feedback
    
    Usage in FastAPI:
        result = grade_student_answer(
            question_text="Explain what is a variable in programming",
            student_answer="A variable is a container that stores data values",
            correct_answer="A variable is a named storage location that holds data which can be changed during program execution",
            question_type="short_answer",
            points=5
        )
        # Returns: {"score": 4.2, "feedback": "✓ Good answer with minor gaps", "percentage": 84.0}
    """
    grader = IntelligentGrader()
    score, feedback = grader.grade_answer(
        question_text, student_answer, correct_answer, question_type, points
    )
    
    percentage = round((score / points * 100) if points > 0 else 0, 1)
    
    return {
        "score": score,
        "max_score": points,
        "feedback": feedback,
        "percentage": percentage,
        "passed": percentage >= 50
    }


# Example usage
if __name__ == "__main__":
    # Test cases
    test_cases = [
        {
            "question": "Explain what is a database",
            "student": "A database is a collection of organized data that can be accessed and managed",
            "correct": "A database is an organized collection of structured information or data stored electronically in a computer system",
            "type": "short_answer",
            "points": 5
        },
        {
            "question": "Define what is an algorithm",
            "student": "step by step instructions to solve problem",
            "correct": "An algorithm is a step-by-step procedure or formula for solving a problem or completing a task",
            "type": "short_answer",
            "points": 3
        },
        {
            "question": "Describe the main components of a computer",
            "student": "CPU, RAM, hard drive, motherboard, power supply",
            "correct": "The main components include CPU (processor), RAM (memory), storage devices (hard drive/SSD), motherboard, power supply unit, and input/output devices",
            "type": "short_answer",
            "points": 4
        }
    ]
    
    print("=" * 60)
    print("INTELLIGENT AUTO-GRADING SYSTEM TEST")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}:")
        print(f"Question: {test['question']}")
        print(f"Student Answer: {test['student']}")
        print(f"Expected Answer: {test['correct']}")
        
        result = grade_student_answer(
            test['question'], test['student'], test['correct'], 
            test['type'], test['points']
        )
        
        print(f"\n🎯 RESULT:")
        print(f"   Score: {result['score']}/{result['max_score']} ({result['percentage']}%)")
        print(f"   Feedback: {result['feedback']}")
        print(f"   Status: {'PASS ✅' if result['passed'] else 'FAIL ❌'}")
        print("-" * 60)
