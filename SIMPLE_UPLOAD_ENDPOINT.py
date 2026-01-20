# Simple Direct Upload Endpoint - No Parser Complexity

# Add this to backend/main.py after the existing upload endpoints

@app.post("/questions/upload-simple")
async def upload_questions_simple(
    file: UploadFile = File(...),
    department: str = Form(...),
    level: str = Form(...),
    lesson_id: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simple direct upload - reads file and returns parsed questions"""
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teacher access required")
    
    # Validate lesson
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.department == department,
        Lesson.level == level,
        Lesson.is_active == True
    ).first()
    if not lesson:
        raise HTTPException(status_code=400, detail="Invalid lesson")
    
    try:
        content = await file.read()
        text = content.decode('utf-8')
        
        # Simple line-by-line parsing
        questions = []
        lines = text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            
            # Skip empty/header lines
            if not line or line.startswith('=') or 'SECTION' in line:
                continue
            
            # Check for question number
            import re
            match = re.match(r'^(\d+)\.\s+(.+)$', line)
            if not match:
                continue
            
            q_text = match.group(2).strip()
            options = []
            answer = ""
            
            # Collect options and answer
            while i < len(lines):
                next_line = lines[i].strip()
                
                # Stop at next question
                if re.match(r'^(\d+)\.\s+', next_line):
                    break
                
                if not next_line:
                    i += 1
                    continue
                
                # Check for option
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
                
                i += 1
            
            if not answer:
                continue
            
            # Determine type
            if '(True/False)' in q_text or '(T/F)' in q_text:
                q_type = 'true_false'
                q_text = q_text.replace('(True/False)', '').replace('(T/F)', '').strip()
                correct = 'True' if answer.lower() in ['true', 't'] else 'False'
                points = 1
            elif options and len(options) >= 2:
                q_type = 'mcq'
                correct = answer
                if len(answer) == 1 and answer.lower() in 'abcd':
                    idx = ord(answer.lower()) - ord('a')
                    if 0 <= idx < len(options):
                        correct = options[idx]
                points = 1
            else:
                q_type = 'short_answer'
                correct = answer
                # Detect type for points
                if any(w in q_text.lower() for w in ['define', 'what is']):
                    points = 2
                elif any(w in q_text.lower() for w in ['explain', 'why']):
                    points = 5
                elif any(w in q_text.lower() for w in ['describe']):
                    points = 4
                elif any(w in q_text.lower() for w in ['analyze']):
                    points = 6
                else:
                    points = 3
            
            questions.append({
                'question_text': q_text,
                'question_type': q_type,
                'options': options if q_type == 'mcq' else [],
                'correct_answer': correct,
                'points': points
            })
        
        # Save to database
        created = 0
        for q in questions:
            try:
                db_q = Question(
                    question_text=q['question_text'],
                    question_type=q['question_type'],
                    options=q['options'],
                    correct_answer=q['correct_answer'],
                    points=q['points'],
                    department=department,
                    level=level,
                    lesson_id=lesson_id,
                    created_by=current_user.id
                )
                db.add(db_q)
                created += 1
            except:
                pass
        
        db.commit()
        
        return {
            'success': True,
            'message': f'✅ Successfully imported {created} questions',
            'total': created,
            'questions': questions[:5]  # Return first 5 for preview
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
