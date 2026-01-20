@echo off
echo Starting Complete RTB Generator...
cd backend
pip install -r requirements.txt
python rtb_complete_api.py
pause
