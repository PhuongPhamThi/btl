from flask import Blueprint, render_template, redirect, url_for, session, request
from models import db, Student, Course

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('auth.login'))
    student = Student.query.get(session['user_id'])
    return render_template('student_dashboard.html', courses=student.enrolled_courses)

@student_bp.route('/enroll_course', methods=['POST'])
def enroll_course():
    if session.get('role') != 'student':
        return redirect(url_for('auth.login'))
    student = Student.query.get(session['user_id'])
    course_id = request.form.get('course_id')
    course = Course.query.get_or_404(course_id)
    if course not in student.enrolled_courses:
        student.enrolled_courses.append(course)
        db.session.commit()
    return redirect(url_for('student.dashboard'))