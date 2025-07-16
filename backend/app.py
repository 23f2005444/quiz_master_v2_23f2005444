from flask import Flask
from flask_jwt_extended import JWTManager
from controllers.extensions import db
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    from controllers.models import Admin
    db.create_all()
    admin_role = Admin.query.filter_by(username='admin').first()
    if not admin_role:
        admin_role = Admin(username='admin', email='admin@gmail.com')
        admin_role.password = 'admin123'
        db.session.add(admin_role)
    db.session.commit()

# Importing blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(user_bp, url_prefix='/api/user')

if __name__ == '__main__':
    app.run(debug=True)