from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def has_permission(self, permission):
        permissions = {
            'admin': ['view', 'add', 'edit', 'delete', 'reports', 'analytics', 'users'],
            'warehouse': ['view', 'add', 'edit'],
            'manager': ['view', 'reports', 'analytics']
        }
        return permission in permissions.get(self.role, [])