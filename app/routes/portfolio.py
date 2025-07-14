from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify, abort
from flask_login import login_required, current_user
try:
    from app.models import Portfolio, User, Project, Skill, Testimonial, Inquiry, Analytics, db
except ImportError:
    from models import Portfolio, User, Project, Skill, Testimonial, Inquiry, Analytics, db
from werkzeug.utils import secure_filename
import os
import json
import mimetypes

portfolio = Blueprint('portfolio', __name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def validate_file_upload(file, max_size_mb=2):
    """Validate file upload for security and size"""
    if not file or not file.filename:
        return False, "No file selected"
    
    # Check file extension
    if not allowed_file(file.filename):
        return False, "File type not allowed"
    
    # Check file size (max_size_mb in MB)
    max_size_bytes = max_size_mb * 1024 * 1024
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    if file_size > max_size_bytes:
        return False, f"File size must be less than {max_size_mb}MB"
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file.filename)
    if mime_type and not mime_type.startswith('image/'):
        return False, "Only image files are allowed"
    
    return True, "File is valid"

# Helper decorator to block admin access
def block_admin():
    if current_user.is_authenticated and getattr(current_user, 'is_admin', False):
        return redirect(url_for('admin.dashboard'))

@portfolio.route('/editor')
@login_required
def editor():
    """Portfolio editor page with drag-and-drop functionality"""
    resp = block_admin()
    if resp: return resp
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        # Create a default portfolio if none exists
        portfolio = Portfolio(
            title=f"{current_user.first_name}'s Portfolio",
            bio="Welcome to my portfolio! I'm a passionate freelancer with expertise in various technologies.",
            user_id=current_user.id,
            is_public=False,  # Start as private
            is_approved=False  # Start as not approved
        )
        db.session.add(portfolio)
        db.session.commit()
    
    return render_template('portfolio/editor.html', portfolio=portfolio)

@portfolio.route('/update-basic-info', methods=['POST'])
@login_required
def update_basic_info():
    """Update portfolio basic information"""
    resp = block_admin()
    if resp: return resp
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        flash('Portfolio not found', 'error')
        return redirect(url_for('portfolio.editor'))
    
    portfolio.title = request.form.get('title', '')
    portfolio.bio = request.form.get('bio', '')
    portfolio.location = request.form.get('location', '')
    portfolio.website = request.form.get('website', '')
    portfolio.linkedin = request.form.get('linkedin', '')
    portfolio.github = request.form.get('github', '')
    # Only update is_public if explicitly set, don't change is_approved here
    if 'is_public' in request.form:
        portfolio.is_public = True
    # Note: is_public can be set to False via the unpublish function
    
    # Handle profile image upload
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and file.filename:
            is_valid, error_message = validate_file_upload(file, max_size_mb=2)
            if not is_valid:
                flash(f'Profile image error: {error_message}', 'error')
                return redirect(url_for('portfolio.editor'))
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            portfolio.profile_image = f'/uploads/{filename}'
    
    db.session.commit()
    flash('Portfolio updated successfully!', 'success')
    return redirect(url_for('portfolio.editor'))

@portfolio.route('/add-project', methods=['POST'])
@login_required
def add_project():
    """Add a new project to portfolio"""
    resp = block_admin()
    if resp: return resp
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        return jsonify({'success': False, 'message': 'Portfolio not found'})
    
    # Validate required fields
    if not request.form.get('title') or not request.form.get('description') or not request.form.get('technologies') or not request.form.get('category'):
        return jsonify({'success': False, 'message': 'Please fill in all required fields'})
    
    project = Project(
        portfolio_id=portfolio.id,
        title=request.form.get('title'),
        description=request.form.get('description'),
        technologies=request.form.get('technologies'),
        category=request.form.get('category'),
        project_url=request.form.get('project_url'),
        github_url=request.form.get('github_url'),
        order_index=portfolio.projects.count()
    )
    
    # Handle project image upload
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            is_valid, error_message = validate_file_upload(file, max_size_mb=2)
            if not is_valid:
                return jsonify({'success': False, 'message': f'Image error: {error_message}'})
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            project.image_url = f'/uploads/{filename}'
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Project added successfully!'})

@portfolio.route('/add-skill', methods=['POST'])
@login_required
def add_skill():
    """Add a new skill to portfolio"""
    resp = block_admin()
    if resp: return resp
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        return jsonify({'success': False, 'message': 'Portfolio not found'})
    
    # Validate required fields
    if not request.form.get('name') or not request.form.get('level') or not request.form.get('category'):
        return jsonify({'success': False, 'message': 'Please fill in all required fields'})
    
    skill = Skill(
        portfolio_id=portfolio.id,
        name=request.form.get('name'),
        level=request.form.get('level'),
        category=request.form.get('category'),
        order_index=portfolio.skills.count()
    )
    
    db.session.add(skill)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Skill added successfully!'})

