# PDF-Only Student Upload Guide

## ✅ System Updated - PDF Only

The student upload system now accepts **PDF files only** for maximum reliability and consistency.

## Why PDF Only?

- ✅ **100% Reliable** - No Excel version compatibility issues
- ✅ **Consistent Format** - PDF is standardized across all systems
- ✅ **Simple** - One format, one parser, no confusion
- ✅ **Universal** - Works on any device, any OS

## How to Upload Students

### Step 1: Prepare Your Student List

Create a simple numbered list in any program (Word, Excel, Notepad):

```
Department: Software Development
Level: Level 5

1. John Doe
2. Jane Smith
3. Alice Johnson
4. Bob Williams
5. Charlie Brown
```

### Step 2: Export as PDF

**From Microsoft Word:**
- File → Save As → Choose "PDF" format

**From Microsoft Excel:**
- File → Save As → Choose "PDF" format

**From Google Docs:**
- File → Download → PDF Document

**From Notepad/Text Editor:**
- Print → Save as PDF (use Microsoft Print to PDF)

### Step 3: Upload to System

1. Login as DOS/Admin
2. Go to "Students" section
3. Click "📄 Upload Student List"
4. Select your PDF file
5. Click "✅ Upload Students"

## PDF Format Requirements

Your PDF should contain:
- **Numbered list** of student names (1, 2, 3...)
- **Department name** (optional, in header)
- **Level** (optional, in header)
- **One student per line**

### Example PDF Content:

```
STUDENT LIST - SOFTWARE DEVELOPMENT LEVEL 5

1. UWIMANA Jean
2. MUGISHA Patrick
3. ISHIMWE Grace
4. NIYONZIMA Eric
5. MUKAMANA Sarah
```

## What Happens After Upload?

The system will:
1. Extract student names from PDF
2. Generate usernames: `student001`, `student002`, etc.
3. Set default password: `student123`
4. Assign to specified department and level
5. Show success message with count

## Troubleshooting

**"No students found in PDF"**
- Ensure your PDF has numbered list (1, 2, 3...)
- Check that names are clearly visible
- Avoid complex formatting

**"PDF parsing error"**
- Make sure file is actually PDF format
- Try re-exporting from original document
- Ensure PDF is not password-protected

**Wrong department/level assigned**
- Add department and level in PDF header
- Or manually edit students after upload

## Default Credentials

After upload, all students get:
- **Username**: `student001`, `student002`, etc.
- **Password**: `student123`
- **Role**: Student

Students can login immediately with these credentials.

## Tips for Best Results

1. **Keep it simple** - Plain numbered list works best
2. **One name per line** - Don't combine multiple students
3. **Clear formatting** - Use standard fonts and sizes
4. **Test with small list** - Upload 5 students first to verify
5. **Check after upload** - Verify students appear in system

## Need Help?

Contact your system administrator or IT support for assistance.
