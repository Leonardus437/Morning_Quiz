from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import os
import shutil
import uuid
from pathlib import Path

router = APIRouter()

# Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Pydantic models
class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    due_date: Optional[datetime] = None
    max_score: float = 100
    allow_late_submission: bool = False
    submission_type: str = "file"  # file, text, link, both
    file_types_allowed: Optional[List[str]] = ["pdf", "docx", "txt", "zip"]
    max_file_size: int = MAX_FILE_SIZE
    school_id: Optional[int] = None
    trade_id: Optional[int] = None
    level: Optional[str] = None
    status: str = "draft"

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    due_date: Optional[datetime] = None
    max_score: Optional[float] = None
    allow_late_submission: Optional[bool] = None
    status: Optional[str] = None

class SubmissionCreate(BaseModel):
    assignment_id: int
    submission_text: Optional[str] = None
    submission_link: Optional[str] = None

class SubmissionGrade(BaseModel):
    score: float
    feedback: Optional[str] = None

# Helper functions
def get_db():
    from main import get_db
    return get_db()

def get_current_user(token: str = Depends(lambda: None)):
    # Implement your JWT token validation here
    # For now, return a mock user
    return {"id": 1, "role": "teacher"}

def save_upload_file(upload_file: UploadFile, folder: str) -> dict:
    """Save uploaded file and return file info"""
    file_ext = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / folder / unique_filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return {
        "file_name": upload_file.filename,
        "file_path": str(file_path),
        "file_size": file_path.stat().st_size,
        "file_type": file_ext[1:] if file_ext else "unknown"
    }

