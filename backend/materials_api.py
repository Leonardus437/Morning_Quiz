"""
Educational Materials System - Teacher posts materials, students interact
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Float, create_engine, text
from sqlalchemy.orm import Session, relationship
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import os

router = APIRouter()

# Pydantic Models
class MaterialCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content: str
    material_type: str  # article, video, pdf, link, interactive
    department: str
    level: str
    lesson_id: Optional[int] = None
    tags: Optional[List[str]] = []
    estimated_time: Optional[int] = None  # in minutes

class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    is_published: Optional[bool] = None

class MaterialInteraction(BaseModel):
    interaction_type: str  # view, like, bookmark, complete
    progress: Optional[int] = None  # 0-100 for completion tracking
    notes: Optional[str] = None

class MaterialComment(BaseModel):
    comment_text: str
    parent_id: Optional[int] = None  # for threaded comments

# Helper function to get database session
def get_db():
    from main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials=None, db: Session = Depends(get_db)):
    from main import get_current_user as main_get_current_user
    return main_get_current_user(credentials, db)

# ============================================================================
# TEACHER ENDPOINTS - Create and Manage Materials
# ============================================================================

@router.post("/create")
def create_material(
    material: MaterialCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Teacher creates new educational material"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create materials")
    
    result = db.execute(text("""
        INSERT INTO materials (
            title, description, content, material_type, department, level,
            lesson_id, tags, estimated_time, created_by, is_published
        ) VALUES (
            :title, :desc, :content, :type, :dept, :level,
            :lesson, :tags, :time, :creator, true
        ) RETURNING id
    """), {
        "title": material.title,
        "desc": material.description,
        "content": material.content,
        "type": material.material_type,
        "dept": material.department,
        "level": material.level,
        "lesson": material.lesson_id,
        "tags": material.tags,
        "time": material.estimated_time,
        "creator": current_user.id
    })
    
    db.commit()
    material_id = result.fetchone()[0]
    
    return {
        "id": material_id,
        "message": "Material created successfully",
        "title": material.title
    }

@router.get("/teacher/my-materials")
def get_teacher_materials(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all materials created by the teacher"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can access this")
    
    result = db.execute(text("""
        SELECT m.id, m.title, m.description, m.material_type, m.department, m.level,
               m.created_at, m.is_published, m.estimated_time,
               COUNT(DISTINCT mi.id) as view_count,
               COUNT(DISTINCT CASE WHEN mi.interaction_type = 'like' THEN mi.id END) as like_count,
               COUNT(DISTINCT CASE WHEN mi.interaction_type = 'complete' THEN mi.id END) as completion_count
        FROM materials m
        LEFT JOIN material_interactions mi ON m.id = mi.material_id
        WHERE m.created_by = :teacher_id
        GROUP BY m.id
        ORDER BY m.created_at DESC
    """), {"teacher_id": current_user.id})
    
    materials = []
    for row in result:
        materials.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "material_type": row[3],
            "department": row[4],
            "level": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "is_published": row[7],
            "estimated_time": row[8],
            "stats": {
                "views": row[9],
                "likes": row[10],
                "completions": row[11]
            }
        })
    
    return materials

@router.put("/{material_id}")
def update_material(
    material_id: int,
    material: MaterialUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update material"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can update materials")
    
    # Build dynamic update query
    updates = []
    params = {"id": material_id, "teacher": current_user.id}
    
    if material.title:
        updates.append("title = :title")
        params["title"] = material.title
    if material.description:
        updates.append("description = :desc")
        params["desc"] = material.description
    if material.content:
        updates.append("content = :content")
        params["content"] = material.content
    if material.is_published is not None:
        updates.append("is_published = :published")
        params["published"] = material.is_published
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    query = f"""
        UPDATE materials
        SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = :id AND created_by = :teacher
    """
    
    db.execute(text(query), params)
    db.commit()
    
    return {"message": "Material updated successfully"}

@router.delete("/{material_id}")
def delete_material(
    material_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete material"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can delete materials")
    
    db.execute(text("""
        DELETE FROM materials
        WHERE id = :id AND created_by = :teacher
    """), {"id": material_id, "teacher": current_user.id})
    
    db.commit()
    return {"message": "Material deleted successfully"}

@router.get("/{material_id}/analytics")
def get_material_analytics(
    material_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a material"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view analytics")
    
    # Get material info
    material = db.execute(text("""
        SELECT title, created_at FROM materials
        WHERE id = :id AND created_by = :teacher
    """), {"id": material_id, "teacher": current_user.id}).fetchone()
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Get interaction stats
    stats = db.execute(text("""
        SELECT 
            COUNT(DISTINCT user_id) as unique_viewers,
            COUNT(DISTINCT CASE WHEN interaction_type = 'view' THEN user_id END) as views,
            COUNT(DISTINCT CASE WHEN interaction_type = 'like' THEN user_id END) as likes,
            COUNT(DISTINCT CASE WHEN interaction_type = 'bookmark' THEN user_id END) as bookmarks,
            COUNT(DISTINCT CASE WHEN interaction_type = 'complete' THEN user_id END) as completions,
            AVG(CASE WHEN interaction_type = 'complete' THEN progress END) as avg_completion
        FROM material_interactions
        WHERE material_id = :id
    """), {"id": material_id}).fetchone()
    
    # Get recent interactions
    recent = db.execute(text("""
        SELECT u.full_name, mi.interaction_type, mi.created_at, mi.progress
        FROM material_interactions mi
        JOIN users u ON mi.user_id = u.id
        WHERE mi.material_id = :id
        ORDER BY mi.created_at DESC
        LIMIT 20
    """), {"id": material_id})
    
    recent_activity = []
    for row in recent:
        recent_activity.append({
            "student": row[0],
            "action": row[1],
            "timestamp": row[2].isoformat() if row[2] else None,
            "progress": row[3]
        })
    
    return {
        "material": {
            "title": material[0],
            "created_at": material[1].isoformat() if material[1] else None
        },
        "stats": {
            "unique_viewers": stats[0] or 0,
            "total_views": stats[1] or 0,
            "likes": stats[2] or 0,
            "bookmarks": stats[3] or 0,
            "completions": stats[4] or 0,
            "avg_completion": round(stats[5] or 0, 1)
        },
        "recent_activity": recent_activity
    }

# ============================================================================
# STUDENT ENDPOINTS - View and Interact with Materials
# ============================================================================

@router.get("/student/available")
def get_available_materials(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all materials available to the student"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this")
    
    result = db.execute(text("""
        SELECT m.id, m.title, m.description, m.material_type, m.department, m.level,
               m.created_at, m.estimated_time, m.tags,
               u.full_name as teacher_name,
               EXISTS(SELECT 1 FROM material_interactions 
                      WHERE material_id = m.id AND user_id = :student AND interaction_type = 'like') as is_liked,
               EXISTS(SELECT 1 FROM material_interactions 
                      WHERE material_id = m.id AND user_id = :student AND interaction_type = 'bookmark') as is_bookmarked,
               (SELECT progress FROM material_interactions 
                WHERE material_id = m.id AND user_id = :student AND interaction_type = 'complete'
                ORDER BY created_at DESC LIMIT 1) as progress
        FROM materials m
        JOIN users u ON m.created_by = u.id
        WHERE m.is_published = true
          AND m.department = :dept
          AND m.level = :level
        ORDER BY m.created_at DESC
    """), {
        "student": current_user.id,
        "dept": current_user.department,
        "level": current_user.level
    })
    
    materials = []
    for row in result:
        materials.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "material_type": row[3],
            "department": row[4],
            "level": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "estimated_time": row[7],
            "tags": row[8] or [],
            "teacher_name": row[9],
            "is_liked": row[10],
            "is_bookmarked": row[11],
            "progress": row[12] or 0
        })
    
    return materials

@router.get("/student/{material_id}")
def get_material_detail(
    material_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed view of a material"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this")
    
    # Get material
    result = db.execute(text("""
        SELECT m.id, m.title, m.description, m.content, m.material_type,
               m.department, m.level, m.created_at, m.estimated_time, m.tags,
               u.full_name as teacher_name,
               l.title as lesson_title
        FROM materials m
        JOIN users u ON m.created_by = u.id
        LEFT JOIN lessons l ON m.lesson_id = l.id
        WHERE m.id = :id AND m.is_published = true
    """), {"id": material_id}).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Record view
    db.execute(text("""
        INSERT INTO material_interactions (material_id, user_id, interaction_type)
        VALUES (:mat, :user, 'view')
    """), {"mat": material_id, "user": current_user.id})
    db.commit()
    
    # Get user's interactions
    interactions = db.execute(text("""
        SELECT interaction_type, progress, notes
        FROM material_interactions
        WHERE material_id = :mat AND user_id = :user
        ORDER BY created_at DESC
    """), {"mat": material_id, "user": current_user.id})
    
    user_interactions = {}
    for row in interactions:
        if row[0] not in user_interactions:
            user_interactions[row[0]] = {
                "progress": row[1],
                "notes": row[2]
            }
    
    return {
        "id": result[0],
        "title": result[1],
        "description": result[2],
        "content": result[3],
        "material_type": result[4],
        "department": result[5],
        "level": result[6],
        "created_at": result[7].isoformat() if result[7] else None,
        "estimated_time": result[8],
        "tags": result[9] or [],
        "teacher_name": result[10],
        "lesson_title": result[11],
        "user_interactions": user_interactions
    }

@router.post("/{material_id}/interact")
def interact_with_material(
    material_id: int,
    interaction: MaterialInteraction,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Student interacts with material (like, bookmark, complete)"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can interact")
    
    # Check if interaction already exists
    existing = db.execute(text("""
        SELECT id FROM material_interactions
        WHERE material_id = :mat AND user_id = :user AND interaction_type = :type
    """), {
        "mat": material_id,
        "user": current_user.id,
        "type": interaction.interaction_type
    }).fetchone()
    
    if existing and interaction.interaction_type in ['like', 'bookmark']:
        # Remove interaction (unlike/unbookmark)
        db.execute(text("""
            DELETE FROM material_interactions
            WHERE id = :id
        """), {"id": existing[0]})
        db.commit()
        return {"message": f"Removed {interaction.interaction_type}", "action": "removed"}
    else:
        # Add interaction
        db.execute(text("""
            INSERT INTO material_interactions (
                material_id, user_id, interaction_type, progress, notes
            ) VALUES (:mat, :user, :type, :prog, :notes)
        """), {
            "mat": material_id,
            "user": current_user.id,
            "type": interaction.interaction_type,
            "prog": interaction.progress,
            "notes": interaction.notes
        })
        db.commit()
        return {"message": f"Added {interaction.interaction_type}", "action": "added"}

@router.get("/student/my-bookmarks")
def get_bookmarked_materials(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student's bookmarked materials"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this")
    
    result = db.execute(text("""
        SELECT m.id, m.title, m.description, m.material_type, m.created_at,
               u.full_name as teacher_name
        FROM materials m
        JOIN material_interactions mi ON m.id = mi.material_id
        JOIN users u ON m.created_by = u.id
        WHERE mi.user_id = :student AND mi.interaction_type = 'bookmark'
        ORDER BY mi.created_at DESC
    """), {"student": current_user.id})
    
    bookmarks = []
    for row in result:
        bookmarks.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "material_type": row[3],
            "created_at": row[4].isoformat() if row[4] else None,
            "teacher_name": row[5]
        })
    
    return bookmarks

@router.get("/student/progress")
def get_student_progress(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student's learning progress"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can access this")
    
    stats = db.execute(text("""
        SELECT 
            COUNT(DISTINCT CASE WHEN interaction_type = 'view' THEN material_id END) as materials_viewed,
            COUNT(DISTINCT CASE WHEN interaction_type = 'complete' THEN material_id END) as materials_completed,
            AVG(CASE WHEN interaction_type = 'complete' THEN progress END) as avg_progress
        FROM material_interactions
        WHERE user_id = :student
    """), {"student": current_user.id}).fetchone()
    
    return {
        "materials_viewed": stats[0] or 0,
        "materials_completed": stats[1] or 0,
        "avg_progress": round(stats[2] or 0, 1)
    }

# ============================================================================
# COMMENTS SYSTEM
# ============================================================================

@router.post("/{material_id}/comments")
def add_comment(
    material_id: int,
    comment: MaterialComment,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add comment to material"""
    result = db.execute(text("""
        INSERT INTO material_comments (
            material_id, user_id, comment_text, parent_id
        ) VALUES (:mat, :user, :text, :parent)
        RETURNING id
    """), {
        "mat": material_id,
        "user": current_user.id,
        "text": comment.comment_text,
        "parent": comment.parent_id
    })
    
    db.commit()
    comment_id = result.fetchone()[0]
    
    return {"id": comment_id, "message": "Comment added"}

@router.get("/{material_id}/comments")
def get_comments(
    material_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all comments for a material"""
    result = db.execute(text("""
        SELECT c.id, c.comment_text, c.parent_id, c.created_at,
               u.full_name, u.role
        FROM material_comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.material_id = :mat
        ORDER BY c.created_at ASC
    """), {"mat": material_id})
    
    comments = []
    for row in result:
        comments.append({
            "id": row[0],
            "text": row[1],
            "parent_id": row[2],
            "created_at": row[3].isoformat() if row[3] else None,
            "author": row[4],
            "author_role": row[5]
        })
    
    return comments
