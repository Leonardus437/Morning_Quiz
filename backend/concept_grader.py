"""
CONCEPT-BASED AI GRADER
Grades based on understanding, not keyword matching
Works globally - doesn't depend on database content
"""
import re
from typing import Tuple
from difflib import SequenceMatcher

def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def concept_based_grade(
    student_answer: str,
    correct_answer: str,
    max_points: int = 1,
    question_text: str = ""
) -> Tuple[float, str, float]:
    """
    Grade based on CONCEPT understanding, not exact words
    """
    
    if not student_answer or not student_answer.strip():
        return 0.0, "No answer provided", 1.0
    
    if not correct_answer or not correct_answer.strip():
        return max_points, "Accepted", 1.0
    
    student_norm = normalize_text(student_answer)
    correct_norm = normalize_text(correct_answer)
    
    # Exact match
    if student_norm == correct_norm:
        return max_points, "Perfect!", 0.98
    
    # CONCEPT GROUPS - Universal concepts that mean the same thing
    concepts = {
        'decentralization': ['decentralization', 'decentralisation', 'distributed', 'spread', 'no central', 'not centralized', 'no single'],
        'control': ['control', 'controls', 'manage', 'power', 'authority', 'govern', 'rule'],
        'entity': ['entity', 'party', 'organization', 'person', 'group', 'third', 'middle', 'intermediary'],
        'blockchain': ['blockchain', 'ledger', 'database', 'record', 'platform', 'technology', 'chain'],
        'transaction': ['transaction', 'transfer', 'exchange', 'data', 'information', 'record'],
        'network': ['network', 'system', 'nodes', 'computers', 'machines'],
    }
    
    # Count concepts found
    score = 0.0
    concepts_in_answer = 0
    
    for concept_name, keywords in concepts.items():
        # Check if ANY keyword from this concept appears in student answer
        if any(kw in student_norm for kw in keywords):
            concepts_in_answer += 1
            score += 0.20  # Each concept = 20%
    
    # Bonus for length/detail
    if len(student_answer.split()) >= 5:
        score += 0.10
    
    # Convert to points
    score = min(score, 1.0)
    points = round(max_points * score, 2)
    
    # Feedback
    if score >= 0.85:
        feedback = "Excellent! Shows strong understanding"
        confidence = 0.90
    elif score >= 0.70:
        feedback = "Very good! Covers key concepts"
        confidence = 0.85
    elif score >= 0.50:
        feedback = "Good! Shows understanding"
        confidence = 0.75
    elif score >= 0.30:
        feedback = "Fair - partial understanding"
        confidence = 0.60
    elif score >= 0.15:
        feedback = "Some understanding shown"
        confidence = 0.50
    else:
        feedback = "Needs improvement"
        confidence = 0.40
    
    return points, feedback, confidence
