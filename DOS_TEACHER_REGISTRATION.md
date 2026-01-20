# DOS Teacher Registration Feature

## Overview
The DOS (Deputy of Studies) can now register new teachers through a dedicated admin interface. This feature ensures proper access control and streamlined teacher onboarding.

## How It Works

### 1. Access Requirements
- Only users with `admin` role (DOS) can register teachers
- Must be logged into the DOS admin panel at `/admin`

### 2. Registration Process

#### Step 1: Navigate to Teacher Registration
1. Login to DOS admin panel with admin credentials
2. Click on the "Register Teacher" tab in the navigation

#### Step 2: Fill Teacher Information
- **Username**: Unique identifier for the teacher
- **Password**: Initial password (teacher can change later)
- **Full Name**: Teacher's complete name
- **Departments**: Select one or more departments the teacher will handle

#### Step 3: Submit Registration
- Click "Register Teacher" button
- System validates all fields and department selection
- Success message shows username and password for the teacher

### 3. Available Departments
- Software Development
- Computer System and Architecture
- Land Surveying
- Building Construction

### 4. Security Features
- ✅ Only DOS (admin role) can register teachers
- ✅ Username uniqueness validation
- ✅ Password hashing for security
- ✅ Department assignment validation
- ✅ Proper error handling and feedback

## API Endpoint

### POST `/admin/register-teacher`

**Headers:**
```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "teacher001",
  "password": "secure_password",
  "full_name": "John Doe",
  "role": "teacher",
  "departments": ["Software Development", "Computer System and Architecture"]
}
```

**Response (Success):**
```json
{
  "message": "Teacher registered successfully",
  "teacher": {
    "id": 123,
    "username": "teacher001",
    "full_name": "John Doe",
    "departments": ["Software Development", "Computer System and Architecture"],
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Response (Error):**
```json
{
  "detail": "Username already exists"
}
```

## Usage Instructions

### For DOS (Admin):
1. Login to admin panel: `http://localhost:3000/admin`
2. Use default credentials: `admin` / `admin123`
3. Navigate to "Register Teacher" tab
4. Fill in teacher details and select departments
5. Click "Register Teacher"
6. Share the generated credentials with the new teacher

### For New Teachers:
1. Receive username and password from DOS
2. Login at teacher portal: `http://localhost:3000/teacher`
3. Use provided credentials to access teacher features
4. Can create questions and manage quizzes for assigned departments

## Integration with Existing System

The teacher registration integrates seamlessly with:
- **Lesson Management**: Teachers can only create questions for lessons in their assigned departments
- **Quiz Creation**: Teachers can create quizzes for their departments
- **Question Bank**: Teachers see only questions from their departments or ones they created
- **Teacher-Lesson Assignments**: DOS can assign specific lessons to registered teachers

## Testing

Run the test script to verify functionality:
```bash
python test_teacher_registration.py
```

This tests:
- DOS login and teacher registration
- Teacher login with new credentials
- Duplicate username prevention
- Access control (non-admin cannot register teachers)

## Benefits

1. **Centralized Control**: DOS maintains full control over teacher accounts
2. **Department Management**: Teachers are properly assigned to relevant departments
3. **Security**: Proper authentication and authorization
4. **Audit Trail**: All registrations are logged with timestamps
5. **Integration**: Seamless integration with existing lesson and quiz management