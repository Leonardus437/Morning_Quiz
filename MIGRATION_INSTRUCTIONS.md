# DATABASE MIGRATION FOR RENDER

## Problem
The Render PostgreSQL database is missing columns that were added in recent updates.

## Error
```
column quiz_attempts.percentage does not exist
```

## Solution: Run Manual Migration

### Option 1: Via Render Shell (RECOMMENDED)

1. Go to https://dashboard.render.com
2. Select your `tvet-quiz-backend` service
3. Click "Shell" tab
4. Run:
```bash
python migrate_db.py
```

### Option 2: Via Local Script with Render Database URL

1. Get your DATABASE_URL from Render:
   - Go to https://dashboard.render.com
   - Select your PostgreSQL database
   - Copy the "External Database URL"

2. Run locally:
```bash
cd backend
set DATABASE_URL=your_database_url_here
python migrate_db.py
```

### Option 3: Force Redeploy

If migrations still don't work, the startup event should run them automatically:

1. Go to https://dashboard.render.com
2. Select `tvet-quiz-backend`
3. Click "Manual Deploy" → "Clear build cache & deploy"

## Verify Migration

After running migration, test:
```bash
curl https://tvet-quiz-backend.onrender.com/health
```

Should return status 200 with no database errors in logs.

## What Gets Added

The migration adds these columns:
- `quiz_attempts.percentage` (FLOAT)
- `quiz_attempts.grade` (VARCHAR)
- `quiz_attempts.total_possible_points` (FLOAT)
- `questions.question_config` (JSON)
- `questions.correct_answers` (JSON)
- And 10+ more columns for advanced features
