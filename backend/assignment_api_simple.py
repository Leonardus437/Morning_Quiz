from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter()

# Import from main.py
from main import Base, get_db, get_current_user, User

# Database Models
class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True)
    level = Column(String(10), nullable=True)
    title = Column(String(200))
    description = Column(Text)
    file_path = Column(String(500), nullable=True)
    due_date = Column(DateTime, nullable=True)
    max_score = Column(Float, default=100)
    assignment_type = Column(String(50), default="document")
    allow_late_submission = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    max_score: float = 100
    assignment_type: str = "document"
    allow_late_submission: bool = True
    school_id: Optional[int] = None
    trade_id: Optional[int] = None
    level: Optional[str] = None

class AssignmentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    max_score: float
    assignment_type: str
    allow_late_submission: bool
    is_published: bool
    created_at: datetime

# Teacher Endpoints
@router.get("")
def get_teacher_assignments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all assignments for logged-in teacher"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can access assignments")
    
    assignments = db.query(Assignment).filter(
        Assignment.teacher_id == current_user.id
    ).order_by(Assignment.created_at.desc()).all()
    
    return assignments

@router.post("")
async def create_assignment(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    due_date: Optional[str] = Form(None),
    max_score: float = Form(100),
    assignment_type: str = Form("document"),
    allow_late_submission: bool = Form(True),
    school_id: Optional[int] = Form(None),
    trade_id: Optional[int] = Form(None),
    level: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new assignment with optional file upload"""
    import os
    
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create assignments")
    
    # Parse due_date if provided
    due_date_obj = None
    if due_date:
        try:
            due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        except:
            pass
    
    # Handle file upload
    file_path = None
    if file:
        upload_dir = "uploads/assignment_files"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = f"{upload_dir}/{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    
    new_assignment = Assignment(
        teacher_id=current_user.id,
        school_id=school_id or current_user.school_id,
        trade_id=trade_id or current_user.trade_id,
        level=level,
        title=title,
        description=description,
        file_path=file_path,
        due_date=due_date_obj,
        max_score=max_score,
        assignment_type=assignment_type,
        allow_late_submission=allow_late_submission,
        is_published=False
    )
    
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    return {
        "success": True,
        "assignment": new_assignment,
        "message": "Assignment created successfully"
    }

@router.get("/{assignment_id}")
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single assignment details"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Teachers can see their own assignments, students can see published ones
    if current_user.role == "teacher" and assignment.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if current_user.role == "student" and not assignment.is_published:
        raise HTTPException(status_code=403, detail="Assignment not published")
    
    return assignment

@router.get("/{assignment_id}/download")
async def download_assignment_file(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download assignment file"""
    from fastapi.responses import FileResponse
    import os
    
    print(f"[DOWNLOAD] Request for assignment {assignment_id} by user {current_user.username}")
    
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id
    ).first()
    
    if not assignment:
        print(f"[DOWNLOAD ERROR] Assignment {assignment_id} not found")
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    print(f"[DOWNLOAD] Assignment found: {assignment.title}, file_path={assignment.file_path}")
    
    # Students can only download published assignments
    if current_user.role == "student" and not assignment.is_published:
        print(f"[DOWNLOAD ERROR] Assignment not published")
        raise HTTPException(status_code=403, detail="Assignment not published")
    
    if not assignment.file_path:
        print(f"[DOWNLOAD ERROR] No file attached to assignment")
        raise HTTPException(status_code=404, detail="No file attached to this assignment")
    
    if not os.path.exists(assignment.file_path):
        print(f"[DOWNLOAD ERROR] File not found at path: {assignment.file_path}")
        raise HTTPException(status_code=404, detail=f"Assignment file not found on server")
    
    print(f"[DOWNLOAD] Serving file: {assignment.file_path}")
    return FileResponse(
        path=assignment.file_path,
        filename=os.path.basename(assignment.file_path),
        media_type='application/octet-stream'
    )

