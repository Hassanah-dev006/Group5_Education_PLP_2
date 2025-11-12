"""
Report Generator Module
Handles report generation and export in various formats
"""

import csv
from datetime import datetime
from typing import Dict, List, Optional


class ReportGenerator:
    """Generates reports and exports data"""
    
    def generate_class_summary(self, course, student_manager, assignment_manager, grade_manager) -> str:
        """
        Generate a comprehensive class summary report
        
        Args:
            course: Course dictionary
            student_manager: StudentManager instance
            assignment_manager: AssignmentManager instance
            grade_manager: GradeManager instance
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("CLASS SUMMARY REPORT".center(70))
        report.append("=" * 70)
        report.append("")
        report.append(f"Course: {course['name']} ({course['code']})")
        report.append(f"Semester: {course['semester']}")
        report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append("-" * 70)
        report.append("COURSE STATISTICS")
        report.append("-" * 70)
        
        students = student_manager.get_all_students()
        assignments = assignment_manager.get_all_assignments()
        
        report.append(f"Total Students: {len(students)}")
        report.append(f"Total Assignments: {len(assignments)}")
        report.append("")
        
        # Assignment overview
        if assignments:
            report.append("-" * 70)
            report.append("ASSIGNMENTS")
            report.append("-" * 70)
            report.append(f"{'Title':<40} {'Weight':<10} {'Max Score':<10}")
            report.append("-" * 70)
            
            for assignment in assignments:
                report.append(f"{assignment['title']:<40} "
                            f"{assignment['weight']:<10.2%} "
                            f"{assignment['max_score']:<10}")
            
            total_weight = sum(a['weight'] for a in assignments)
            report.append("-" * 70)
            report.append(f"Total Weight: {total_weight:.2%}")
            report.append("")
        
        # Grade distribution
        final_grades = grade_manager.calculate_final_grades(student_manager, assignment_manager)
        
        if final_grades:
            report.append("-" * 70)
            report.append("FINAL GRADES")
            report.append("-" * 70)
            report.append(f"{'Student ID':<15} {'Name':<30} {'Total':<10} {'Grade':<10}")
            report.append("-" * 70)
            
            for result in final_grades:
                report.append(f"{result['student_id']:<15} "
                            f"{result['name']:<30} "
                            f"{result['weighted_total']:<10.2f} "
                            f"{result['letter_grade']:<10}")
            
            report.append("")
            
            # Grade distribution
            grade_counts = {}
            for result in final_grades:
                grade = result['letter_grade']
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
            
            report.append("-" * 70)
            report.append("GRADE DISTRIBUTION")
            report.append("-" * 70)
            for grade in ['A', 'B', 'C', 'D', 'F']:
                count = grade_counts.get(grade, 0)
                percentage = (count / len(final_grades) * 100) if final_grades else 0
                report.append(f"{grade}: {count} students ({percentage:.1f}%)")
            
            # Class statistics
            if final_grades:
                scores = [r['weighted_total'] for r in final_grades]
                avg_score = sum(scores) / len(scores)
                report.append("")
                report.append(f"Class Average: {avg_score:.2f}")
                report.append(f"Highest Score: {max(scores):.2f}")
                report.append(f"Lowest Score: {min(scores):.2f}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def generate_individual_report(self, student_id: str, student_manager, 
                                   assignment_manager, grade_manager) -> str:
        """
        Generate an individual student report
        
        Args:
            student_id: Student identifier
            student_manager: StudentManager instance
            assignment_manager: AssignmentManager instance
            grade_manager: GradeManager instance
            
        Returns:
            Formatted report string
        """
        student = student_manager.get_student(student_id)
        if not student:
            return "Student not found!"
        
        report = []
        report.append("=" * 70)
        report.append("INDIVIDUAL STUDENT REPORT".center(70))
        report.append("=" * 70)
        report.append("")
        report.append(f"Student ID: {student['id']}")
        report.append(f"Name: {student['name']}")
        report.append(f"Email: {student.get('email', 'N/A')}")
        report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Assignment grades
        student_grades = grade_manager.get_student_grades(student_id)
        assignments = assignment_manager.get_all_assignments()
        
        if student_grades:
            report.append("-" * 70)
            report.append("ASSIGNMENT GRADES")
            report.append("-" * 70)
            report.append(f"{'Assignment':<40} {'Score':<10} {'Max':<10} {'Percentage':<10}")
            report.append("-" * 70)
            
            for assignment in assignments:
                title = assignment['title']
                if title in student_grades:
                    score = student_grades[title]
                    max_score = assignment['max_score']
                    percentage = (score / max_score) * 100
                    report.append(f"{title:<40} {score:<10.2f} {max_score:<10} {percentage:<10.2f}%")
                else:
                    report.append(f"{title:<40} {'MISSING':<10} {assignment['max_score']:<10} {'N/A':<10}")
            
            report.append("")
            
            # Final grade
            final = grade_manager.calculate_student_final(student_id, assignment_manager)
            if final:
                report.append("-" * 70)
                report.append("FINAL GRADE")
                report.append("-" * 70)
                report.append(f"Weighted Total: {final['weighted_total']:.2f}")
                report.append(f"Letter Grade: {final['letter_grade']}")
                report.append("")
                
                # Performance feedback
                score = final['weighted_total']
                if score >= 90:
                    feedback = "Excellent work! Keep up the outstanding performance."
                elif score >= 80:
                    feedback = "Good job! You're performing well in this course."
                elif score >= 70:
                    feedback = "Satisfactory performance. Consider reviewing challenging areas."
                elif score >= 60:
                    feedback = "You're passing, but there's room for improvement. Seek help if needed."
                else:
                    feedback = "Your performance needs improvement. Please seek academic support."
                
                report.append("-" * 70)
                report.append("FEEDBACK")
                report.append("-" * 70)
                report.append(feedback)
        else:
            report.append("\nNo grades recorded yet.")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def export_to_csv(self, filename: str, student_manager, assignment_manager, grade_manager) -> bool:
        """
        Export all grades to CSV file
        
        Args:
            filename: Output filename
            student_manager: StudentManager instance
            assignment_manager: AssignmentManager instance
            grade_manager: GradeManager instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            students = student_manager.get_all_students()
            assignments = assignment_manager.get_all_assignments()
            
            if not students or not assignments:
                return False
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                # Create header
                fieldnames = ['Student ID', 'Name', 'Email']
                for assignment in assignments:
                    fieldnames.append(assignment['title'])
                fieldnames.extend(['Weighted Total', 'Letter Grade'])
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write student data
                for student in students:
                    student_id = student['id']
                    row = {
                        'Student ID': student_id,
                        'Name': student['name'],
                        'Email': student.get('email', '')
                    }
                    
                    # Add assignment grades
                    student_grades = grade_manager.get_student_grades(student_id)
                    for assignment in assignments:
                        title = assignment['title']
                        row[title] = student_grades.get(title, 'N/A')
                    
                    # Add final grade
                    final = grade_manager.calculate_student_final(student_id, assignment_manager)
                    if final:
                        row['Weighted Total'] = f"{final['weighted_total']:.2f}"
                        row['Letter Grade'] = final['letter_grade']
                    else:
                        row['Weighted Total'] = 'N/A'
                        row['Letter Grade'] = 'N/A'
                    
                    writer.writerow(row)
            
            return True
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return False
    
    def export_class_to_pdf(self, filename: str, course, student_manager, 
                           assignment_manager, grade_manager) -> bool:
        """
        Export class summary to PDF
        
        Args:
            filename: Output PDF filename
            course: Course dictionary
            student_manager: StudentManager instance
            assignment_manager: AssignmentManager instance
            grade_manager: GradeManager instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=1
            )
            
            elements.append(Paragraph("CLASS SUMMARY REPORT", title_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Course info
            course_info = f"""
            <b>Course:</b> {course['name']} ({course['code']})<br/>
            <b>Semester:</b> {course['semester']}<br/>
            <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            elements.append(Paragraph(course_info, styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            # Assignments table
            assignments = assignment_manager.get_all_assignments()
            if assignments:
                elements.append(Paragraph("<b>Assignments</b>", styles['Heading2']))
                
                assign_data = [['Assignment', 'Weight', 'Max Score']]
                for assignment in assignments:
                    assign_data.append([
                        assignment['title'],
                        f"{assignment['weight']:.1%}",
                        str(assignment['max_score'])
                    ])
                
                assign_table = Table(assign_data, colWidths=[4*inch, 1*inch, 1*inch])
                assign_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(assign_table)
                elements.append(Spacer(1, 0.3*inch))
            
            # Final grades table
            final_grades = grade_manager.calculate_final_grades(student_manager, assignment_manager)
            if final_grades:
                elements.append(Paragraph("<b>Final Grades</b>", styles['Heading2']))
                
                grade_data = [['Student ID', 'Name', 'Total', 'Grade']]
                for result in final_grades:
                    grade_data.append([
                        result['student_id'],
                        result['name'][:25],
                        f"{result['weighted_total']:.2f}",
                        result['letter_grade']
                    ])
                
                grade_table = Table(grade_data, colWidths=[1.2*inch, 3*inch, 1*inch, 0.8*inch])
                grade_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(grade_table)
                elements.append(Spacer(1, 0.3*inch))
                
                # Grade distribution
                grade_counts = {}
                for result in final_grades:
                    grade = result['letter_grade']
                    grade_counts[grade] = grade_counts.get(grade, 0) + 1
                
                elements.append(Paragraph("<b>Grade Distribution</b>", styles['Heading2']))
                dist_data = [['Grade', 'Count', 'Percentage']]
                for grade in ['A', 'B', 'C', 'D', 'F']:
                    count = grade_counts.get(grade, 0)
                    percentage = (count / len(final_grades) * 100) if final_grades else 0
                    dist_data.append([grade, str(count), f"{percentage:.1f}%"])
                
                dist_table = Table(dist_data, colWidths=[1*inch, 1*inch, 1.5*inch])
                dist_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(dist_table)
            
            doc.build(elements)
            return True
            
        except ImportError:
            print("\n⚠ ReportLab library not installed!")
            print("Install it with: pip3 install reportlab")
            return False
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
    
    def export_individual_to_pdf(self, filename: str, student_id: str,
                                student_manager, assignment_manager, grade_manager) -> bool:
        """
        Export individual student report to PDF
        
        Args:
            filename: Output PDF filename
            student_id: Student identifier
            student_manager: StudentManager instance
            assignment_manager: AssignmentManager instance
            grade_manager: GradeManager instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            student = student_manager.get_student(student_id)
            if not student:
                return False
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=1
            )
            
            elements.append(Paragraph("INDIVIDUAL STUDENT REPORT", title_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Student info
            student_info = f"""
            <b>Student ID:</b> {student['id']}<br/>
            <b>Name:</b> {student['name']}<br/>
            <b>Email:</b> {student.get('email', 'N/A')}<br/>
            <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            elements.append(Paragraph(student_info, styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            # Grades table
            student_grades = grade_manager.get_student_grades(student_id)
            assignments = assignment_manager.get_all_assignments()
            
            if student_grades:
                elements.append(Paragraph("<b>Assignment Grades</b>", styles['Heading2']))
                
                grade_data = [['Assignment', 'Score', 'Max', 'Percentage']]
                for assignment in assignments:
                    title = assignment['title']
                    if title in student_grades:
                        score = student_grades[title]
                        max_score = assignment['max_score']
                        percentage = (score / max_score) * 100
                        grade_data.append([
                            title[:30],
                            f"{score:.2f}",
                            str(max_score),
                            f"{percentage:.2f}%"
                        ])
                    else:
                        grade_data.append([title[:30], 'MISSING', str(assignment['max_score']), 'N/A'])
                
                grade_table = Table(grade_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
                grade_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(grade_table)
                elements.append(Spacer(1, 0.3*inch))
                
                # Final grade
                final = grade_manager.calculate_student_final(student_id, assignment_manager)
                if final:
                    final_info = f"""
                    <b>Weighted Total:</b> {final['weighted_total']:.2f}<br/>
                    <b>Letter Grade:</b> {final['letter_grade']}
                    """
                    elements.append(Paragraph("<b>Final Grade</b>", styles['Heading2']))
                    elements.append(Paragraph(final_info, styles['Normal']))
            
            doc.build(elements)
            return True
            
        except ImportError:
            print("\n⚠ ReportLab library not installed!")
            print("Install it with: pip3 install reportlab")
            return False
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
    
    def calculate_statistics(self, student_manager, assignment_manager, grade_manager) -> Dict:
        """
        Calculate course statistics
        
        Args:
            student_manager: StudentManager instance
            assignment_manager: AssignmentManager instance
            grade_manager: GradeManager instance
            
        Returns:
            Dictionary with statistics
        """
        final_grades = grade_manager.calculate_final_grades(student_manager, assignment_manager)
        
        stats = {
            "total_students": len(student_manager.get_all_students()),
            "total_assignments": len(assignment_manager.get_all_assignments()),
            "average_grade": 0.0,
            "highest_grade": 0.0,
            "lowest_grade": 0.0,
            "grade_distribution": {}
        }
        
        if final_grades:
            scores = [r['weighted_total'] for r in final_grades]
            stats["average_grade"] = sum(scores) / len(scores)
            stats["highest_grade"] = max(scores)
            stats["lowest_grade"] = min(scores)
            
            # Grade distribution
            for result in final_grades:
                grade = result['letter_grade']
                stats["grade_distribution"][grade] = stats["grade_distribution"].get(grade, 0) + 1
        
        return stats