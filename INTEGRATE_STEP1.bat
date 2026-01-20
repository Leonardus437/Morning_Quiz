@echo off
echo ========================================
echo TVET Quiz - Teacher Enhancement Step 1
echo Bulk Question Upload Integration
echo ========================================
echo.
echo This script will:
echo 1. Add bulk upload endpoint to backend
echo 2. Add template generator endpoint
echo 3. Restart backend
echo.
echo SAFE: Only ADDS new code, doesn't modify existing
echo.
pause

cd backend

echo.
echo [1/3] Adding imports...
echo. >> main.py
echo # BULK UPLOAD - STEP 1 >> main.py
echo from bulk_question_upload import handle_bulk_upload >> main.py
echo from template_generator import generate_question_template >> main.py

echo.
echo [2/3] Adding upload endpoint...
echo. >> main.py
echo @app.post("/questions/upload-bulk") >> main.py
echo async def upload_questions_bulk( >> main.py
echo     file: UploadFile = File(...), >> main.py
echo     department: str = Form(...), >> main.py
echo     level: str = Form(...), >> main.py
echo     lesson_id: int = Form(...), >> main.py
echo     current_user: User = Depends(get_current_user), >> main.py
echo     db: Session = Depends(get_db) >> main.py
echo ): >> main.py
echo     if current_user.role != "teacher": >> main.py
echo         raise HTTPException(status_code=403, detail="Teacher access required") >> main.py
echo     return await handle_bulk_upload(file, department, level, lesson_id) >> main.py

echo.
echo [3/3] Adding template endpoint...
echo. >> main.py
echo @app.get("/questions/template/excel") >> main.py
echo async def download_question_template(): >> main.py
echo     from fastapi.responses import StreamingResponse >> main.py
echo     import io >> main.py
echo     template_bytes = generate_question_template() >> main.py
echo     return StreamingResponse( >> main.py
echo         io.BytesIO(template_bytes), >> main.py
echo         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", >> main.py
echo         headers={"Content-Disposition": "attachment; filename=Question_Template.xlsx"} >> main.py
echo     ) >> main.py

cd ..

echo.
echo ========================================
echo ✅ Backend integration complete!
echo ========================================
echo.
echo Next steps:
echo 1. Restart backend: docker-compose restart backend
echo 2. Follow STEP1_TESTING_GUIDE.md for frontend integration
echo 3. Test the new feature!
echo.
echo Endpoints added:
echo - POST /questions/upload-bulk
echo - GET /questions/template/excel
echo.
pause