@portfolio.route('/add-testimonial', methods=['POST'])
@login_required
def add_testimonial():
    """Add a new testimonial to portfolio"""
    resp = block_admin()
    if resp: return resp
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        return jsonify({'success': False, 'message': 'Portfolio not found'})
    
    # Validate required fields
    if not request.form.get('client_name') or not request.form.get('testimonial_text') or not request.form.get('rating'):
        return jsonify({'success': False, 'message': 'Please fill in all required fields'})
    
    testimonial = Testimonial(
        portfolio_id=portfolio.id,
        client_name=request.form.get('client_name'),
        client_company=request.form.get('client_company'),
        client_position=request.form.get('client_position'),
        testimonial_text=request.form.get('testimonial_text'),
        rating=int(request.form.get('rating', 5)),
        order_index=portfolio.testimonials.count()
    )
    
    # Handle client image upload
    if 'client_image' in request.files:
        file = request.files['client_image']
        if file and file.filename:
            is_valid, error_message = validate_file_upload(file, max_size_mb=2)
            if not is_valid:
                return jsonify({'success': False, 'message': f'Client image error: {error_message}'})
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            testimonial.client_image = f'/uploads/{filename}'
    
    db.session.add(testimonial)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Testimonial added successfully!'})

@portfolio.route('/send-inquiry/<int:portfolio_id>', methods=['POST'])
def send_inquiry(portfolio_id):
    """Send an inquiry to a portfolio owner"""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    
    inquiry = Inquiry(
        portfolio_id=portfolio.id,
        name=request.form.get('name'),
        email=request.form.get('email'),
        subject=request.form.get('subject'),
        message=request.form.get('message')
    )
    
    db.session.add(inquiry)
    db.session.commit()
    
    # Send email notification to portfolio owner
    try:
        from app.services.email_service import send_inquiry_notification
        send_inquiry_notification(inquiry)
    except Exception as e:
        # Log error but don't break the form submission
        print(f"Error sending inquiry notification: {e}")
    
    flash('Your message has been sent successfully!', 'success')
    return redirect(url_for('main.view_portfolio', portfolio_id=portfolio.id))

@portfolio.route('/analytics')
@login_required
def analytics():
    """Portfolio analytics dashboard"""
    resp = block_admin()
    if resp: return resp
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        flash('Portfolio not found', 'error')
        return redirect(url_for('portfolio.editor'))
    
    # Get analytics data
    views = Analytics.query.filter_by(portfolio_id=portfolio.id, event_type='view').all()
    inquiries = Inquiry.query.filter_by(portfolio_id=portfolio.id).all()
    
    # Calculate stats
    total_views = len(views)
    total_inquiries = len(inquiries)
    unread_inquiries = len([i for i in inquiries if not i.is_read])
    
    return render_template('portfolio/analytics.html', 
                         portfolio=portfolio,
                         total_views=total_views,
                         total_inquiries=total_inquiries,
                         unread_inquiries=unread_inquiries,
                         views=views,
                         inquiries=inquiries)

@portfolio.route('/inquiries')
@login_required
def my_inquiries():
    """View portfolio inquiries"""
    resp = block_admin()
    if resp: return resp
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        flash('Portfolio not found', 'error')
        return redirect(url_for('portfolio.editor'))
    
    inquiries = Inquiry.query.filter_by(portfolio_id=portfolio.id).order_by(Inquiry.created_at.desc()).all()
    return render_template('portfolio/inquiries.html', inquiries=inquiries, portfolio=portfolio)

@portfolio.route('/mark-inquiry-read/<int:inquiry_id>', methods=['POST'])
@login_required
def mark_inquiry_read(inquiry_id):
    """Mark an inquiry as read"""
    resp = block_admin()
    if resp: return resp
    inquiry = Inquiry.query.get_or_404(inquiry_id)
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    
    if inquiry.portfolio_id != portfolio.id:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    inquiry.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})

