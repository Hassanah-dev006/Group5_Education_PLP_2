"""
Student Manager Module
Handles student enrollment and management using SQLite database
"""

import csv
from typing import Dict, List, Optional


class StudentManager:
    """Manages student information and operations"""
    
    def __init__(self, db):
        """
        Initialize student manager
        
        Args:
            db: DatabaseManager instance
        """
        self.db = db
        self.course_code = None
        self.students = {}
    
    def set_course(self, course_code: str):
        """
        Set the current course and load its students
        
        Args:
            course_code: Course code to work with
        """
        self.course_code = course_code
        self._load_students()
    
    def _load_students(self):
        """Load students for current course from database"""
        if not self.course_code:
            self.students = {}
            return
        
        students_list = self.db.get_all_students(self.course_code)
        self.students = {s['id']: s for s in students_list}
    
    def add_student(self, student_id: str, name: str, email: str = "") -> bool:
        """
        Add a new student
        
        Args:
            student_id: Unique student identifier
            name: Student's full name
            email: Student's email address (optional)
            
        Returns:
            bool: True if successful, False if student already exists
        """
        if not self.course_code:
            return False
        
        if self.db.add_student(student_id, self.course_code, name, email):
            self.students[student_id] = {
                "id": student_id,
                "course_code": self.course_code,
                "name": name,
                "email": email
            }
            return True
        return False
    
    def get_student(self, student_id: str) -> Optional[Dict]:
        """
        Get student information
        
        Args:
            student_id: Student identifier
            
        Returns:
            Student dictionary or None if not found
        """
        return self.students.get(student_id)
    
    def get_all_students(self) -> List[Dict]:
        """
        Get all students
        
        Returns:
            List of student dictionaries
        """
        return list(self.students.values())
    
    def update_student(self, student_id: str, name: Optional[str] = None, 
                      email: Optional[str] = None) -> bool:
        """
        Update student information
        
        Args:
            student_id: Student identifier
            name: New name (optional)
            email: New email (optional)
            
        Returns:
            bool: True if successful, False if student not found
        """
        if not self.course_code or student_id not in self.students:
            return False
        
        if self.db.update_student(student_id, self.course_code, name, email):
            if name:
                self.students[student_id]["name"] = name
            if email is not None:
                self.students[student_id]["email"] = email
            return True
        return False
    
    def remove_student(self, student_id: str) -> bool:
        """
        Remove a student
        
        Args:
            student_id: Student identifier
            
        Returns:
            bool: True if successful, False if student not found
        """
        if not self.course_code or student_id not in self.students:
            return False
        
        if self.db.delete_student(student_id, self.course_code):
            del self.students[student_id]
            return True
        return False
    
    def import_from_csv(self, filename: str) -> int:
        """
        Import students from CSV file
        
        Args:
            filename: Path to CSV file
            
        Returns:
            Number of students imported
        """
        if not self.course_code:
            return 0
        
        import os
        if not os.path.exists(filename):
            return 0
        
        count = 0
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    student_id = row.get('student_id', '').strip().upper()
                    name = row.get('name', '').strip()
                    email = row.get('email', '').strip()
                    
                    if student_id and name:
                        if self.add_student(student_id, name, email):
                            count += 1
        except Exception as e:
            print(f"Error importing CSV: {e}")
            return 0
        
        return count
    
    def export_to_csv(self, filename: str) -> bool:
        """
        Export students to CSV file
        
        Args:
            filename: Path to output CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['student_id', 'name', 'email']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for student in self.students.values():
                    writer.writerow({
                        'student_id': student['id'],
                        'name': student['name'],
                        'email': student.get('email', '')
                    })
            return True
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False