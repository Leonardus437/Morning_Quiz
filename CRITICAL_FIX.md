# 🚨 CRITICAL FIXES NEEDED

## Issue 1: Admin Cannot Generate Credentials ❌

**Problem**: Admin selects department and level, but no students found.

**Root Cause**: Department name mismatch
- Admin stores: "Software Development", "Land Surveying", etc. (FULL NAMES)
- Backend expects: "SWD", "LSV", etc. (SHORT CODES)
- Students are stored with FULL NAMES in database

**Solution**: Remove the department code conversion in admin page

**File**: `frontend/src/routes/admin/+page.svelte`
**Line**: 685

**CHANGE FROM**:
```javascript
const deptCode = getDepartmentCode(uploadSelectedDepartment);
console.log('Generating credentials for:', deptCode, uploadSelectedLevel);

const blob = await api.generateStudentCredentialsPDF(deptCode, uploadSelectedLevel);
```

**CHANGE TO**:
```javascript
// Use FULL department name, not code
console.log('Generating credentials for:', uploadSelectedDepartment, uploadSelectedLevel);

const blob = await api.generateStudentCredentialsPDF(uploadSelectedDepartment, uploadSelectedLevel);
```

---

## Issue 2: Teacher Lessons Dropdown Empty ❌

**Problem**: Teacher has lessons assigned by DOS, but dropdown shows "Select Lesson" only.

**Root Cause**: The `filteredLessons` function works correctly, but we need to verify:
1. Backend returns lessons in correct format
2. Department/Level values match exactly

**Debugging Steps**:

1. **Check what backend returns**:
   - Open browser console (F12)
   - Look for: `Teacher assigned lessons: X [array]`
   - Verify the lesson objects have: `id`, `title`, `department`, `level`

2. **Check department/level matching**:
   - When creating question, check console for: `Filtering lessons: { dept, level, teacherAssignedLessons, filtered, lessons }`
   - Verify `dept` and `level` EXACTLY match lesson's `department` and `level`

**Possible Issues**:
- Department: "Software Development" vs "SWD" mismatch
- Level: "Level 5" vs "L5" mismatch
- Lessons have different department/level than selected

**Solution**: Ensure consistent naming

---

## IMMEDIATE ACTION REQUIRED

### Step 1: Fix Credentials Generation (CRITICAL)

Edit `frontend/src/routes/admin/+page.svelte` line 685:

```javascript
// OLD CODE (line 683-687):
const deptCode = getDepartmentCode(uploadSelectedDepartment);
console.log('Generating credentials for:', deptCode, uploadSelectedLevel);

const blob = await api.generateStudentCredentialsPDF(deptCode, uploadSelectedLevel);

// NEW CODE:
console.log('Generating credentials for:', uploadSelectedDepartment, uploadSelectedLevel);

const blob = await api.generateStudentCredentialsPDF(uploadSelectedDepartment, uploadSelectedLevel);
```

### Step 2: Verify Lesson Data

1. Login as teacher
2. Open browser console (F12)
3. Go to "Add Question" tab
4. Select department and level
5. Check console output for lesson filtering
6. Take screenshot and share

### Step 3: Check Student Data

Run this in browser console while logged in as admin:

```javascript
fetch('http://localhost:8000/admin/students', {
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
})
.then(r => r.json())
.then(data => {
  console.log('Total students:', data.total);
  console.log('Sample student:', data.students[0]);
  console.log('Departments:', [...new Set(data.students.map(s => s.department))]);
  console.log('Levels:', [...new Set(data.students.map(s => s.level))]);
});
```

This will show EXACT department and level names in database.

---

## Expected Results After Fix

✅ **Credentials Generation**:
- Admin selects "Software Development" + "Level 5"
- System finds students with department="Software Development" and level="Level 5"
- PDF generates successfully

✅ **Lessons Dropdown**:
- Teacher creates question
- Selects department and level
- Dropdown shows all assigned lessons for that department/level
- Can select lesson and create question

---

## If Still Not Working

**For Credentials**:
1. Check if students exist: Go to Admin → Students tab
2. Verify department and level names EXACTLY match dropdown values
3. Check browser console for errors

**For Lessons**:
1. Check browser console for "Teacher assigned lessons" log
2. Verify lessons have correct department/level
3. Ensure department/level in dropdown EXACTLY matches lesson data

---

## Contact Support

If issues persist after applying fixes:
1. Take screenshot of browser console (F12)
2. Take screenshot of Admin → Students tab
3. Take screenshot of DOS → Assignments tab (showing teacher's lessons)
4. Share all three screenshots

