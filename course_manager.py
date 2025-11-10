import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class CourseManager:
    """Manages course information and operations"""
    
    def __init__(self):
        self.courses_dir = "courses"
        self.current_course = None
        self._initialize_directories()
    
    def _initialize_directories(self):
        """Create necessary directories if they don't exist"""
        if not os.path.exists(self.courses_dir):
            os.makedirs(self.courses_dir)
    
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
        course_file = os.path.join(self.courses_dir, f"{code}.json")
        
        if os.path.exists(course_file):
            return False
        
        course_data = {
            "code": code,
            "name": name,
            "semester": semester,
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(course_file, 'w') as f:
            json.dump(course_data, f, indent=4)
        
        self.current_course = course_data
        return True
    
    def load_course(self, code: str) -> bool:
        """
        Load an existing course
        
        Args:
            code: Course code to load
            
        Returns:
            bool: True if successful, False otherwise
        """
        course_file = os.path.join(self.courses_dir, f"{code}.json")
        
        if not os.path.exists(course_file):
            return False
        
        with open(course_file, 'r') as f:
            self.current_course = json.load(f)
        
        return True
    
    def list_courses(self) -> List[Dict]:
        """
        List all available courses
        
        Returns:
            List of course dictionaries
        """
        courses = []
        
        if not os.path.exists(self.courses_dir):
            return courses
        
        for filename in os.listdir(self.courses_dir):
            if filename.endswith('.json'):
                course_file = os.path.join(self.courses_dir, filename)
                with open(course_file, 'r') as f:
                    courses.append(json.load(f))
        
        return sorted(courses, key=lambda x: x['code'])
    
    def save_course(self) -> bool:
        """
        Save current course data
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.current_course:
            return False
        
        course_file = os.path.join(self.courses_dir, f"{self.current_course['code']}.json")
        self.current_course['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(course_file, 'w') as f:
            json.dump(self.current_course, f, indent=4)
        
        return True
    
    def get_course_path(self, code: str) -> str:
        """Get the file path for a course"""
        return os.path.join(self.courses_dir, f"{code}.json")

