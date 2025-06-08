from flask import Flask, render_template, redirect, url_for, session
from config import Config
from models import db
from auth.routes import auth_bp
from admin.routes import admin_bp
from teacher.routes import teacher_bp
from student.routes import student_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)

# Thêm route mặc định cho root URL
@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'teacher':
            return redirect(url_for('teacher.teacher_dashboard'))
        elif role == 'student':
            return redirect(url_for('student.student_dashboard'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)