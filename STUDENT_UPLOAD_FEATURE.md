# Student Upload Feature - Implementation Guide

## Overview
Admin can now upload Excel files with student lists. The system will automatically:
- Parse the Excel file (Book1.xlsx format)
- Extract class group, department, and level
- Generate usernames from student names
- Create accounts with default password: `student123`

## Excel File Format (Book1.xlsx)
```
Row 1: School Name (e.g., "RUNDA TSS")
Row 2: Class Group (e.g., "Class Group: L5CSA")
Row 3: Empty
Row 4: Headers (S/N, Names)
Row 5+: Student data (1, STUDENT NAME)
```

## Backend Implementation

### 1. Add to main.py
Copy the code from `student_upload_endpoint.py` and add it to `backend/main.py`

### 2. Import Required Module
Add at the top of main.py:
```python
from student_import import parse_student_excel, hash_password
```

## Frontend Implementation (Admin Panel)

Add this to the admin dashboard (`frontend/src/routes/admin/+page.svelte`):

```svelte
<script>
let uploadFile = null;
let uploading = false;
let uploadResult = null;

async function uploadStudentExcel() {
    if (!uploadFile) {
        alert('Please select an Excel file');
        return;
    }
    
    uploading = true;
    uploadResult = null;
    
    try {
        const formData = new FormData();
        formData.append('file', uploadFile);
        
        const response = await fetch('http://localhost:8000/admin/upload-students-excel', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        
        uploadResult = await response.json();
        uploadFile = null;
        
        alert(`Success! Created: ${uploadResult.created}, Updated: ${uploadResult.updated}`);
    } catch (error) {
        alert(`Upload failed: ${error.message}`);
    } finally {
        uploading = false;
    }
}
</script>

<!-- Add this section to admin panel -->
<div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
    <h3>📤 Upload Student List (Excel)</h3>
    <p style="color: #666; margin-bottom: 15px;">
        Upload an Excel file with student names. System will auto-generate usernames and passwords.
    </p>
    
    <input 
        type="file" 
        accept=".xlsx,.xls"
        on:change={(e) => uploadFile = e.target.files[0]}
        style="margin-bottom: 10px;"
    />
    
    <button 
        on:click={uploadStudentExcel}
        disabled={uploading || !uploadFile}
        style="padding: 10px 20px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer;"
    >
        {uploading ? 'Uploading...' : 'Upload Students'}
    </button>
    
    {#if uploadResult}
        <div style="margin-top: 15px; padding: 15px; background: #d4edda; border-radius: 4px;">
            <p><strong>✅ Import Successful!</strong></p>
            <p>Class: {uploadResult.class_group}</p>
            <p>Department: {uploadResult.department} | Level: {uploadResult.level}</p>
            <p>Created: {uploadResult.created} | Updated: {uploadResult.updated}</p>
            <p style="color: #666; font-size: 14px; margin-top: 10px;">
                Default password for all students: <strong>student123</strong>
            </p>
        </div>
    {/if}
</div>
```

## Usage Instructions

### For Admin:
1. Login to admin panel
2. Go to "Upload Students" section
3. Click "Choose File" and select Excel file (Book1.xlsx format)
4. Click "Upload Students"
5. System will:
   - Parse the file
   - Extract class group (e.g., L5CSA)
   - Generate usernames from names
   - Create accounts with password: `student123`

### Username Generation Rules:
- Remove all non-alphabetic characters
- Convert to lowercase
- Limit to 15 characters
- Example: "ABAYISENGA HALLELUA" → "abayisengahalle"

### Default Credentials:
- Username: Auto-generated from name
- Password: `student123` (same for all)

## Testing

1. Use the provided `Book1.xlsx` template
2. Upload via admin panel
3. Verify students can login with generated credentials
4. Check student list in admin panel

## Files Created:
- `backend/student_import.py` - Excel parsing logic
- `backend/student_upload_endpoint.py` - API endpoint code
- `import_students_docker.py` - Command-line import script (already working)

## Notes:
- Excel file must follow the Book1.xlsx format
- System handles duplicate usernames (updates existing)
- All students get default password: `student123`
- Admin can download credentials list after upload
