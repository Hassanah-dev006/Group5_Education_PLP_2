import hashlib
from datetime import datetime
from typing import Dict, List, Optional
import getpass

# Import custom modules
from database import DatabaseManager
from course_manager import CourseManager
from student_manager import StudentManager
from assignment_manager import AssignmentManager
from grade_manager import GradeManager
from report_generator import ReportGenerator
from utils import clear_screen, pause, validate_input


class PyGrade:
    """Main PyGrade application class"""
    
    def __init__(self):
        self.db = DatabaseManager()  # Initialize database
        self.current_user = None
        self.user_role = None
        self.course_manager = CourseManager(self.db)
        self.student_manager = StudentManager(self.db)
        self.assignment_manager = AssignmentManager(self.db)
        self.grade_manager = GradeManager(self.db)
        self.report_generator = ReportGenerator()
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the system and create default users if needed"""
        users = self.db.get_all_users()
        if not users:
            self._create_default_users()
    
    def _create_default_users(self):
        """Create default user accounts"""
        self.db.create_user(
            "admin",
            self._hash_password("admin123"),
            "lecturer",
            "System Administrator"
        )
        self.db.create_user(
            "lecturer1",
            self._hash_password("lecture123"),
            "lecturer",
            "Dr. John Smith"
        )
        self.db.create_user(
            "student1",
            self._hash_password("student123"),
            "student",
            "Alice Johnson",
            "S001"
        )
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self) -> bool:
        """Handle user login"""
        clear_screen()
        print("=" * 60)
        print(" " * 15 + "PYGRADE LOGIN SYSTEM")
        print("=" * 60)
        print("\nDefault Credentials:")
        print("  Lecturer: admin / admin123")
        print("  Student: student1 / student123")
        print("-" * 60)
        
        username = input("\nPlease enter your username: ").strip()
        password = getpass.getpass("Please enter your password: ")
        
        # Get user from database
        user = self.db.get_user(username)
        
        if user and user["password"] == self._hash_password(password):
            self.current_user = username
            self.user_role = user["role"]
            print(f"\n✓ Login successful! Welcome, {user['name']}")
            pause()
            return True
        
        print("\n❌ Invalid username or password!")
        pause()
        return False
    
    def main_menu(self):
        """Display main menu based on user role"""
        if self.user_role == "lecturer":
            self.lecturer_dashboard()
        elif self.user_role == "student":
            self.student_dashboard()
    
    def lecturer_dashboard(self):
        """Main dashboard for lecturers"""
        while True:
            clear_screen()
            print("=" * 60)
            print(" " * 15 + "LECTURER DASHBOARD")
            print("=" * 60)
            
            # Display current course info if loaded
            if self.course_manager.current_course:
                course = self.course_manager.current_course
                print(f"\n📚 Current Course: {course['name']} ({course['code']})")
                print(f"   Students: {len(self.student_manager.students)}")
                print(f"   Assignments: {len(self.assignment_manager.assignments)}")
            else:
                print("\n⚠ No course loaded")
            
            print("\n" + "-" * 60)
            print("MAIN MENU:")
            print("-" * 60)
            print("1. Course Management")
            print("2. Student Management")
            print("3. Assignment Management")
            print("4. Grade Management")
            print("5. Reports & Analytics")
            print("6. Help & Documentation")
            print("7. Logout")
            print("-" * 60)
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                self.course_management_menu()
            elif choice == "2":
                self.student_management_menu()
            elif choice == "3":
                self.assignment_management_menu()
            elif choice == "4":
                self.grade_management_menu()
            elif choice == "5":
                self.reports_menu()
            elif choice == "6":
                self.show_help()
            elif choice == "7":
                print("\n👋 Logging out...")
                pause()
                break
            else:
                print("\n❌ Invalid choice! Please try again.")
                pause()
    
    def course_management_menu(self):
        """Course management submenu"""
        while True:
            clear_screen()
            print("=" * 60)
            print(" " * 15 + "COURSE MANAGEMENT")
            print("=" * 60)
            print("\n1. Create New Course")
            print("2. Load Existing Course")
            print("3. View Course Details")
            print("4. Edit Course Information")
            print("5. Back to Main Menu")
            print("-" * 60)
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                self.create_course()
            elif choice == "2":
                self.load_course()
            elif choice == "3":
                self.view_course_details()
            elif choice == "4":
                self.edit_course()
            elif choice == "5":
                break
            else:
                print("\n❌ Invalid choice!")
                pause()
    
    def create_course(self):
        """Create a new course"""
        clear_screen()
        print("=" * 60)
        print(" " * 15 + "CREATE NEW COURSE")
        print("=" * 60)
        
        code = input("\nEnter course code (e.g., CS101): ").strip().upper()
        name = input("Enter course name: ").strip()
        semester = input("Enter semester (e.g., Fall 2025): ").strip()
        
        if self.course_manager.create_course(code, name, semester):
            print(f"\n✓ Course '{name}' created successfully!")
            self.student_manager.set_course(code)
            self.assignment_manager.set_course(code)
            self.grade_manager.set_course(code)
        else:
            print("\n❌ Failed to create course! Course code may already exist.")
        pause()
    
    def load_course(self):
        """Load an existing course"""
        clear_screen()
        print("=" * 60)
        print(" " * 15 + "LOAD EXISTING COURSE")
        print("=" * 60)
        
        courses = self.course_manager.list_courses()
        
        if not courses:
            print("\n⚠ No courses found!")
            pause()
            return
        
        print("\nAvailable Courses:")
        for i, course in enumerate(courses, 1):
            print(f"{i}. {course['code']} - {course['name']} ({course['semester']})")
        
        try:
            choice = int(input("\nSelect course number: "))
            if 1 <= choice <= len(courses):
                course_code = courses[choice - 1]['code']
                if self.course_manager.load_course(course_code):
                    self.student_manager.set_course(course_code)
                    self.assignment_manager.set_course(course_code)
                    self.grade_manager.set_course(course_code)
                    print(f"\n✓ Course loaded successfully!")
                else:
                    print("\n❌ Failed to load course!")
            else:
                print("\n❌ Invalid selection!")
        except ValueError:
            print("\n❌ Invalid input!")
        pause()
    
    def view_course_details(self):
        """View current course details"""
        clear_screen()
        if not self.course_manager.current_course:
            print("⚠ No course loaded!")
            pause()
            return
        
        course = self.course_manager.current_course
        print("=" * 60)
        print(" " * 15 + "COURSE DETAILS")
        print("=" * 60)
        print(f"\nCourse Code: {course['code']}")
        print(f"Course Name: {course['name']}")
        print(f"Semester: {course['semester']}")
        print(f"Created: {course['created_date']}")
        print(f"Students Enrolled: {len(self.student_manager.students)}")
        print(f"Assignments: {len(self.assignment_manager.assignments)}")
        pause()
    
    def edit_course(self):
        """Edit course information"""
        if not self.course_manager.current_course:
            print("⚠ No course loaded!")
            pause()
            return
        
        clear_screen()
        print("=" * 60)
        print(" " * 15 + "EDIT COURSE")
        print("=" * 60)
        
        course = self.course_manager.current_course
        print(f"\nCurrent Name: {course['name']}")
        new_name = input("Enter new name (or press Enter to keep): ").strip()
        
        print(f"Current Semester: {course['semester']}")
        new_semester = input("Enter new semester (or press Enter to keep): ").strip()
        
        if new_name:
            course['name'] = new_name
        if new_semester:
            course['semester'] = new_semester
        
        self.course_manager.save_course()
        print("\n✓ Course updated successfully!")
        pause()
    
    def student_management_menu(self):
        """Student management submenu"""
        if not self.course_manager.current_course:
            print("⚠ Please load a course first!")
            pause()
            return
        
        while True:
            clear_screen()
            print("=" * 60)
            print(" " * 15 + "STUDENT MANAGEMENT")
            print("=" * 60)
            print(f"\nCourse: {self.course_manager.current_course['name']}")
            print(f"Students Enrolled: {len(self.student_manager.students)}")
            print("\n" + "-" * 60)
            print("1. Add Student Manually")
            print("2. Import Students from CSV")
            print("3. View All Students")
            print("4. Edit Student Information")
            print("5. Remove Student")
            print("6. Back to Main Menu")
            print("-" * 60)
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                self.add_student_manual()
            elif choice == "2":
                self.import_students_csv()
            elif choice == "3":
                self.view_all_students()
            elif choice == "4":
                self.edit_student()
            elif choice == "5":
                self.remove_student()
            elif choice == "6":
                break
            else:
                print("\n❌ Invalid choice!")
                pause()
    
    def add_student_manual(self):
        """Add a student manually"""
        clear_screen()
        print("=" * 60)
        print(" " * 15 + "ADD STUDENT")
        print("=" * 60)
        
        student_id = input("\nEnter student ID: ").strip().upper()
        name = input("Enter student name: ").strip()
        email = input("Enter student email (optional): ").strip()
        
        if self.student_manager.add_student(student_id, name, email):
            print(f"\n✓ Student {name} added successfully!")
        else:
            print(f"\n❌ Student ID {student_id} already exists!")
        pause()
    
    def import_students_csv(self):
        """Import students from CSV file"""
        clear_screen()
        print("=" * 60)
        print(" " * 15 + "IMPORT STUDENTS FROM CSV")
        print("=" * 60)
        print("\nCSV Format: student_id,name,email")
        print("Example: S001,John Doe,john@example.com")
        
        filename = input("\nPlease upload the student list file (CSV format): ").strip()
        
        count = self.student_manager.import_from_csv(filename)
        if count > 0:
            print(f"\n✓ Successfully imported {count} students!")
        else:
            print("\n❌ Failed to import students! Check file format and path.")
        pause()
    
    def view_all_students(self):
        """View all enrolled students"""
        clear_screen()
        print("=" * 60)
        print(" " * 15 + "ENROLLED STUDENTS")
        print("=" * 60)
        
        students = self.student_manager.get_all_students()
        
        if not students:
            print("\n⚠ No students enrolled yet!")
        else:
            print(f"\nTotal Students: {len(students)}\n")
            print(f"{'ID':<10} {'Name':<30} {'Email':<30}")
            print("-" * 70)
            for student in students:
                print(f"{student['id']:<10} {student['name']:<30} {student.get('email', 'N/A'):<30}")
        pause()
    
    def edit_student(self):
        """Edit student information"""
        clear_screen()
        student_id = input("Enter student ID to edit: ").strip().upper()
        
        student = self.student_manager.get_student(student_id)
        if not student:
            print(f"\n❌ Student {student_id} not found!")
            pause()
            return
        
        print(f"\nCurrent Name: {student['name']}")
        new_name = input("Enter new name (or press Enter to keep): ").strip()
        
        print(f"Current Email: {student.get('email', 'N/A')}")
        new_email = input("Enter new email (or press Enter to keep): ").strip()
        
        if self.student_manager.update_student(student_id, new_name or None, new_email or None):
            print("\n✓ Student updated successfully!")
        else:
            print("\n❌ Failed to update student!")
        pause()
    
    def remove_student(self):
        """Remove a student"""
        clear_screen()
        student_id = input("Enter student ID to remove: ").strip().upper()
        
        confirm = input(f"Are you sure you want to remove {student_id}? (yes/no): ").strip().lower()
        if confirm == "yes":
            if self.student_manager.remove_student(student_id):
                print(f"\n✓ Student {student_id} removed successfully!")
            else:
                print(f"\n❌ Student {student_id} not found!")
        else:
            print("\n❌ Operation cancelled!")
        pause()
    
    def assignment_management_menu(self):
        """Assignment management submenu"""
        if not self.course_manager.current_course:
            print("⚠ Please load a course first!")
            pause()
            return
        
        while True:
            clear_screen()
            print("=" * 60)
            print(" " * 15 + "ASSIGNMENT MANAGEMENT")
            print("=" * 60)
            print(f"\nCourse: {self.course_manager.current_course['name']}")
            print(f"Total Assignments: {len(self.assignment_manager.assignments)}")
            print("\n" + "-" * 60)
            print("1. Create New Assignment")
            print("2. View All Assignments")
            print("3. Edit Assignment")
            print("4. Delete Assignment")
            print("5. Back to Main Menu")
            print("-" * 60)
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                self.create_assignment()
            elif choice == "2":
                self.view_assignments()
            elif choice == "3":
                self.edit_assignment()
            elif choice == "4":
                self.delete_assignment()
            elif choice == "5":
                break
            else:
                print("\n❌ Invalid choice!")
                pause()
    
    def create_assignment(self):
        """Create a new assignment"""
        clear_screen()
        print("=" * 60)
        print(" " * 15 + "CREATE NEW ASSIGNMENT")
        print("=" * 60)
        
        title = input("\nPlease provide the assignment title: ").strip()
        
        while True:
            try:
                weight = float(input("Enter assignment weight (e.g., 0.2 for 20%): "))
                if 0 < weight <= 1:
                    break
                print("Weight must be between 0 and 1!")
            except ValueError:
                print("Invalid input! Please enter a decimal number.")
        
        max_score = input("Enter maximum score (default 100): ").strip()
        max_score = float(max_score) if max_score else 100.0
        
        if self.assignment_manager.create_assignment(title, weight, max_score):
            print(f"\n✓ Assignment '{title}' created successfully!")
        else:
            print(f"\n❌ Assignment '{title}' already exists!")
        pause()
    
    def view_assignments(self):
        """View all assignments"""
        clear_screen()
        print("=" * 60)
        print(" " * 15 + "COURSE ASSIGNMENTS")
        print("=" * 60)
        
        assignments = self.assignment_manager.get_all_assignments()
        
        if not assignments:
            print("\n⚠ No assignments created yet!")
        else:
            print(f"\nTotal Assignments: {len(assignments)}")
            total_weight = sum(a['weight'] for a in assignments)
            print(f"Total Weight: {total_weight:.2%}\n")
            print(f"{'Title':<30} {'Weight':<10} {'Max Score':<10}")
            print("-" * 50)
            for assignment in assignments:
                print(f"{assignment['title']:<30} {assignment['weight']:<10.2%} {assignment['max_score']:<10}")
        pause()
    
    def edit_assignment(self):
        """Edit an assignment"""
        clear_screen()
        assignments = self.assignment_manager.get_all_assignments()
        
        if not assignments:
            print("⚠ No assignments available!")
            pause()
            return
        
        print("Select Assignment to Edit:")
        for i, assignment in enumerate(assignments, 1):
            print(f"{i}. {assignment['title']}")
        
        try:
            choice = int(input("\nEnter assignment number: "))
            if 1 <= choice <= len(assignments):
                title = assignments[choice - 1]['title']
                
                new_title = input(f"New title (current: {title}, press Enter to keep): ").strip()
                new_weight = input("New weight (press Enter to keep): ").strip()
                new_max = input("New max score (press Enter to keep): ").strip()
                
                weight = float(new_weight) if new_weight else None
                max_score = float(new_max) if new_max else None
                
                if self.assignment_manager.update_assignment(title, new_title or None, weight, max_score):
                    print("\n✓ Assignment updated successfully!")
                else:
                    print("\n❌ Failed to update assignment!")
            else:
                print("\n❌ Invalid selection!")
        except ValueError:
            print("\n❌ Invalid input!")
        pause()
    
    def delete_assignment(self):
        """Delete an assignment"""
        clear_screen()
        title = input("Enter assignment title to delete: ").strip()
        
        confirm = input(f"Delete '{title}' and all associated grades? (yes/no): ").strip().lower()
        if confirm == "yes":
            if self.assignment_manager.delete_assignment(title):
                # Also remove grades for this assignment
                self.grade_manager.delete_assignment_grades(title)
                print(f"\n✓ Assignment '{title}' deleted successfully!")
            else:
                print(f"\n❌ Assignment '{title}' not found!")
        else:
            print("\n❌ Operation cancelled!")
        pause()
    
    def grade_management_menu(self):
        """Grade management submenu"""
        if not self.course_manager.current_course:
            print("⚠ Please load a course first!")
            pause()
            return
        
        while True:
            clear_screen()
            print("=" * 60)
            print(" " * 15 + "GRADE MANAGEMENT")
            print("=" * 60)
            print(f"\nCourse: {self.course_manager.current_course['name']}")
            print("\n" + "-" * 60)
            print("1. Enter Grade for Student")
            print("2. Bulk Import Grades from CSV")
            print("3. View Student Grades")
            print("4. Calculate Final Grades")
            print("5. Detect Outliers")
            print("6. Back to Main Menu")
            print("-" * 60)
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                self.enter_grade()
            elif choice == "2":
                self.import_grades_csv()
            elif choice == "3":
                self.view_student_grades()
            elif choice == "4":
                self.calculate_final_grades()
            elif choice == "5":
                self.detect_outliers()
            elif choice == "6":
                break
            else:
                print("\n❌ Invalid choice!")
                pause()
    
    def enter_grade(self):
        """Enter a grade for a student"""
        clear_screen()
        print("=" * 60)
        print(" " * 15 + "ENTER GRADE")
        print("=" * 60)
        
        student_id = input("\nEnter student ID: ").strip().upper()
        if not self.student_manager.get_student(student_id):
            print(f"\n❌ Student {student_id} not found!")
            pause()
            return
        
        # Show available assignments
        assignments = self.assignment_manager.get_all_assignments()
        if not assignments:
            print("\n⚠ No assignments available!")
            pause()
            return
        
        print("\nAvailable Assignments:")
        for i, assignment in enumerate(assignments, 1):
            print(f"{i}. {assignment['title']} (Max: {assignment['max_score']})")
        
        assignment_title = input("\nEnter assignment name: ").strip()
        assignment = self.assignment_manager.get_assignment(assignment_title)
        
        if not assignment:
            print(f"\n❌ Assignment '{assignment_title}' not found!")
            pause()
            return
        
        try:
            score = float(input(f"Enter student score (0-{assignment['max_score']}): "))
            if 0 <= score <= assignment['max_score']:
                if self.grade_manager.enter_grade(student_id, assignment_title, score):
                    print(f"\n✓ Grade recorded successfully!")
                else:
                    print("\n❌ Failed to record grade!")
            else:
                print(f"\n❌ Score must be between 0 and {assignment['max_score']}!")
        except ValueError:
            print("\n❌ Invalid score!")
        pause()
    
    def import_grades_csv(self):
        """Import grades from CSV file"""
        clear_screen()
        print("=" * 60)
        print(" " * 15 + "BULK IMPORT GRADES")