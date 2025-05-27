from app.databases.db import db
from flask_login import UserMixin, login_manager
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    """User model for storing user information."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        """Hash the password for secure storage."""
        
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check the hashed password against a provided password."""
        
        return check_password_hash(self.password, password)
    
