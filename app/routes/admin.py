from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from functools import wraps
try:
    from app.models import User, Portfolio, Project, Skill, Testimonial, Inquiry, Analytics, db
except ImportError:
    from models import User, Portfolio, Project, Skill, Testimonial, Inquiry, Analytics, db
from sqlalchemy import desc, func
from datetime import datetime, timedelta

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@login_required
@admin_required
def index():
    """Admin index - redirect to dashboard"""
    return redirect(url_for('admin.dashboard'))

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with comprehensive stats"""
    # Basic stats
    total_users = User.query.count()
    total_portfolios = Portfolio.query.count()
    pending_approval = Portfolio.query.filter_by(is_approved=False).count()
    new_inquiries = Inquiry.query.filter_by(is_read=False).count()
    
    # Recent activity
    recent_portfolios = Portfolio.query.order_by(desc(Portfolio.created_at)).limit(5).all()
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    
    # Analytics data
    total_views = Analytics.query.filter_by(event_type='view').count()
    
    # Views by date (last 7 days)
    views_by_date = {}
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        views_by_date[date] = Analytics.query.filter(
            Analytics.event_type == 'view',
            func.date(Analytics.timestamp) == date
        ).count()
    
    stats = {
        'total_users': total_users,
        'total_portfolios': total_portfolios,
        'pending_approval': pending_approval,
        'new_inquiries': new_inquiries,
        'total_views': total_views,
        'views_by_date': views_by_date
    }
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_portfolios=recent_portfolios,
                         recent_users=recent_users)

@admin.route('/users')
@login_required
@admin_required
def users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/users.html', users=users)

@admin.route('/user/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """View user details"""
    user = User.query.get_or_404(user_id)
    portfolio = Portfolio.query.filter_by(user_id=user.id).first()
    return render_template('admin/user_detail.html', user=user, portfolio=portfolio)

@admin.route('/toggle-user-status/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    return jsonify({'success': True, 'message': f'User {user.username} has been {status}'})

@admin.route('/portfolios')
@login_required
@admin_required
def portfolios():
    """Manage portfolios"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = Portfolio.query
    
    if status_filter == 'pending':
        query = query.filter_by(is_approved=False)
    elif status_filter == 'approved':
        query = query.filter_by(is_approved=True)
    elif status_filter == 'public':
        query = query.filter_by(is_public=True, is_approved=True)
    
    portfolios = query.order_by(desc(Portfolio.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/portfolios.html', 
                         portfolios=portfolios,
                         status_filter=status_filter)

@admin.route('/portfolio/<int:portfolio_id>')
@login_required
@admin_required
def portfolio_detail(portfolio_id):
    """View portfolio details"""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return render_template('admin/portfolio_detail.html', portfolio=portfolio)

@admin.route('/approve-portfolio/<int:portfolio_id>', methods=['POST'])
@login_required
@admin_required
def approve_portfolio(portfolio_id):
    """Approve a portfolio"""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    portfolio.is_approved = True
    db.session.commit()
    flash('Portfolio approved successfully', 'success')
    return redirect(url_for('admin.portfolios'))

@admin.route('/reject-portfolio/<int:portfolio_id>', methods=['POST'])
@login_required
@admin_required
def reject_portfolio(portfolio_id):
    """Reject a portfolio"""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    portfolio.is_approved = False
    portfolio.is_public = False
    db.session.commit()
    flash('Portfolio rejected', 'warning')
    return redirect(url_for('admin.portfolios'))

@admin.route('/feature-portfolio/<int:portfolio_id>', methods=['POST'])
@login_required
@admin_required
def feature_portfolio(portfolio_id):
    """Feature/unfeature a portfolio"""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    portfolio.is_featured = not portfolio.is_featured
    db.session.commit()
    
    status = 'featured' if portfolio.is_featured else 'unfeatured'
    flash(f'Portfolio {status} successfully', 'success')
    return redirect(url_for('admin.portfolios'))

@admin.route('/delete-portfolio/<int:portfolio_id>', methods=['POST'])
@login_required
@admin_required
def delete_portfolio(portfolio_id):
    """Delete a portfolio"""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    db.session.delete(portfolio)
    db.session.commit()
    flash('Portfolio deleted successfully', 'success')
    return redirect(url_for('admin.portfolios'))

@admin.route('/inquiries')
@login_required
@admin_required
def inquiries():
    """View all inquiries"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = Inquiry.query
    
    if status_filter == 'unread':
        query = query.filter_by(is_read=False)
    elif status_filter == 'read':
        query = query.filter_by(is_read=True)
    
    inquiries = query.order_by(desc(Inquiry.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/inquiries.html', 
                         inquiries=inquiries,
                         status_filter=status_filter)

@admin.route('/inquiry/<int:inquiry_id>')
@login_required
@admin_required
def inquiry_detail(inquiry_id):
    """View inquiry details"""
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    return render_template('admin/inquiry_detail.html', inquiry=inquiry)

@admin.route('/mark-inquiry-read/<int:inquiry_id>', methods=['POST'])
@login_required
@admin_required
def mark_inquiry_read(inquiry_id):
    """Mark inquiry as read"""
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    inquiry.is_read = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Inquiry marked as read'})

@admin.route('/delete-inquiry/<int:inquiry_id>', methods=['POST'])
@login_required
@admin_required
def delete_inquiry(inquiry_id):
    """Delete an inquiry"""
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    db.session.delete(inquiry)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Inquiry deleted successfully'})

@admin.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        return jsonify({'success': False, 'message': 'Cannot delete admin user'})
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'User deleted successfully'})

@admin.route('/inquiry/<int:inquiry_id>', methods=['GET'])
@login_required
@admin_required
def get_inquiry(inquiry_id):
    """Get inquiry details as JSON"""
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    return jsonify({
        'success': True,
        'inquiry': {
            'id': inquiry.id,
            'name': inquiry.name,
            'email': inquiry.email,
            'subject': inquiry.subject,
            'message': inquiry.message,
            'is_read': inquiry.is_read,
            'created_at': inquiry.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@admin.route('/analytics')
@login_required
@admin_required
def analytics():
    """Site analytics dashboard"""
    # Overall stats
    total_users = User.query.count()
    total_portfolios = Portfolio.query.count()
    total_views = Analytics.query.filter_by(event_type='view').count()
    total_inquiries = Inquiry.query.count()
    
    # Views by date (last 30 days)
    views_by_date = {}
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        views_by_date[date] = Analytics.query.filter(
            Analytics.event_type == 'view',
            func.date(Analytics.timestamp) == date
        ).count()
    
    # Top portfolios by views
    top_portfolios = Portfolio.query.order_by(desc(Portfolio.view_count)).limit(10).all()
    
    # Recent activity
    recent_views = Analytics.query.filter_by(event_type='view').order_by(desc(Analytics.timestamp)).limit(10).all()
    recent_inquiries = Inquiry.query.order_by(desc(Inquiry.created_at)).limit(10).all()
    
    return render_template('admin/analytics.html',
                         total_users=total_users,
                         total_portfolios=total_portfolios,
                         total_views=total_views,
                         total_inquiries=total_inquiries,
                         views_by_date=views_by_date,
                         top_portfolios=top_portfolios,
                         recent_views=recent_views,
                         recent_inquiries=recent_inquiries)

@admin.route('/settings')
@login_required
@admin_required
def settings():
    """Admin settings"""
    return render_template('admin/settings.html')
