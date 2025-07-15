from flask import Flask, render_template
from controllers.extensions import db
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)

with app.app_context():
    from controllers.models import *
    db.create_all()

    admin_role = Admin.query.filter_by(username = 'admin').first()
    if not admin_role:
        admin_role = Admin(
            username = 'admin',
            email = 'admin@gmail.com'
        )
        admin_role.password = 'admin123'
        db.session.add(admin_role)
    db.session.commit()

# from api import *

# from routes import *


if __name__ == '__main__':
    app.run(debug=True)