from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from models import db, User, Course, Student
from flask_bcrypt import Bcrypt

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin':
        flash('Bạn không có quyền truy cập!', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('admin_dashboard.html')

@admin_bp.route('/manage_users')
def manage_users():
    if session.get('role') != 'admin':
        flash('Bạn không có quyền truy cập!', 'danger')
        return redirect(url_for('auth.login'))
    users = User.query.all() + [s for s in Student.query.all() if s not in User.query.all()]
    return render_template('manage_users.html', users=users)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if session.get('role') != 'admin':
        flash('Bạn không có quyền thực hiện hành động này!', 'danger')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        full_name = request.form.get('full_name')
        email = request.form.get('email')

        if User.query.filter_by(username=username).first() or Student.query.filter_by(username=username).first():
            flash('Tên người dùng đã tồn tại!', 'danger')
            return render_template('add_user.html', roles=['teacher', 'student'])

        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        if role == 'student':
            user = Student(username=username, password=hashed_password, full_name=full_name, email=email)
        else:
            user = User(username=username, password=hashed_password, role=role, full_name=full_name, email=email)
        db.session.add(user)
        db.session.commit()
        flash('Thêm người dùng thành công!', 'success')
        return redirect(url_for('admin.manage_users'))
    return render_template('add_user.html', roles=['teacher', 'student'])

@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if session.get('role') != 'admin':
        flash('Bạn không có quyền thực hiện hành động này!', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(user_id) or Student.query.get(user_id)
    if not user:
        flash('Người dùng không tồn tại!', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    if request.method == 'POST':
        user.username = request.form.get('username', user.username)
        user.full_name = request.form.get('full_name', user.full_name)
        user.email = request.form.get('email', user.email)
        if request.form.get('password'):
            bcrypt = Bcrypt()
            user.password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        db.session.commit()
        flash('Cập nhật người dùng thành công!', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('edit_user.html', user=user, roles=['teacher', 'student'] if not hasattr(user, 'role') else [user.role])

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if session.get('role') != 'admin':
        flash('Bạn không có quyền thực hiện hành động này!', 'danger')
        return redirect(url_for('auth.login'))
    
    current_user_id = session.get('user_id')
    if current_user_id == user_id:
        flash('Bạn không thể xóa chính tài khoản admin đang đăng nhập!', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user = User.query.get(user_id)
    if user:
        if user.role == 'admin':
            flash('Không thể xóa tài khoản admin!', 'danger')
            return redirect(url_for('admin.manage_users'))
        if user.role == 'teacher':
            courses = Course.query.filter_by(teacher_id=user_id).all()
            if courses:
                flash('Không thể xóa giáo viên vì có khóa học liên quan. Vui lòng gán giáo viên khác hoặc xóa các khóa học trước!', 'danger')
                return redirect(url_for('admin.manage_courses'))
        db.session.delete(user)
        db.session.commit()
        flash('Xóa người dùng thành công!', 'success')
    else:
        student = Student.query.get(user_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            flash('Xóa học sinh thành công!', 'success')
        else:
            flash('Người dùng không tồn tại!', 'danger')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/manage_courses', methods=['GET', 'POST', 'DELETE'])
def manage_courses():
    if session.get('role') != 'admin':
        flash('Bạn không có quyền truy cập!', 'danger')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        teacher_id = request.form['teacher_id']
        course = Course(title=title, description=description, teacher_id=teacher_id)
        db.session.add(course)
        db.session.commit()
        flash('Thêm khóa học thành công!', 'success')
        return redirect(url_for('admin.manage_courses'))
    elif request.method == 'DELETE':
        course_id = request.form.get('course_id')
        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        flash('Xóa khóa học thành công!', 'success')
        return redirect(url_for('admin.manage_courses'))
    courses = Course.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    students = Student.query.all()  # Danh sách tất cả học sinh
    # Lấy danh sách học sinh cho mỗi khóa học
    courses_with_students = []
    for course in courses:
        course_students = course.students.all() if hasattr(course.students, 'all') else []
        courses_with_students.append({'course': course, 'students': course_students})
    return render_template('manage_courses.html', courses_with_students=courses_with_students, teachers=teachers, students=students)

@admin_bp.route('/assign_student_to_course/<int:course_id>', methods=['POST'])
def assign_student_to_course(course_id):
    if session.get('role') != 'admin':
        flash('Bạn không có quyền thực hiện hành động này!', 'danger')
        return redirect(url_for('auth.login'))
    
    course = Course.query.get_or_404(course_id)
    student_id = request.form.get('student_id')
    if not student_id:
        flash('Vui lòng chọn học sinh!', 'danger')
        return redirect(url_for('admin.manage_courses'))
    
    student = Student.query.get(student_id)
    if not student:
        flash('Học sinh không tồn tại!', 'danger')
        return redirect(url_for('admin.manage_courses'))
    
    from models import course_student
    if not db.session.query(course_student).filter_by(course_id=course_id, student_id=student_id).first():
        db.session.execute(course_student.insert().values(course_id=course_id, student_id=student_id))
        db.session.commit()
        flash('Gán học sinh vào khóa học thành công!', 'success')
    else:
        flash('Học sinh đã được gán vào khóa học này!', 'danger')
    
    return redirect(url_for('admin.manage_courses'))

@admin_bp.route('/view_course_students/<int:course_id>')
def view_course_students(course_id):
    if session.get('role') != 'admin':
        flash('Bạn không có quyền truy cập!', 'danger')
        return redirect(url_for('auth.login'))
    
    course = Course.query.get_or_404(course_id)
    # Xử lý đúng với lazy='dynamic' bằng cách gọi .all() trực tiếp
    course_students = course.students.all()  # Lấy danh sách học sinh
    return render_template('view_course_students.html', course=course, students=course_students)

@admin_bp.route('/manage_students', methods=['GET', 'POST', 'DELETE'])
def manage_students():
    if session.get('role') != 'admin':
        flash('Bạn không có quyền truy cập!', 'danger')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        if Student.query.filter_by(username=username).first():
            flash('Tên người dùng đã tồn tại!', 'danger')
            return render_template('manage_students.html')
        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        student = Student(username=username, password=hashed_password, full_name=full_name, email=email)
        db.session.add(student)
        db.session.commit()
        flash('Thêm học sinh thành công!', 'success')
        return redirect(url_for('admin.manage_students'))
    elif request.method == 'DELETE':
        student_id = request.form.get('student_id')
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        flash('Xóa học sinh thành công!', 'success')
        return redirect(url_for('admin.manage_students'))
    students = Student.query.all()
    return render_template('manage_students.html', students=students)