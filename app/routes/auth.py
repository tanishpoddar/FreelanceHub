from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash
try:
    from ..app import limiter
except ImportError:
    from app import limiter
try:
    from app.models import User, db
    from app.forms import LoginForm, RegisterForm, PasswordResetRequestForm, PasswordResetForm
    from app.app import mail
except ImportError:
    from models import User, db
    from forms import LoginForm, RegisterForm, PasswordResetRequestForm, PasswordResetForm
    from app import mail

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter((User.email == form.email.data) | (User.username == form.email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        
        flash('Invalid email/username or password', 'error')
    elif form.errors:
        # Show form validation errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def register():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email
        try:
            from app.services.email_service import send_welcome_email
            send_welcome_email(user)
        except Exception as e:
            # Log error but don't break registration
            print(f"Error sending welcome email: {e}")
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/profile')
@login_required
def profile():
    """User profile page"""
    # Redirect admin users to admin dashboard
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    return render_template('auth/profile.html', user=current_user)


def send_reset_email(user):
    """Send password reset email to user"""
    token = user.get_reset_token()
    msg = Message(
        'Password Reset Request',
        sender='noreply@freelanceportfolio.com',
        recipients=[user.email]
    )
    msg.body = f'''To reset your password, visit the following link:
{url_for('auth.reset_password', token=token, _external=True)}

If you did not make this request, please ignore this email and no changes will be made.

This link will expire in 30 minutes.
'''
    mail.send(msg)


@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('Check your email for instructions to reset your password', 'info')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_password_request'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset! You can now log in', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)
