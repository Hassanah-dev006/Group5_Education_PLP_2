# PyGrade - Automated Grading System

A Python-based command-line grading system with SQLite database for managing courses, students, assignments, and grades.

---

## Features

✅ SQLite database backend  
✅ User authentication (Lecturer & Student roles)  
✅ Course and student management  
✅ Weighted grade calculation  
✅ Automatic outlier detection  
✅ CSV import/export  
✅ PDF report generation  

---

## Requirements

- Python 3.7+
- ReportLab library

---

## Installation
```bash
# 1. Install dependency
pip install reportlab

# 2. Run PyGrade
python3 pygrade.py
```

---

## Quick Start

### Default Login
```
Lecturer: admin / admin123
Student:  student1 / student123
```

### Basic Workflow
1. Login as lecturer
2. Create a course (Course Management → Create New Course)
3. Add students (Student Management → Import from CSV)
4. Create assignments with weights (Assignment Management)
5. Enter grades (Grade Management → Bulk Import)
6. Calculate final grades
7. Generate reports

---

## File Structure
```
pygrade/
├── pygrade.py              # Main application
├── database.py             # Database manager
├── course_manager.py       # Course operations
├── student_manager.py      # Student operations
├── assignment_manager.py   # Assignment operations
├── grade_manager.py        # Grade calculations
├── report_generator.py     # Report generation
├── utils.py                # Helper functions
├── pygrade.db              # SQLite database (auto-created)
├── sample_students.csv     # Sample data
└── sample_grades.csv       # Sample data
```

**Total**: 8 Python files (~3,700 lines of code)

---

## CSV File Formats

### Students (`students.csv`)
```csv
student_id,name,email
S001,John Doe,john@example.com
S002,Jane Smith,jane@example.com
```

### Grades (`grades.csv`)
```csv
student_id,assignment_title,score
S001,Midterm Exam,85
S002,Midterm Exam,92
```

---

## Grading Scale

| Grade | Range |
|-------|-------|
| A     | 90-100 |
| B     | 80-89  |
| C     | 70-79  |
| D     | 60-69  |
| F     | 0-59   |

**Formula**: `Final Grade = Σ(Score/Max × Weight × 100)`

---

## Database

All data stored in `pygrade.db` (SQLite):

- **users** - User accounts
- **courses** - Course information
- **students** - Student enrollment
- **assignments** - Assignment definitions
- **grades** - Grade records

### Backup
```bash
# Backup database
cp pygrade.db backup.db

# Reset system
rm pygrade.db && python3 pygrade.py
```

---

## Troubleshooting

### No output when running
```bash
python3 pygrade.py 2>&1
```

### PDF export fails
```bash
pip install reportlab --break-system-packages
```

### Login not working
```bash
# Remove database and restart
rm pygrade.db
python3 pygrade.py
```

### CSV import fails
- Check file encoding (must be UTF-8)
- Verify column headers match format
- Ensure student IDs and assignments exist

### Check installation
```bash
python3 --version  # Should be 3.7+
python3 -c "import reportlab; print('OK')"
```

---

## Main Menu
```
LECTURER MENU:
1. Course Management     → Create/load courses
2. Student Management    → Add/import students
3. Assignment Management → Define assignments
4. Grade Management      → Enter/import grades
5. Reports & Analytics   → Generate reports
6. Help & Documentation
7. Logout

STUDENT MENU:
1. View My Grades        → See all grades
2. View Course Info      → Course details
3. Logout
```

---

## Key Commands
```bash
# Run application
python3 pygrade.py

# View database
sqlite3 pygrade.db ".tables"

# Query data
sqlite3 pygrade.db "SELECT * FROM courses;"

# Backup
cp pygrade.db pygrade_backup_$(date +%Y%m%d).db
```

---

## Features Overview

### For Lecturers
- Create and manage multiple courses
- Import students from CSV (bulk operation)
- Define weighted assignments (must total 100%)
- Enter grades individually or bulk import
- Automatic grade calculation
- Outlier detection (missing, unusual scores)
- Generate reports (Text, CSV, PDF)
- View class statistics

### For Students
- View personal grades
- See weighted totals and letter grades
- View course information
- Secure access (cannot see other students' data)

---

## Important Notes

⚠️ **Assignment Weights**: Must total 1.0 (100%)  
⚠️ **Data Storage**: All data in `pygrade.db` - backup regularly  
⚠️ **CSV Encoding**: Files must be UTF-8  
⚠️ **Passwords**: Stored as SHA-256 hashes  

---

## Quick Reference

| Action | Path |
|--------|------|
| Create Course | Main Menu → 1 → 1 |
| Import Students | Main Menu → 2 → 2 |
| Create Assignment | Main Menu → 3 → 1 |
| Import Grades | Main Menu → 4 → 2 |
| Calculate Finals | Main Menu → 4 → 4 |
| Generate Report | Main Menu → 5 → 1 |

---

## System Info

**Version**: 1.0.0 (SQLite Edition)  
**Language**: Python 3.7+  
**Database**: SQLite 3  
**Platforms**: Windows, macOS, Linux