@router.put("/{assignment_id}")
def update_assignment(
    assignment_id: int,
    assignment_data: AssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update assignment"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    assignment.title = assignment_data.title
    assignment.description = assignment_data.description
    assignment.max_score = assignment_data.max_score
    assignment.assignment_type = assignment_data.assignment_type
    assignment.allow_late_submission = assignment_data.allow_late_submission
    
    if assignment_data.due_date:
        try:
            assignment.due_date = datetime.fromisoformat(assignment_data.due_date.replace('Z', '+00:00'))
        except:
            pass
    
    db.commit()
    db.refresh(assignment)
    
    return {
        "success": True,
        "assignment": assignment,
        "message": "Assignment updated successfully"
    }

@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete assignment"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    db.delete(assignment)
    db.commit()
    
    return {
        "success": True,
        "message": "Assignment deleted successfully"
    }

@router.post("/{assignment_id}/publish")
def publish_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish assignment to students"""
    from main import Notification
    
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    assignment.is_published = True
    db.commit()
    
    # Notify matching students
    students = db.query(User).filter(
        User.role == "student",
        User.school_id == assignment.school_id,
        User.trade_id == assignment.trade_id,
        User.level == assignment.level
    ).all()
    
    for student in students:
        notification = Notification(
            user_id=student.id,
            title=f"New Assignment: {assignment.title}",
            message=f"A new assignment '{assignment.title}' has been published. Due: {assignment.due_date.strftime('%Y-%m-%d %H:%M') if assignment.due_date else 'No deadline'}",
            type="assignment"
        )
        db.add(notification)
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Assignment published to {len(students)} students",
        "students_notified": len(students)
    }

# Student Endpoints
@router.get("/student/assignments")
def get_student_assignments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all published assignments for logged-in student"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this endpoint")
    
    # Debug logging
    print(f"[DEBUG] Student requesting assignments:")
    print(f"  - User ID: {current_user.id}")
    print(f"  - Username: {current_user.username}")
    print(f"  - School ID: {current_user.school_id}")
    print(f"  - Trade ID: {current_user.trade_id}")
    print(f"  - Level: {current_user.level}")
    
    # Get all published assignments first
    all_assignments = db.query(Assignment).filter(
        Assignment.is_published == True
    ).all()
    
    print(f"[DEBUG] Total published assignments: {len(all_assignments)}")
    for a in all_assignments:
        print(f"  - Assignment {a.id}: school={a.school_id}, trade={a.trade_id}, level={a.level}")
    
    # Filter by student's school/trade/level
    assignments = db.query(Assignment).filter(
        Assignment.is_published == True,
        Assignment.school_id == current_user.school_id,
        Assignment.trade_id == current_user.trade_id,
        Assignment.level == current_user.level
    ).order_by(Assignment.created_at.desc()).all()
    
    print(f"[DEBUG] Filtered assignments for student: {len(assignments)}")
    
    return assignments

@router.get("/test-cors")
async def test_cors():
    """Test endpoint to verify CORS is working - NO AUTH REQUIRED"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content={
            "message": "CORS is working!",
            "timestamp": datetime.utcnow().isoformat(),
            "cors_enabled": True,
            "assignment_submission_ready": True
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

@router.get("/public-test")
async def public_test():
    """Public test endpoint - NO AUTH"""
    return {
        "status": "ok",
        "message": "Assignment API is working!",
        "cors": "enabled",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.options("/submit")
async def submit_assignment_options():
    """Handle CORS preflight for assignment submission"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "3600"
        }
    )

# Define AssignmentSubmission at module level
class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String(500), nullable=True)
    text_content = Column(Text, nullable=True)
    link_url = Column(String(500), nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    status = Column(String(20), default="submitted")

@router.post("/submit")
async def submit_assignment(
    assignment_id: int = Form(...),
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
    link_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit assignment (file, text, or link)"""
    from fastapi.responses import JSONResponse
    import os
    import traceback
    
    try:
        print(f"[SUBMIT] Received submission request")
        print(f"  - Assignment ID: {assignment_id}")
        print(f"  - User: {current_user.username} (ID: {current_user.id})")
        print(f"  - File: {file.filename if file else 'None'}")
        print(f"  - Text content: {'Yes' if text_content else 'No'}")
        print(f"  - Link URL: {'Yes' if link_url else 'No'}")
        
        if current_user.role != "student":
            print(f"[SUBMIT ERROR] User is not a student: {current_user.role}")
            return JSONResponse(
                status_code=403,
                content={"success": False, "detail": "Only students can submit assignments"},
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        assignment = db.query(Assignment).filter(
            Assignment.id == assignment_id,
            Assignment.is_published == True
        ).first()
        
        if not assignment:
            print(f"[SUBMIT ERROR] Assignment {assignment_id} not found or not published")
            return JSONResponse(
                status_code=404,
                content={"success": False, "detail": "Assignment not found or not published"},
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        print(f"[SUBMIT] Assignment found: {assignment.title}")
        
        # Ensure table exists
        try:
            Base.metadata.create_all(bind=db.get_bind())
            print(f"[SUBMIT] AssignmentSubmission table ensured")
        except Exception as e:
            print(f"[SUBMIT ERROR] Failed to create table: {e}")
        
        # Check if already submitted
        existing = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.student_id == current_user.id
        ).first()
        
        if existing:
            print(f"[SUBMIT ERROR] Already submitted")
            return JSONResponse(
                status_code=400,
                content={"success": False, "detail": "You have already submitted this assignment"},
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # Handle file upload
        file_path = None
        if file:
            try:
                upload_dir = "uploads/submissions"
                os.makedirs(upload_dir, exist_ok=True)
                timestamp = datetime.utcnow().timestamp()
                file_path = f"{upload_dir}/{current_user.id}_{assignment_id}_{timestamp}_{file.filename}"
                
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                print(f"[SUBMIT] File saved: {file_path}")
            except Exception as e:
                print(f"[SUBMIT ERROR] File upload failed: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "detail": f"File upload failed: {str(e)}"},
                    headers={"Access-Control-Allow-Origin": "*"}
                )
        
        # Create submission
        try:
            submission = AssignmentSubmission(
                assignment_id=assignment_id,
                student_id=current_user.id,
                file_path=file_path,
                text_content=text_content,
                link_url=link_url
            )
            
            db.add(submission)
            db.commit()
            db.refresh(submission)
            print(f"[SUBMIT] Submission created: ID={submission.id}")
        except Exception as e:
            print(f"[SUBMIT ERROR] Database error: {e}")
            print(f"[SUBMIT ERROR] Traceback: {traceback.format_exc()}")
            db.rollback()
            return JSONResponse(
                status_code=500,
                content={"success": False, "detail": f"Failed to save submission: {str(e)}"},
                headers={"Access-Control-Allow-Origin": "*"}
            )
        
        # Notify teacher
        try:
            from main import Notification
            teacher = db.query(User).filter(User.id == assignment.teacher_id).first()
            if teacher:
                notification = Notification(
                    user_id=teacher.id,
                    title=f"New Assignment Submission",
                    message=f"{current_user.full_name or current_user.username} submitted '{assignment.title}'",
                    type="assignment_submission"
                )
                db.add(notification)
                db.commit()
                print(f"[SUBMIT] Teacher notified")
        except Exception as e:
            print(f"[SUBMIT WARNING] Notification failed: {e}")
        
        print(f"[SUBMIT] Success!")
        return JSONResponse(
            content={
                "success": True,
                "message": "Assignment submitted successfully",
                "submission_id": submission.id
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
    
    except Exception as e:
        print(f"[SUBMIT FATAL ERROR] {str(e)}")
        print(f"[SUBMIT FATAL ERROR] Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": f"Submission failed: {str(e)}"},
            headers={"Access-Control-Allow-Origin": "*"}
        )


# Teacher: View Submissions
@router.get("/{assignment_id}/submissions")
def get_assignment_submissions(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all submissions for an assignment (teacher only)"""
    from sqlalchemy import text
    
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view submissions")
    
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.teacher_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Get submissions with student details
    result = db.execute(text("""
        SELECT 
            s.id, s.assignment_id, s.student_id, s.file_path, 
            s.text_content, s.link_url, s.submitted_at, s.score, s.feedback,
            u.full_name, u.username
        FROM assignment_submissions s
        JOIN users u ON s.student_id = u.id
        WHERE s.assignment_id = :aid
        ORDER BY s.submitted_at DESC
    """), {"aid": assignment_id})
    
    submissions = []
    for row in result:
        submissions.append({
            "id": row[0],
            "assignment_id": row[1],
            "student_id": row[2],
            "file_path": row[3],
            "text_content": row[4],
            "link_url": row[5],
            "submitted_at": row[6].isoformat() if row[6] else None,
            "score": row[7],
            "feedback": row[8],
            "student_name": row[9],
            "student_username": row[10]
        })
    
    return {
        "assignment": {
            "id": assignment.id,
            "title": assignment.title,
            "max_score": assignment.max_score
        },
        "submissions": submissions,
        "total": len(submissions)
    }

# Teacher: Download Student Submission
@router.get("/submissions/{submission_id}/download")
async def download_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download student submission file"""
    from fastapi.responses import FileResponse
    from sqlalchemy import text
    import os
    
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can download submissions")
    
    result = db.execute(text("""
        SELECT s.file_path, s.assignment_id, a.teacher_id
        FROM assignment_submissions s
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.id = :sid
    """), {"sid": submission_id}).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    file_path, assignment_id, teacher_id = result
    
    if teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type='application/octet-stream'
    )

# Teacher: Grade Submission
@router.post("/submissions/{submission_id}/grade")
async def grade_submission(
    submission_id: int,
    score: float = Form(...),
    feedback: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Grade student submission and provide feedback"""
    from sqlalchemy import text
    from main import Notification
    
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can grade submissions")
    
    # Verify teacher owns this assignment
    result = db.execute(text("""
        SELECT s.id, s.student_id, s.assignment_id, a.teacher_id, a.title, a.max_score
        FROM assignment_submissions s
        JOIN assignments a ON s.assignment_id = a.id
        WHERE s.id = :sid
    """), {"sid": submission_id}).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    sub_id, student_id, assignment_id, teacher_id, assignment_title, max_score = result
    
    if teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if score > max_score:
        raise HTTPException(status_code=400, detail=f"Score cannot exceed {max_score}")
    
    # Update submission
    db.execute(text("""
        UPDATE assignment_submissions
        SET score = :score, feedback = :feedback
        WHERE id = :sid
    """), {"score": score, "feedback": feedback, "sid": submission_id})
    
    db.commit()
    
    # Notify student
    notification = Notification(
        user_id=student_id,
        title=f"Assignment Graded: {assignment_title}",
        message=f"Your assignment has been graded. Score: {score}/{max_score}. Check feedback!",
        type="assignment_graded"
    )
    db.add(notification)
    db.commit()
    
    return {
        "success": True,
        "message": "Submission graded successfully",
        "score": score,
        "feedback": feedback
    }

# Assignment Comments/Chat System
@router.post("/{assignment_id}/comments")
async def add_comment(
    assignment_id: int,
    comment_text: str = Form(...),
    submission_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add comment to assignment (teacher or student)"""
    from sqlalchemy import text
    from main import Notification
    
    # Verify assignment exists
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Create comment
    db.execute(text("""
        INSERT INTO assignment_comments (assignment_id, submission_id, user_id, comment_text, created_at)
        VALUES (:aid, :sid, :uid, :text, :created)
    """), {
        "aid": assignment_id,
        "sid": submission_id,
        "uid": current_user.id,
        "text": comment_text,
        "created": datetime.utcnow()
    })
    
    db.commit()
    
    # Notify the other party
    if current_user.role == "student":
        # Notify teacher
        notification = Notification(
            user_id=assignment.teacher_id,
            title=f"New Comment: {assignment.title}",
            message=f"{current_user.full_name or current_user.username}: {comment_text[:50]}...",
            type="assignment_comment"
        )
        db.add(notification)
    else:
        # Notify student (if submission_id provided)
        if submission_id:
            result = db.execute(text("SELECT student_id FROM assignment_submissions WHERE id = :sid"), {"sid": submission_id}).first()
            if result:
                notification = Notification(
                    user_id=result[0],
                    title=f"Teacher Comment: {assignment.title}",
                    message=f"{current_user.full_name or current_user.username}: {comment_text[:50]}...",
                    type="assignment_comment"
                )
                db.add(notification)
    
    db.commit()
    
    return {
        "success": True,
        "message": "Comment added successfully"
    }

# Get Comments for Assignment
@router.get("/{assignment_id}/comments")
def get_comments(
    assignment_id: int,
    submission_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all comments for an assignment"""
    from sqlalchemy import text
    
    query = """
        SELECT 
            c.id, c.comment_text, c.created_at, c.user_id,
            u.full_name, u.username, u.role
        FROM assignment_comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.assignment_id = :aid
    """
    
    params = {"aid": assignment_id}
    
    if submission_id:
        query += " AND (c.submission_id = :sid OR c.submission_id IS NULL)"
        params["sid"] = submission_id
    
    query += " ORDER BY c.created_at ASC"
    
    result = db.execute(text(query), params)
    
    comments = []
    for row in result:
        comments.append({
            "id": row[0],
            "comment_text": row[1],
            "created_at": row[2].isoformat() if row[2] else None,
            "user_id": row[3],
            "user_name": row[4] or row[5],
            "user_role": row[6]
        })
    
    return {
        "assignment_id": assignment_id,
        "comments": comments,
        "total": len(comments)
    }

# Student: Get My Submission
@router.get("/{assignment_id}/my-submission")
def get_my_submission(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student's own submission for an assignment"""
    from sqlalchemy import text
    
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this endpoint")
    
    result = db.execute(text("""
        SELECT id, file_path, text_content, link_url, submitted_at, score, feedback
        FROM assignment_submissions
        WHERE assignment_id = :aid AND student_id = :sid
    """), {"aid": assignment_id, "sid": current_user.id}).first()
    
    if not result:
        return {"submitted": False}
    
    return {
        "submitted": True,
        "submission": {
            "id": result[0],
            "file_path": result[1],
            "text_content": result[2],
            "link_url": result[3],
            "submitted_at": result[4].isoformat() if result[4] else None,
            "score": result[5],
            "feedback": result[6]
        }
    }
