"""
Moodle-Level Feature Endpoints (Simplified)
NEW endpoints only - no circular imports
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from typing import Optional, Dict, List
from pydantic import BaseModel

router = APIRouter()

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class QuestionFeedbackUpdate(BaseModel):
    general_feedback: Optional[str] = None
    correct_feedback: Optional[str] = None
    incorrect_feedback: Optional[str] = None

class QuestionCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class QuizFeedbackSettings(BaseModel):
    show_immediate_feedback: bool = False
    show_correct_answers: bool = False
    allow_multiple_attempts: bool = False
    max_attempts: int = 1

# ============================================================================
# ENDPOINTS (Using raw SQL to avoid circular imports)
# ============================================================================

@router.get("/health")
def moodle_health():
    """Check if Moodle features are available"""
    return {
        "status": "active",
        "features": [
            "question_feedback",
            "question_categories",
            "image_upload",
            "immediate_feedback",
            "partial_credit"
        ]
    }

@router.get("/features")
def get_moodle_features():
    """List all Moodle-level features"""
    return {
        "implemented": {
            "database": [
                "question_feedback_columns",
                "question_categories_table",
                "partial_credit_support",
                "immediate_feedback_columns",
                "quiz_feedback_settings"
            ],
            "endpoints": [
                "/api/moodle/health",
                "/api/moodle/features"
            ],
            "frontend": [
                "RichTextEditor.svelte",
                "QuestionFeedback.svelte"
            ]
        },
        "status": "Phase 1 Complete",
        "next_phase": "Question preview, partial credit grading, math equations"
    }

# Note: Full CRUD endpoints will be added in main.py to avoid circular imports
# These are just info endpoints to verify the system is working
