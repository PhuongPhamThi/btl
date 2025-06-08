from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Định nghĩa bảng trung gian student_course
student_course = db.Table('student_course',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, student
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    # Sử dụng tên backref khác để tránh xung đột
    courses = db.relationship('Course', backref='taught_by', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Mối quan hệ với User
    teacher = db.relationship('User', foreign_keys=[teacher_id])

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    enrolled_courses = db.relationship('Course', secondary=student_course, backref='students')
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)