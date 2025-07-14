import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, current_user
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

try:
    from .models import db, User
    from .config import config
except ImportError:
    from models import db, User
    from config import config

login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV') or 'default'
    
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Configure session security
    app.config['PERMANENT_SESSION_LIFETIME'] = app.config.get('PERMANENT_SESSION_LIFETIME', 24 * 3600)  # 24 hours
    app.config['SESSION_COOKIE_SECURE'] = app.config.get('SESSION_COOKIE_SECURE', False)  # True in production
    app.config['SESSION_COOKIE_HTTPONLY'] = app.config.get('SESSION_COOKIE_HTTPONLY', True)
    app.config['SESSION_COOKIE_SAMESITE'] = app.config.get('SESSION_COOKIE_SAMESITE', 'Lax')
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/freelancehub.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('FreelanceHub startup')
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Global context processor for moment.js
    @app.context_processor
    def inject_moment():
        """Inject moment.js functions into templates."""
        def moment(date=None, format=None):
            if date is None:
                date = datetime.now()
            if format is None:
                format = 'YYYY'
            return date.strftime(format.replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d'))
        
        return dict(moment=moment)
    
    # Register blueprints
    try:
        from .routes.main import main as main_blueprint
        from .routes.auth import auth as auth_blueprint
        from .routes.portfolio import portfolio as portfolio_blueprint
        from .routes.admin import admin as admin_blueprint
        from .routes.api import api as api_blueprint
    except ImportError:
        from routes.main import main as main_blueprint
        from routes.auth import auth as auth_blueprint
        from routes.portfolio import portfolio as portfolio_blueprint
        from routes.admin import admin as admin_blueprint
        from routes.api import api as api_blueprint
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(portfolio_blueprint, url_prefix='/portfolio')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # Exempt public routes from CSRF protection
    csrf.exempt(app.view_functions['portfolio.send_inquiry'])
    
    # Add missing route handlers
    @app.route('/faqs')
    def faqs():
        """FAQ page"""
        # Redirect admin users to admin dashboard
        if current_user.is_authenticated and current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return render_template('faqs.html')
    
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        """Contact page"""
        # Redirect admin users to admin dashboard
        if current_user.is_authenticated and current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        
        if request.method == 'POST':
            try:
                # Get form data
                first_name = request.form.get('first_name')
                last_name = request.form.get('last_name')
                email = request.form.get('email')
                subject = request.form.get('subject')
                message = request.form.get('message')
                
                # Validate required fields
                if not all([first_name, last_name, email, subject, message]):
                    flash('Please fill in all required fields.', 'error')
                    return render_template('contact.html')
                
                # Send email
                msg = Message(
                    subject=f'Contact Form: {subject}',
                    recipients=[app.config['MAIL_DEFAULT_SENDER']],
                    body=f"""
New contact form submission from FreelanceHub:

Name: {first_name} {last_name}
Email: {email}
Subject: {subject}

Message:
{message}

---
This message was sent from the FreelanceHub contact form.
                    """.strip()
                )
                
                mail.send(msg)
                
                # Send confirmation email to user
                confirmation_msg = Message(
                    subject='Thank you for contacting FreelanceHub',
                    recipients=[email],
                    body=f"""
Dear {first_name},

Thank you for contacting FreelanceHub! We have received your message and will get back to you within 24-48 hours.

Your message details:
Subject: {subject}
Message: {message}

If you have any urgent questions, please don't hesitate to reach out to us directly at {app.config['MAIL_DEFAULT_SENDER']}.

Best regards,
The FreelanceHub Team
                    """.strip()
                )
                
                mail.send(confirmation_msg)
                
                flash('Thank you for your message! We will get back to you within 24-48 hours.', 'success')
                return redirect(url_for('contact'))
                
            except Exception as e:
                app.logger.error(f'Error sending contact form email: {e}')
                flash('Sorry, there was an error sending your message. Please try again later or contact us directly at ' + app.config['MAIL_DEFAULT_SENDER'], 'error')
                return render_template('contact.html')
        
        return render_template('contact.html')
    
    @app.route('/privacy')
    def privacy():
        """Privacy policy page"""
        # Redirect admin users to admin dashboard
        if current_user.is_authenticated and current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return render_template('privacy.html')
    
    @app.route('/terms')
    def terms():
        """Terms of service page"""
        # Redirect admin users to admin dashboard
        if current_user.is_authenticated and current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return render_template('terms.html')
    
    # CLI command to initialize database
    @app.cli.command()
    def init_db():
        """Initialize database."""
        db.create_all()
        print('Database initialized successfully!')
    
    # CLI command to create admin user
    @app.cli.command()
    def create_admin():
        """Create admin user."""
        admin = User.query.filter_by(email=app.config['ADMIN_EMAIL']).first()
        if not admin:
            admin = User(
                username='admin',
                email=app.config['ADMIN_EMAIL'],
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('admin123')  # Change this in production
            db.session.add(admin)
            db.session.commit()
            print('Admin user created successfully!')
        else:
            print('Admin user already exists!')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='127.0.0.1', port=5000)
