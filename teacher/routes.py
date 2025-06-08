from flask import Blueprint, render_template, redirect, url_for, session

teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@teacher_bp.route('/dashboard')
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
    return render_template('teacher_dashboard.html')