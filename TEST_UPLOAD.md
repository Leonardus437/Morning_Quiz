# Student Upload Test - Department/Level Fix

## Issue
Students uploaded with wrong department/level showing as "undefined" in statistics.

## Root Cause
Frontend wasn't validating department/level selection before upload.

## Fixes Applied

1. **Frontend validation**: Now requires department/level selection BEFORE file upload
2. **Response handling**: Fixed to show correct department/level from form data
3. **Visual warning**: Added yellow warning box to emphasize selection requirement

## Test Steps

1. Login as admin (username: `admin`, password: `admin123`)
2. Go to Students tab
3. Click "Upload Students"
4. **FIRST**: Select Department (e.g., "Land Surveying") and Level (e.g., "L3")
5. **THEN**: Choose your Excel/PDF file
6. File will auto-process and upload
7. Verify statistics show correct department/level

## Generate Credentials

1. Click "Generate Credentials" button
2. Select SAME department and level you used for upload
3. Click "Generate PDF"
4. PDF will download with all student credentials

## Database Verification

Check students in database:
```bash
docker exec tvet_quiz-db-1 psql -U quiz_user -d morning_quiz -c "SELECT username, full_name, department, level FROM users WHERE role='student' AND department='Land Surveying' AND level='L3' LIMIT 5;"
```

## Expected Result
- Statistics show correct department/level
- Students saved with correct values in database
- Credentials PDF generates successfully for that department/level
