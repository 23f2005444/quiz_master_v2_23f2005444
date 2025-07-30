from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from controllers.extensions import db, cache
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app, resources={
r"/api/*": {
    "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}
})

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Configure Flask-Caching
app.config['CACHE_TYPE'] = 'simple'  # Using simple cache instead of Redis for now
app.config['CACHE_DEFAULT_TIMEOUT'] = int(os.getenv('CACHE_TIMEOUT', 300))

# Initialize extensions
db.init_app(app)
cache.init_app(app)
jwt = JWTManager(app)

# Initialize Celery
from celery_app import celery, init_celery
init_celery(app)

# Database setup
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
from routes.quiz import quiz_bp
from routes.quiz_attempts import attempts_bp
from routes.users import users_bp
from routes.exports import exports_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
app.register_blueprint(quiz_bp, url_prefix='/api', name='quiz_api_root')
app.register_blueprint(attempts_bp, url_prefix='/api/attempts')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(exports_bp, url_prefix='/api/exports')  # New export routes

# Create a route to test cache
@app.route('/api/test-cache')
@cache.cached(timeout=60)
def test_cache():
    import time
    time.sleep(2)
    return {'message': 'Cache test successful', 'time': time.time()}

if __name__ == '__main__':
    app.run(debug=True)