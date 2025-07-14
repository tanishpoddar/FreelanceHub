from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    portfolio = db.relationship('Portfolio', backref='user', uselist=False, cascade='all, delete-orphan')
    analytics = db.relationship('Analytics', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_token(self, expires_sec=1800):
        """Generate a password reset token valid for 30 minutes"""
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        """Verify and decode a password reset token"""
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
        except:
            return None
        return User.query.get(data['user_id'])
    
    def __repr__(self):
        return f'<User {self.username}>'

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    bio = db.Column(db.Text)
    profile_image = db.Column(db.String(200))
    location = db.Column(db.String(100), index=True)
    website = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    github = db.Column(db.String(200))
    is_public = db.Column(db.Boolean, default=True, index=True)
    is_featured = db.Column(db.Boolean, default=False, index=True)
    is_approved = db.Column(db.Boolean, default=False, index=True)
    view_count = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # Relationships
    projects = db.relationship('Project', backref='portfolio', lazy='dynamic', cascade='all, delete-orphan')
    skills = db.relationship('Skill', backref='portfolio', lazy='dynamic', cascade='all, delete-orphan')
    testimonials = db.relationship('Testimonial', backref='portfolio', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Portfolio {self.title}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    project_url = db.Column(db.String(200))
    github_url = db.Column(db.String(200))
    technologies = db.Column(db.String(500))  # Comma-separated list
    category = db.Column(db.String(100))
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Project {self.title}>'

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(20))  # Beginner, Intermediate, Advanced, Expert
    category = db.Column(db.String(50))  # Frontend, Backend, Design, etc.
    order_index = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Skill {self.name}>'

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    client_company = db.Column(db.String(100))
    client_position = db.Column(db.String(100))
    client_image = db.Column(db.String(200))
    testimonial_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Testimonial by {self.client_name}>'

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # view, inquiry, download, etc.
    visitor_ip = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    referrer = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Analytics {self.event_type} for Portfolio {self.portfolio_id}>'

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    portfolio = db.relationship('Portfolio', backref='inquiries')
    
    def __repr__(self):
        return f'<Inquiry from {self.name}>'
