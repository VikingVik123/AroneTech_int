from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from app.databases.db import db
from app.models.users import User
import os
from dotenv import load_dotenv
load_dotenv()

login_manager = LoginManager()

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    if test_config is None:
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    else:
        # Load test config
        app.config.from_mapping(test_config)

    CORS(app, resources={r"/*": {"origins": "*"}})

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'


    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    if not user_id:
        return None
    return User.query.get(int(user_id))
