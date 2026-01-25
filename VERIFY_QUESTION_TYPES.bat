@echo off
echo ========================================
echo Checking Question Types in Database
echo ========================================
echo.

cd backend
python -c "from sqlalchemy import create_engine, text; engine = create_engine('sqlite:///quiz.db'); conn = engine.connect(); result = conn.execute(text('SELECT DISTINCT question_type FROM questions')); types = [row[0] for row in result]; print('\n=== QUESTION TYPES FOUND ==='); [print(f'{i+1}. {t}') for i, t in enumerate(types)]; print(f'\nTotal: {len(types)} types'); conn.close()"

echo.
echo ========================================
echo.
echo Expected 12 types:
echo 1. multiple_choice
echo 2. multiple_select
echo 3. true_false
echo 4. dropdown
echo 5. fill_blanks
echo 6. drag_drop_match
echo 7. drag_drop_order
echo 8. linear_scale
echo 9. code_writing
echo 10. sql_query
echo 11. short_answer
echo 12. essay
echo.
pause
