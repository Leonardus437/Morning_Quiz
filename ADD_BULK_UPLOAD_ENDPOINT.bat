@echo off
echo ========================================
echo Adding Bulk Question Upload Endpoint
echo ========================================
echo.
echo This will ADD a new endpoint to backend/main.py
echo WITHOUT modifying existing code
echo.
pause

cd backend

echo.
echo Adding import statement...
echo from bulk_question_upload import handle_bulk_upload >> main.py

echo.
echo Adding endpoint...
echo. >> main.py
echo # BULK QUESTION UPLOAD - NEW FEATURE >> main.py
echo @app.post("/questions/upload-bulk") >> main.py
echo async def upload_questions_bulk( >> main.py
echo     file: UploadFile = File(...), >> main.py
echo     department: str = Form(...), >> main.py
echo     level: str = Form(...), >> main.py
echo     lesson_id: int = Form(...), >> main.py
echo     current_user: User = Depends(get_current_user), >> main.py
echo     db: Session = Depends(get_db) >> main.py
echo ): >> main.py
echo     """Upload questions from Excel/Word/PDF""" >> main.py
echo     if current_user.role != "teacher": >> main.py
echo         raise HTTPException(status_code=403, detail="Teacher access required") >> main.py
echo     return await handle_bulk_upload(file, department, level, lesson_id) >> main.py

echo.
echo ✅ Endpoint added successfully!
echo.
echo Next steps:
echo 1. Restart backend: docker-compose restart backend
echo 2. Test endpoint: http://localhost:8000/docs
echo.
pause
