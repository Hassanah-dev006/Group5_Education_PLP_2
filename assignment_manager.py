"""
Assignment Manager Module
Handles assignment creation and management using SQLite database
"""

from typing import Dict, List, Optional


class AssignmentManager:
    """Manages assignment information and operations"""
    
    def __init__(self, db):
        """
        Initialize assignment manager
        
        Args:
            db: DatabaseManager instance
        """
        self.db = db
        self.course_code = None
        self.assignments = {}
    
    def set_course(self, course_code: str):
        """
        Set the current course and load its assignments
        
        Args:
            course_code: Course code to work with
        """
        self.course_code = course_code
        self._load_assignments()
    
    def _load_assignments(self):
        """Load assignments for current course from database"""
        if not self.course_code:
            self.assignments = {}
            return
        
        assignments_list = self.db.get_all_assignments(self.course_code)
        self.assignments = {a['title']: a for a in assignments_list}
    
    def create_assignment(self, title: str, weight: float, max_score: float = 100.0) -> bool:
        """
        Create a new assignment
        
        Args:
            title: Assignment title
            weight: Assignment weight (0.0 to 1.0)
            max_score: Maximum possible score
            
        Returns:
            bool: True if successful, False if assignment already exists
        """
        if not self.course_code:
            return False
        
        if self.db.create_assignment(self.course_code, title, weight, max_score):
            self.assignments[title] = {
                "title": title,
                "weight": weight,
                "max_score": max_score,
                "course_code": self.course_code
            }
            return True
        return False
    
    def get_assignment(self, title: str) -> Optional[Dict]:
        """
        Get assignment information
        
        Args:
            title: Assignment title
            
        Returns:
            Assignment dictionary or None if not found
        """
        return self.assignments.get(title)
    
    def get_all_assignments(self) -> List[Dict]:
        """
        Get all assignments
        
        Returns:
            List of assignment dictionaries
        """
        return list(self.assignments.values())
    
    def update_assignment(self, title: str, new_title: Optional[str] = None,
                         weight: Optional[float] = None, 
                         max_score: Optional[float] = None) -> bool:
        """
        Update assignment information
        
        Args:
            title: Current assignment title
            new_title: New title (optional)
            weight: New weight (optional)
            max_score: New max score (optional)
            
        Returns:
            bool: True if successful, False if assignment not found
        """
        if not self.course_code or title not in self.assignments:
            return False
        
        # Check if new title already exists
        if new_title and new_title != title and new_title in self.assignments:
            return False
        
        if self.db.update_assignment(self.course_code, title, new_title, weight, max_score):
            # Update local cache
            assignment = self.assignments[title]
            
            if new_title and new_title != title:
                assignment["title"] = new_title
                self.assignments[new_title] = assignment
                del self.assignments[title]
            
            if weight is not None:
                assignment["weight"] = weight
            if max_score is not None:
                assignment["max_score"] = max_score
            
            return True
        return False
    
    def delete_assignment(self, title: str) -> bool:
        """
        Delete an assignment
        
        Args:
            title: Assignment title
            
        Returns:
            bool: True if successful, False if assignment not found
        """
        if not self.course_code or title not in self.assignments:
            return False
        
        if self.db.delete_assignment(self.course_code, title):
            del self.assignments[title]
            return True
        return False
    
    def get_total_weight(self) -> float:
        """
        Calculate total weight of all assignments
        
        Returns:
            Total weight as a float
        """
        return sum(assignment["weight"] for assignment in self.assignments.values())
    
    def validate_weights(self) -> bool:
        """
        Check if total weight equals 1.0 (100%)
        
        Returns:
            bool: True if weights are valid, False otherwise
        """
        total = self.get_total_weight()
        return abs(total - 1.0) < 0.01  # Allow small floating point errors