"""
Course Manager Module
Handles course creation, loading, and management using SQLite database
"""

from datetime import datetime
from typing import Dict, List, Optional


class CourseManager:
    """Manages course information and operations"""
    
    def __init__(self, db):
        """
        Initialize course manager
        
        Args:
            db: DatabaseManager instance
        """
        self.db = db
        self.current_course = None
    
    def create_course(self, code: str, name: str, semester: str) -> bool:
        """
        Create a new course
        
        Args:
            code: Course code (e.g., CS101)
            name: Course name
            semester: Semester information
            
        Returns:
            bool: True if successful, False otherwise
        """
        created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_modified = created_date
        
        if self.db.create_course(code, name, semester, created_date, last_modified):
            self.current_course = {
                "code": code,
                "name": name,
                "semester": semester,
                "created_date": created_date,
                "last_modified": last_modified
            }
            return True
        return False
    
    def load_course(self, code: str) -> bool:
        """
        Load an existing course
        
        Args:
            code: Course code to load
            
        Returns:
            bool: True if successful, False otherwise
        """
        course = self.db.get_course(code)
        if course:
            self.current_course = course
            return True
        return False
    
    def list_courses(self) -> List[Dict]:
        """
        List all available courses
        
        Returns:
            List of course dictionaries
        """
        return self.db.get_all_courses()
    
    def save_course(self) -> bool:
        """
        Save current course data
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.current_course:
            return False
        
        last_modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return self.db.update_course(
            self.current_course['code'],
            self.current_course.get('name'),
            self.current_course.get('semester'),
            last_modified
        )