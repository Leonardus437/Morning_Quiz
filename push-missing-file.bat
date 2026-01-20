@echo off
cd /d "d:\Morning_Quiz-master"
echo Adding performance_reports.py...
git add backend/performance_reports.py
git add backend/main.py
git add backend/ai_grader.py
git commit -m "Add missing performance_reports.py and fix backend imports"
git push origin main
echo Done!
pause
