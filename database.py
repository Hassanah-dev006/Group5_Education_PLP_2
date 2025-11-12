"""
Database Manager Module
Handles all database operations for PyGrade using SQLite
"""

import sqlite3
import os
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager


class DatabaseManager:
    """Manages SQLite database operations for PyGrade"""
    
    def __init__(self, db_name: str = "pygrade.db"):
        """
        Initialize database manager
        
        Args:
            db_name: Name of the SQLite database file
        """
        self.db_name = db_name
        self.initialize_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def initialize_database(self):
        """Create all necessary tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    name TEXT NOT NULL,
                    student_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Courses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    semester TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    last_modified TEXT NOT NULL
                )
            """)
            
            # Students table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id TEXT NOT NULL,
                    course_code TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT,
                    PRIMARY KEY (id, course_code),
                    FOREIGN KEY (course_code) REFERENCES courses(code) ON DELETE CASCADE
                )
            """)
            
            # Assignments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_code TEXT NOT NULL,
                    title TEXT NOT NULL,
                    weight REAL NOT NULL,
                    max_score REAL NOT NULL,
                    UNIQUE(course_code, title),
                    FOREIGN KEY (course_code) REFERENCES courses(code) ON DELETE CASCADE
                )
            """)
            
            # Grades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    course_code TEXT NOT NULL,
                    assignment_title TEXT NOT NULL,
                    score REAL NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(student_id, course_code, assignment_title),
                    FOREIGN KEY (student_id, course_code) REFERENCES students(id, course_code) ON DELETE CASCADE,
                    FOREIGN KEY (course_code) REFERENCES courses(code) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_students_course 
                ON students(course_code)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_assignments_course 
                ON assignments(course_code)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_grades_student 
                ON grades(student_id, course_code)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_grades_assignment 
                ON grades(course_code, assignment_title)
            """)
            
            conn.commit()
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, username: str, password: str, role: str, name: str, student_id: str = None) -> bool:
        """Create a new user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, password, role, name, student_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, password, role, name, student_id))
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== COURSE OPERATIONS ====================
    
    def create_course(self, code: str, name: str, semester: str, created_date: str, last_modified: str) -> bool:
        """Create a new course"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO courses (code, name, semester, created_date, last_modified)
                    VALUES (?, ?, ?, ?, ?)
                """, (code, name, semester, created_date, last_modified))
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_course(self, code: str) -> Optional[Dict]:
        """Get course by code"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM courses WHERE code = ?", (code,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_courses(self) -> List[Dict]:
        """Get all courses"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM courses ORDER BY code")
            return [dict(row) for row in cursor.fetchall()]
    
    def update_course(self, code: str, name: str = None, semester: str = None, last_modified: str = None) -> bool:
        """Update course information"""
        updates = []
        params = []
        
        if name:
            updates.append("name = ?")
            params.append(name)
        if semester:
            updates.append("semester = ?")
            params.append(semester)
        if last_modified:
            updates.append("last_modified = ?")
            params.append(last_modified)
        
        if not updates:
            return False
        
        params.append(code)
        query = f"UPDATE courses SET {', '.join(updates)} WHERE code = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    # ==================== STUDENT OPERATIONS ====================
    
    def add_student(self, student_id: str, course_code: str, name: str, email: str = "") -> bool:
        """Add a student to a course"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO students (id, course_code, name, email)
                    VALUES (?, ?, ?, ?)
                """, (student_id, course_code, name, email))
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_student(self, student_id: str, course_code: str) -> Optional[Dict]:
        """Get student by ID and course"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM students 
                WHERE id = ? AND course_code = ?
            """, (student_id, course_code))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_students(self, course_code: str) -> List[Dict]:
        """Get all students in a course"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM students 
                WHERE course_code = ?
                ORDER BY id
            """, (course_code,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_student(self, student_id: str, course_code: str, name: str = None, email: str = None) -> bool:
        """Update student information"""
        updates = []
        params = []
        
        if name:
            updates.append("name = ?")
            params.append(name)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        
        if not updates:
            return False
        
        params.extend([student_id, course_code])
        query = f"UPDATE students SET {', '.join(updates)} WHERE id = ? AND course_code = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    def delete_student(self, student_id: str, course_code: str) -> bool:
        """Delete a student from a course"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM students 
                WHERE id = ? AND course_code = ?
            """, (student_id, course_code))
            return cursor.rowcount > 0
    
    # ==================== ASSIGNMENT OPERATIONS ====================
    
    def create_assignment(self, course_code: str, title: str, weight: float, max_score: float) -> bool:
        """Create a new assignment"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO assignments (course_code, title, weight, max_score)
                    VALUES (?, ?, ?, ?)
                """, (course_code, title, weight, max_score))
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_assignment(self, course_code: str, title: str) -> Optional[Dict]:
        """Get assignment by title and course"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM assignments 
                WHERE course_code = ? AND title = ?
            """, (course_code, title))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_assignments(self, course_code: str) -> List[Dict]:
        """Get all assignments in a course"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM assignments 
                WHERE course_code = ?
                ORDER BY id
            """, (course_code,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_assignment(self, course_code: str, old_title: str, new_title: str = None, 
                         weight: float = None, max_score: float = None) -> bool:
        """Update assignment information"""
        updates = []
        params = []
        
        if new_title:
            updates.append("title = ?")
            params.append(new_title)
        if weight is not None:
            updates.append("weight = ?")
            params.append(weight)
        if max_score is not None:
            updates.append("max_score = ?")
            params.append(max_score)
        
        if not updates:
            return False
        
        params.extend([course_code, old_title])
        query = f"UPDATE assignments SET {', '.join(updates)} WHERE course_code = ? AND title = ?"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # If title changed, update grades table
            if new_title:
                cursor.execute("""
                    UPDATE grades 
                    SET assignment_title = ? 
                    WHERE course_code = ? AND assignment_title = ?
                """, (new_title, course_code, old_title))
            
            return cursor.rowcount > 0
    
    def delete_assignment(self, course_code: str, title: str) -> bool:
        """Delete an assignment"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete associated grades first
            cursor.execute("""
                DELETE FROM grades 
                WHERE course_code = ? AND assignment_title = ?
            """, (course_code, title))
            
            # Delete assignment
            cursor.execute("""
                DELETE FROM assignments 
                WHERE course_code = ? AND title = ?
            """, (course_code, title))
            
            return cursor.rowcount > 0
    
    # ==================== GRADE OPERATIONS ====================
    
    def enter_grade(self, student_id: str, course_code: str, assignment_title: str, score: float) -> bool:
        """Enter or update a grade"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO grades (student_id, course_code, assignment_title, score)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(student_id, course_code, assignment_title) 
                    DO UPDATE SET score = ?, recorded_at = CURRENT_TIMESTAMP
                """, (student_id, course_code, assignment_title, score, score))
                return True
        except sqlite3.Error:
            return False
    
    def get_student_grades(self, student_id: str, course_code: str) -> Dict[str, float]:
        """Get all grades for a student in a course"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT assignment_title, score 
                FROM grades 
                WHERE student_id = ? AND course_code = ?
            """, (student_id, course_code))
            return {row['assignment_title']: row['score'] for row in cursor.fetchall()}
    
    def get_assignment_grades(self, course_code: str, assignment_title: str) -> Dict[str, float]:
        """Get all grades for an assignment"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT student_id, score 
                FROM grades 
                WHERE course_code = ? AND assignment_title = ?
            """, (course_code, assignment_title))
            return {row['student_id']: row['score'] for row in cursor.fetchall()}
    
    def delete_assignment_grades(self, course_code: str, assignment_title: str) -> bool:
        """Delete all grades for an assignment"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM grades 
                WHERE course_code = ? AND assignment_title = ?
            """, (course_code, assignment_title))
            return True
    
    # ==================== UTILITY OPERATIONS ====================
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            cursor.execute("SELECT COUNT(*) as count FROM users")
            stats['total_users'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM courses")
            stats['total_courses'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM students")
            stats['total_students'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM assignments")
            stats['total_assignments'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM grades")
            stats['total_grades'] = cursor.fetchone()['count']
            
            return stats