@portfolio.route('/<int:portfolio_id>/contact', methods=['GET'])
def contact(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return render_template('portfolio/contact.html', portfolio=portfolio)

# Legacy routes for backward compatibility
@portfolio.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    resp = block_admin()
    if resp: return resp
    return redirect(url_for('portfolio.editor'))

@portfolio.route('/edit/<int:portfolio_id>', methods=['GET', 'POST'])
@login_required
def edit(portfolio_id):
    resp = block_admin()
    if resp: return resp
    return redirect(url_for('portfolio.editor'))

@portfolio.route('/view/<int:portfolio_id>')
def view(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    return render_template('portfolio/view.html', portfolio=portfolio)

@portfolio.route('/delete-project/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    """Delete a project from portfolio"""
    resp = block_admin()
    if resp: return resp
    project = Project.query.get_or_404(project_id)
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    
    if not portfolio or project.portfolio_id != portfolio.id:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Project deleted successfully!'})

@portfolio.route('/delete-skill/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill(skill_id):
    """Delete a skill from portfolio"""
    resp = block_admin()
    if resp: return resp
    skill = Skill.query.get_or_404(skill_id)
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    
    if not portfolio or skill.portfolio_id != portfolio.id:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    db.session.delete(skill)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Skill deleted successfully!'})

@portfolio.route('/delete-testimonial/<int:testimonial_id>', methods=['POST'])
@login_required
def delete_testimonial(testimonial_id):
    """Delete a testimonial from portfolio"""
    resp = block_admin()
    if resp: return resp
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    
    if not portfolio or testimonial.portfolio_id != portfolio.id:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    db.session.delete(testimonial)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Testimonial deleted successfully!'})

@portfolio.route('/update-order', methods=['POST'])
@login_required
def update_order():
    """Update the order of portfolio items"""
    resp = block_admin()
    if resp: return resp
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        return jsonify({'success': False, 'message': 'Portfolio not found'})
    
    data = request.get_json()
    item_type = data.get('type')
    item_ids = data.get('item_ids', [])
    
    if item_type == 'projects':
        for index, project_id in enumerate(item_ids):
            project = Project.query.get(project_id)
            if project and project.portfolio_id == portfolio.id:
                project.order_index = index
    elif item_type == 'skills':
        for index, skill_id in enumerate(item_ids):
            skill = Skill.query.get(skill_id)
            if skill and skill.portfolio_id == portfolio.id:
                skill.order_index = index
    elif item_type == 'testimonials':
        for index, testimonial_id in enumerate(item_ids):
            testimonial = Testimonial.query.get(testimonial_id)
            if testimonial and testimonial.portfolio_id == portfolio.id:
                testimonial.order_index = index
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Order updated successfully!'})

@portfolio.route('/publish', methods=['POST'])
@login_required
def publish():
    """Publish portfolio"""
    resp = block_admin()
    if resp: return resp
    print(f"Publish route called by user: {current_user.id}")
    
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        print("Portfolio not found")
        return jsonify({'success': False, 'message': 'Portfolio not found'})
    
    print(f"Portfolio found: {portfolio.title}")
    print(f"Current is_public: {portfolio.is_public}")
    
    # Check if portfolio has minimum required content
    if not portfolio.title or not portfolio.bio:
        print("Missing title or bio")
        return jsonify({'success': False, 'message': 'Please add a title and bio to your portfolio'})
    
    if portfolio.projects.count() == 0:
        print("No projects found")
        return jsonify({'success': False, 'message': 'Please add at least one project to your portfolio'})
    
    print("All checks passed, publishing portfolio...")
    portfolio.is_public = True
    portfolio.is_approved = True  # Auto-approve when user publishes
    db.session.commit()
    
    print(f"Portfolio published successfully. New is_public: {portfolio.is_public}, is_approved: {portfolio.is_approved}")
    return jsonify({'success': True, 'message': 'Portfolio published successfully!'})

@portfolio.route('/unpublish', methods=['POST'])
@login_required
def unpublish():
    """Unpublish portfolio"""
    resp = block_admin()
    if resp: return resp
    print(f"Unpublish route called by user: {current_user.id}")
    
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        print("Portfolio not found")
        return jsonify({'success': False, 'message': 'Portfolio not found'})
    
    print(f"Portfolio found: {portfolio.title}")
    print(f"Current is_public: {portfolio.is_public}")
    
    print("Unpublishing portfolio...")
    portfolio.is_public = False
    portfolio.is_approved = False  # Unapprove when user unpublishes
    db.session.commit()
    
    print(f"Portfolio unpublished successfully. New is_public: {portfolio.is_public}, is_approved: {portfolio.is_approved}")
    return jsonify({'success': True, 'message': 'Portfolio unpublished successfully!'})

@portfolio.route('/my-portfolios')
@login_required
def my_portfolios():
    resp = block_admin()
    if resp: return resp
    portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
    return render_template('portfolio/my_portfolios.html', portfolios=portfolios)
