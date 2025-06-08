from flask import Blueprint, render_template, redirect, url_for, session, request
from models import db, User, Course, Student

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    return render_template('admin_dashboard.html')

@admin_bp.route('/manage_users')
def manage_users():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        if role in ['teacher', 'student']:
            if role == 'student':
                user = Student(username=username, password=password, full_name=full_name, email=email)
            else:
                user = User(username=username, password=password, role=role, full_name=full_name, email=email)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('admin.manage_users'))
    return render_template('add_user.html', roles=['teacher', 'student'])

@admin_bp.route('/manage_courses', methods=['GET', 'POST', 'DELETE'])
def manage_courses():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        teacher_id = request.form['teacher_id']
        course = Course(title=title, description=description, teacher_id=teacher_id)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('admin.manage_courses'))
    elif request.method == 'DELETE':
        course_id = request.form.get('course_id')
        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        return redirect(url_for('admin.manage_courses'))
    courses = Course.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    return render_template('manage_courses.html', courses=courses, teachers=teachers)

@admin_bp.route('/manage_students', methods=['GET', 'POST', 'DELETE'])
def manage_students():
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        student = Student(username=username, password=password, full_name=full_name, email=email)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('admin.manage_students'))
    elif request.method == 'DELETE':
        student_id = request.form.get('student_id')
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        return redirect(url_for('admin.manage_students'))
    students = Student.query.all()
    return render_template('manage_students.html', students=students)

@admin_bp.route('/assign_student_to_course/<int:course_id>', methods=['GET', 'POST'])
def assign_student_to_course(course_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    course = Course.query.get_or_404(course_id)
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        student = Student.query.get_or_404(student_id)
        if course not in student.enrolled_courses:
            student.enrolled_courses.append(course)
            db.session.commit()
        return redirect(url_for('admin.manage_courses'))
    students = Student.query.all()
    return render_template('assign_student_to_course.html', course=course, students=students)