from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User, Student
from flask_bcrypt import Bcrypt
import re

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

# Hàm kiểm tra định dạng email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        full_name = request.form.get('full_name')
        email = request.form.get('email')

        # Kiểm tra username đã tồn tại
        if User.query.filter_by(username=username).first() or Student.query.filter_by(username=username).first():
            flash('Tên người dùng đã tồn tại!', 'danger')
            return render_template('register.html')

        # Kiểm tra định dạng email
        if email and not is_valid_email(email):
            flash('Email không hợp lệ!', 'danger')
            return render_template('register.html')

        # Kiểm tra vai trò admin
        if role == 'admin' and session.get('role') != 'admin':
            flash('Chỉ admin mới có thể tạo tài khoản admin!', 'danger')
            return render_template('register.html')

        # Mã hóa mật khẩu
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Tạo user hoặc student
        if role == 'student':
            user = Student(username=username, password=hashed_password, full_name=full_name, email=email)
        else:
            user = User(username=username, password=hashed_password, role=role, full_name=full_name, email=email)
        
        db.session.add(user)
        db.session.commit()
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', roles=['teacher', 'student'] if session.get('role') != 'admin' else ['admin', 'teacher', 'student'])

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        student = None if user else Student.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Đăng nhập thành công!', 'success')
            # Điều hướng đến dashboard tương ứng
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher.teacher_dashboard'))
        elif student and bcrypt.check_password_hash(student.password, password):
            session['user_id'] = student.id
            session['role'] = 'student'
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('student.student_dashboard'))
        else:
            flash('Tên người dùng hoặc mật khẩu không đúng!', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Đăng xuất thành công!', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('user_id'):
        flash('Vui lòng đăng nhập!', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id']) or Student.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        email = request.form.get('email')
        if email and not is_valid_email(email):
            flash('Email không hợp lệ!', 'danger')
            return render_template('profile.html', user=user)
        user.email = email
        db.session.commit()
        flash('Cập nhật thông tin thành công!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('profile.html', user=user)