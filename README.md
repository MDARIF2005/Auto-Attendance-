# Smart Attendance Platform

## Overview
A web-based platform for automated attendance management in schools and colleges. Supports organization registration, admin/faculty/student management, attendance tracking, and timetable management.

## Features
- Organization registration and management
- Admin, faculty, and student registration/login
- Attendance tracking for students and faculty
- Timetable management
- Role-based dashboards
- Filtering by academic year, branch, section, department

## Requirements

### Python Packages
- Flask
- pyrebase

Install requirements:
```bash
pip install flask pyrebase
```

### Firebase
- Create a Firebase project
- Enable Realtime Database and Authentication
- Add your Firebase config to `firebase.py`

### File Structure
```
app.py
firebase.py
requirements.txt
README.md
/templates/
    index.html
    ograisationreg.html
    admin_base.html
    admin.html
    organisation.html
    student_base.html
```

## How to Run
1. Install requirements
2. Set up Firebase config in `firebase.py`
3. Run the app:
```bash
python app.py
```
4. Open your browser at `http://localhost:5000`

## Usage
- Register your organization and admin
- Login as admin to access the dashboard
- Add students, faculty, attendance, and timetables
- Use filters to view and manage data

## License
MIT