# Teacher endpoints
@router.post("/assignments")
async def create_assignment(
    assignment: AssignmentCreate,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new assignment"""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create assignments")
    
    query = """
        INSERT INTO assignments (
            teacher_id, title, description, instructions, due_date, max_score,
            allow_late_submission, submission_type, file_types_allowed, max_file_size,
            school_id, trade_id, level, status
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
        RETURNING id, created_at
    """
    
    result = await db.fetchrow(
        query,
        current_user["id"], assignment.title, assignment.description,
        assignment.instructions, assignment.due_date, assignment.max_score,
        assignment.allow_late_submission, assignment.submission_type,
        assignment.file_types_allowed, assignment.max_file_size,
        assignment.school_id, assignment.trade_id, assignment.level, assignment.status
    )
    
    return {
        "success": True,
        "assignment_id": result["id"],
        "created_at": result["created_at"],
        "message": "Assignment created successfully"
    }

@router.post("/assignments/{assignment_id}/attachments")
async def upload_assignment_attachment(
    assignment_id: int,
    file: UploadFile = File(...),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upload attachment for assignment"""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can upload attachments")
    
    # Verify assignment belongs to teacher
    assignment = await db.fetchrow(
        "SELECT id FROM assignments WHERE id = $1 AND teacher_id = $2",
        assignment_id, current_user["id"]
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Save file
    file_info = save_upload_file(file, f"assignments/{assignment_id}")
    
    # Save to database
    query = """
        INSERT INTO assignment_attachments (assignment_id, file_name, file_path, file_size, file_type)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
    """
    result = await db.fetchrow(
        query,
        assignment_id, file_info["file_name"], file_info["file_path"],
        file_info["file_size"], file_info["file_type"]
    )
    
    return {
        "success": True,
        "attachment_id": result["id"],
        "file_name": file_info["file_name"],
        "message": "Attachment uploaded successfully"
    }

@router.get("/assignments")
async def get_teacher_assignments(
    status: Optional[str] = None,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all assignments for teacher"""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = """
        SELECT a.*, 
               COUNT(DISTINCT s.student_id) as total_submissions,
               COUNT(DISTINCT CASE WHEN s.status = 'graded' THEN s.student_id END) as graded_count
        FROM assignments a
        LEFT JOIN assignment_submissions s ON a.id = s.assignment_id
        WHERE a.teacher_id = $1
    """
    params = [current_user["id"]]
    
    if status:
        query += " AND a.status = $2"
        params.append(status)
    
    query += " GROUP BY a.id ORDER BY a.created_at DESC"
    
    assignments = await db.fetch(query, *params)
    return {"success": True, "assignments": [dict(a) for a in assignments]}

@router.get("/assignments/{assignment_id}/submissions")
async def get_assignment_submissions(
    assignment_id: int,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all submissions for an assignment"""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = """
        SELECT s.*, u.username, u.full_name,
               json_agg(json_build_object(
                   'id', sf.id,
                   'file_name', sf.file_name,
                   'file_size', sf.file_size,
                   'uploaded_at', sf.uploaded_at
               )) FILTER (WHERE sf.id IS NOT NULL) as files
        FROM assignment_submissions s
        JOIN users u ON s.student_id = u.id
        LEFT JOIN submission_files sf ON s.id = sf.submission_id
        WHERE s.assignment_id = $1
        GROUP BY s.id, u.username, u.full_name
        ORDER BY s.submitted_at DESC
    """
    
    submissions = await db.fetch(query, assignment_id)
    return {"success": True, "submissions": [dict(s) for s in submissions]}

@router.put("/submissions/{submission_id}/grade")
async def grade_submission(
    submission_id: int,
    grade: SubmissionGrade,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Grade a student submission"""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can grade submissions")
    
    query = """
        UPDATE assignment_submissions
        SET score = $1, feedback = $2, status = 'graded', graded_at = CURRENT_TIMESTAMP
        WHERE id = $3
        RETURNING id, student_id, assignment_id
    """
    
    result = await db.fetchrow(query, grade.score, grade.feedback, submission_id)
    if not result:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return {
        "success": True,
        "message": "Submission graded successfully",
        "submission_id": result["id"]
    }

# Student endpoints
@router.get("/student/assignments")
async def get_student_assignments(
    status: Optional[str] = None,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all assignments for student"""
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get student info
    student = await db.fetchrow(
        "SELECT school_id, trade_id, level FROM users WHERE id = $1",
        current_user["id"]
    )
    
    query = """
        SELECT a.*,
               s.id as submission_id,
               s.status as submission_status,
               s.score,
               s.feedback,
               s.submitted_at,
               s.late_submission,
               json_agg(json_build_object(
                   'id', aa.id,
                   'file_name', aa.file_name,
                   'file_size', aa.file_size
               )) FILTER (WHERE aa.id IS NOT NULL) as attachments
        FROM assignments a
        LEFT JOIN assignment_submissions s ON a.id = s.assignment_id AND s.student_id = $1
        LEFT JOIN assignment_attachments aa ON a.id = aa.assignment_id
        WHERE a.status = 'published'
          AND (a.school_id = $2 OR a.school_id IS NULL)
          AND (a.trade_id = $3 OR a.trade_id IS NULL)
          AND (a.level = $4 OR a.level IS NULL)
        GROUP BY a.id, s.id
        ORDER BY a.due_date ASC NULLS LAST, a.created_at DESC
    """
    
    assignments = await db.fetch(
        query,
        current_user["id"], student["school_id"], student["trade_id"], student["level"]
    )
    
    return {"success": True, "assignments": [dict(a) for a in assignments]}

@router.post("/student/assignments/{assignment_id}/view")
async def track_assignment_view(
    assignment_id: int,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Track when student views an assignment"""
    query = """
        INSERT INTO assignment_views (assignment_id, student_id, view_count, first_viewed_at, last_viewed_at)
        VALUES ($1, $2, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT (assignment_id, student_id)
        DO UPDATE SET 
            view_count = assignment_views.view_count + 1,
            last_viewed_at = CURRENT_TIMESTAMP
    """
    await db.execute(query, assignment_id, current_user["id"])
    return {"success": True}

@router.post("/student/assignments/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: int,
    submission_text: Optional[str] = Form(None),
    submission_link: Optional[str] = Form(None),
    files: List[UploadFile] = File(None),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit assignment with files and/or text"""
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can submit assignments")
    
    # Check if assignment exists and is published
    assignment = await db.fetchrow(
        "SELECT * FROM assignments WHERE id = $1 AND status = 'published'",
        assignment_id
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Create submission
    query = """
        INSERT INTO assignment_submissions (
            assignment_id, student_id, submission_text, submission_link,
            status, submitted_at
        ) VALUES ($1, $2, $3, $4, 'submitted', CURRENT_TIMESTAMP)
        RETURNING id
    """
    
    submission = await db.fetchrow(
        query, assignment_id, current_user["id"], submission_text, submission_link
    )
    submission_id = submission["id"]
    
    # Upload files if provided
    if files:
        for file in files:
            file_info = save_upload_file(file, f"submissions/{submission_id}")
            await db.execute(
                """
                INSERT INTO submission_files (submission_id, file_name, file_path, file_size, file_type)
                VALUES ($1, $2, $3, $4, $5)
                """,
                submission_id, file_info["file_name"], file_info["file_path"],
                file_info["file_size"], file_info["file_type"]
            )
    
    return {
        "success": True,
        "submission_id": submission_id,
        "message": "Assignment submitted successfully"
    }

@router.get("/files/{file_type}/{file_id}/{filename}")
async def download_file(file_type: str, file_id: int, filename: str):
    """Download assignment or submission file"""
    # Implement file download with proper security checks
    file_path = UPLOAD_DIR / file_type / str(file_id) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, filename=filename)

@router.get("/assignments/{assignment_id}/analytics")
async def get_assignment_analytics(
    assignment_id: int,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get analytics for an assignment"""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics = await db.fetchrow(
        "SELECT * FROM assignment_analytics WHERE assignment_id = $1",
        assignment_id
    )
    
    if not analytics:
        return {"success": True, "analytics": None}
    
    return {"success": True, "analytics": dict(analytics)}
