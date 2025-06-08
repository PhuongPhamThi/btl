from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Định nghĩa bảng trung gian course_student
course_student = db.Table('course_student',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'user'  # Thêm tên bảng để tránh xung đột
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, student
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    # Mối quan hệ với các khóa học được giảng dạy
    courses = db.relationship('Course', backref='teachers', lazy=True, foreign_keys='Course.teacher_id')

class Course(db.Model):
    __tablename__ = 'course'  # Thêm tên bảng để tránh xung đột
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Mối quan hệ với giáo viên
    teacher = db.relationship('User', foreign_keys=[teacher_id])
    # Mối quan hệ với học sinh qua bảng trung gian
    students = db.relationship('Student', secondary=course_student, backref=db.backref('enrolled_courses', lazy='dynamic'))

class Student(db.Model):
    __tablename__ = 'student'  # Thêm tên bảng để tránh xung đột
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)