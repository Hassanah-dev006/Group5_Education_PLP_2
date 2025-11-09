import json
import os
import csv
from typing import Dict, List, Optional


class StudentManager:
    """Manages student information and operations"""
    
    def __init__(self):
        self.students_dir = "students"
        self.course_code = None
        self.students = {}
        self._initialize_directories()
    
    def _initialize_directories(self):
        """Create necessary directories if they don't exist"""
        if not os.path.exists(self.students_dir):
            os.makedirs(self.students_dir)
    
    def set_course(self, course_code: str):
        """
        Set the current course and load its students
        
        Args:
            course_code: Course code to work with
        """
        self.course_code = course_code
        self._load_students()
    
    def _get_students_file(self) -> str:
        """Get the students file path for current course"""
        if not self.course_code:
            return None
        return os.path.join(self.students_dir, f"{self.course_code}_students.json")
    
    def _load_students(self):
        """Load students for current course"""
        students_file = self._get_students_file()
        
        if not students_file or not os.path.exists(students_file):
            self.students = {}
            return
        
        with open(students_file, 'r') as f:
            self.students = json.load(f)
    
    def _save_students(self) -> bool:
        """Save students to file"""
        students_file = self._get_students_file()
        
        if not students_file:
            return False
        
        with open(students_file, 'w') as f:
            json.dump(self.students, f, indent=4)
        
        return True
    
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
        if student_id in self.students:
            return False
        
        self.students[student_id] = {
            "id": student_id,
            "name": name,
            "email": email
        }
        
        return self._save_students()
    
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
        if student_id not in self.students:
            return False
        
        if name:
            self.students[student_id]["name"] = name
        if email is not None:
            self.students[student_id]["email"] = email
        
        return self._save_students()
    
    def remove_student(self, student_id: str) -> bool:
        """
        Remove a student
        
        Args:
            student_id: Student identifier
            
        Returns:
            bool: True if successful, False if student not found
        """
        if student_id not in self.students:
            return False
        
        del self.students[student_id]
        return self._save_students()
    
    def import_from_csv(self, filename: str) -> int:
        """
        Import students from CSV file
        
        Args:
            filename: Path to CSV file
            
        Returns:
            Number of students imported
        """
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

