from flask import Flask, redirect, url_for
from flask_bcrypt import Bcrypt
from config import Config
from models import db
from auth.routes import auth_bp
from admin.routes import admin_bp
from teacher.routes import teacher_bp
from student.routes import student_bp

app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)

db.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)

# Thêm route mặc định
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)