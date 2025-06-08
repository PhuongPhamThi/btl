from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User, Student

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        if role == 'student':
            user = Student(username=username, password=password, full_name=full_name, email=email)
        else:
            user = User(username=username, password=password, role=role, full_name=full_name, email=email)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            user = Student.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role if hasattr(user, 'role') else 'student'
            return redirect(url_for('auth.profile'))
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('user_id'):
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id']) or Student.query.get(session['user_id'])
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.email = request.form.get('email')
        db.session.commit()
        return redirect(url_for('auth.profile'))
    return render_template('profile.html', user=user)