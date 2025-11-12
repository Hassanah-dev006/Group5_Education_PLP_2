"""
Grade Manager Module
Handles grade recording, calculation, and analysis using SQLite database
"""

import csv
import statistics
from typing import Dict, List, Optional


class GradeManager:
    """Manages grade operations and calculations"""
    
    def __init__(self, db):
        """
        Initialize grade manager
        
        Args:
            db: DatabaseManager instance
        """
        self.db = db
        self.course_code = None
        self.grades = {}
    
    def set_course(self, course_code: str):
        """
        Set the current course and load its grades
        
        Args:
            course_code: Course code to work with
        """
        self.course_code = course_code
        self._load_grades()
    
    def _load_grades(self):
        """Load grades for current course from database"""
        if not self.course_code:
            self.grades = {}
            return
        
        self.grades = {}
    
    def enter_grade(self, student_id: str, assignment_title: str, score: float) -> bool:
        """
        Enter or update a grade for a student
        
        Args:
            student_id: Student identifier
            assignment_title: Assignment title
            score: Score achieved
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.course_code:
            return False
        
        if self.db.enter_grade(student_id, self.course_code, assignment_title, score):
            if student_id not in self.grades:
                self.grades[student_id] = {}
            self.grades[student_id][assignment_title] = score
            return True
        return False
    
    def get_student_grades(self, student_id: str) -> Dict[str, float]:
        """
        Get all grades for a student
        
        Args:
            student_id: Student identifier
            
        Returns:
            Dictionary of assignment titles to scores
        """
        if not self.course_code:
            return {}
        
        return self.db.get_student_grades(student_id, self.course_code)
    
    def get_assignment_grades(self, assignment_title: str) -> Dict[str, float]:
        """
        Get all grades for an assignment
        
        Args:
            assignment_title: Assignment title
            
        Returns:
            Dictionary of student IDs to scores
        """
        if not self.course_code:
            return {}
        
        return self.db.get_assignment_grades(self.course_code, assignment_title)
    
    def import_grades_csv(self, filename: str, student_manager, assignment_manager) -> int:
        """
        Import grades from CSV file
        
        Args:
            filename: Path to CSV file
            student_manager: StudentManager instance for validation
            assignment_manager: AssignmentManager instance for validation
            
        Returns:
            Number of grades imported
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
                    assignment_title = row.get('assignment_title', '').strip()
                    score_str = row.get('score', '').strip()
                    
                    # Validate student exists
                    if not student_manager.get_student(student_id):
                        continue
                    
                    # Validate assignment exists
                    assignment = assignment_manager.get_assignment(assignment_title)
                    if not assignment:
                        continue
                    
                    # Validate score
                    try:
                        score = float(score_str)
                        if 0 <= score <= assignment['max_score']:
                            if self.enter_grade(student_id, assignment_title, score):
                                count += 1
                    except ValueError:
                        continue
        except Exception as e:
            print(f"Error importing grades: {e}")
            return 0
        
        return count
    
    def calculate_student_final(self, student_id: str, assignment_manager) -> Optional[Dict]:
        """
        Calculate final grade for a student
        
        Args:
            student_id: Student identifier
            assignment_manager: AssignmentManager instance
            
        Returns:
            Dictionary with weighted_total and letter_grade, or None if no grades
        """
        student_grades = self.get_student_grades(student_id)
        
        if not student_grades:
            return None
        
        weighted_total = 0.0
        total_weight = 0.0
        
        for assignment_title, score in student_grades.items():
            assignment = assignment_manager.get_assignment(assignment_title)
            if assignment:
                # Normalize score to percentage
                percentage = (score / assignment['max_score']) * 100
                weighted_total += percentage * assignment['weight']
                total_weight += assignment['weight']
        
        # If not all assignments are graded, adjust the weighted total
        if total_weight > 0:
            final_grade = weighted_total / total_weight if total_weight < 1.0 else weighted_total
        else:
            final_grade = 0.0
        
        letter_grade = self._calculate_letter_grade(final_grade)
        
        return {
            "weighted_total": final_grade,
            "letter_grade": letter_grade
        }
    
    def _calculate_letter_grade(self, score: float) -> str:
        """
        Convert numerical score to letter grade
        
        Args:
            score: Numerical score (0-100)
            
        Returns:
            Letter grade (A, B, C, D, F)
        """
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def calculate_final_grades(self, student_manager, assignment_manager) -> List[Dict]:
        """
        Calculate final grades for all students
        
        Args:
            student_manager: StudentManager instance
            assignment_manager: AssignmentManager instance
            
        Returns:
            List of dictionaries with student info and grades
        """
        results = []
        
        for student in student_manager.get_all_students():
            student_id = student['id']
            final = self.calculate_student_final(student_id, assignment_manager)
            
            if final:
                results.append({
                    "student_id": student_id,
                    "name": student['name'],
                    "weighted_total": final['weighted_total'],
                    "letter_grade": final['letter_grade']
                })
        
        return sorted(results, key=lambda x: x['weighted_total'], reverse=True)
    
    def detect_outliers(self, student_manager, assignment_manager) -> List[Dict]:
        """
        Detect outlier scores (unusually high/low or missing)
        
        Args:
            student_manager: StudentManager instance
            assignment_manager: AssignmentManager instance
            
        Returns:
            List of outlier dictionaries
        """
        outliers = []
        
        # Check for missing grades
        all_students = student_manager.get_all_students()
        all_assignments = assignment_manager.get_all_assignments()
        
        for student in all_students:
            student_id = student['id']
            student_grades = self.get_student_grades(student_id)
            
            for assignment in all_assignments:
                assignment_title = assignment['title']
                
                # Check for missing grade
                if assignment_title not in student_grades:
                    outliers.append({
                        "student_id": student_id,
                        "student_name": student['name'],
                        "assignment": assignment_title,
                        "score": "MISSING",
                        "max_score": assignment['max_score'],
                        "reason": "Missing grade"
                    })
        
        # Check for statistical outliers in each assignment
        for assignment in all_assignments:
            assignment_title = assignment['title']
            assignment_grades = self.get_assignment_grades(assignment_title)
            
            if len(assignment_grades) < 3:
                continue
            
            scores = list(assignment_grades.values())
            mean_score = statistics.mean(scores)
            
            try:
                stdev_score = statistics.stdev(scores)
            except statistics.StatisticsError:
                continue
            
            # Flag scores more than 2 standard deviations from mean
            for student_id, score in assignment_grades.items():
                z_score = abs((score - mean_score) / stdev_score) if stdev_score > 0 else 0
                
                if z_score > 2:
                    student = student_manager.get_student(student_id)
                    if student:
                        outliers.append({
                            "student_id": student_id,
                            "student_name": student['name'],
                            "assignment": assignment_title,
                            "score": score,
                            "max_score": assignment['max_score'],
                            "reason": f"Unusual score (z-score: {z_score:.2f})"
                        })
            
            # Check for zero scores or perfect scores
            for student_id, score in assignment_grades.items():
                student = student_manager.get_student(student_id)
                if not student:
                    continue
                
                if score == 0:
                    outliers.append({
                        "student_id": student_id,
                        "student_name": student['name'],
                        "assignment": assignment_title,
                        "score": score,
                        "max_score": assignment['max_score'],
                        "reason": "Zero score - possible issue"
                    })
                elif score == assignment['max_score'] and len(assignment_grades) > 5:
                    avg_percentage = (mean_score / assignment['max_score']) * 100
                    if avg_percentage < 75:
                        outliers.append({
                            "student_id": student_id,
                            "student_name": student['name'],
                            "assignment": assignment_title,
                            "score": score,
                            "max_score": assignment['max_score'],
                            "reason": "Perfect score while class average is low"
                        })
        
        return outliers
    
    def delete_assignment_grades(self, assignment_title: str) -> bool:
        """
        Delete all grades for an assignment
        
        Args:
            assignment_title: Assignment title
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.course_code:
            return False
        
        return self.db.delete_assignment_grades(self.course_code, assignment_title)
    
    def get_assignment_statistics(self, assignment_title: str) -> Optional[Dict]:
        """
        Get statistics for an assignment
        
        Args:
            assignment_title: Assignment title
            
        Returns:
            Dictionary with statistics or None if not enough data
        """
        assignment_grades = self.get_assignment_grades(assignment_title)
        
        if not assignment_grades:
            return None
        
        scores = list(assignment_grades.values())
        
        stats = {
            "count": len(scores),
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "min": min(scores),
            "max": max(scores)
        }
        
        if len(scores) >= 2:
            stats["stdev"] = statistics.stdev(scores)
        
        return stats