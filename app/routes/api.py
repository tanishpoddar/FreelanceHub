from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
try:
    from app.models import Portfolio, User, Project, Skill, Testimonial, Inquiry, Analytics, db
except ImportError:
    from models import Portfolio, User, Project, Skill, Testimonial, Inquiry, Analytics, db
from sqlalchemy import desc

api = Blueprint('api', __name__)

# Portfolio Management APIs
@api.route('/portfolio/publish', methods=['POST'])
@login_required
def publish_portfolio():
    """Publish portfolio for public viewing"""
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        return jsonify({'success': False, 'message': 'Portfolio not found'})
    
    portfolio.is_public = True
    portfolio.is_approved = True  # Auto-approve for now, could be moderated
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Portfolio published successfully'})

@api.route('/portfolio/unpublish', methods=['POST'])
@login_required
def unpublish_portfolio():
    """Unpublish portfolio"""
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        return jsonify({'success': False, 'message': 'Portfolio not found'})
    
    portfolio.is_public = False
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Portfolio unpublished successfully'})

# Project Management APIs
@api.route('/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """Delete a project"""
    project = Project.query.get_or_404(project_id)
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    
    if project.portfolio_id != portfolio.id:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Project deleted successfully'})

@api.route('/projects/reorder', methods=['POST'])
@login_required
def reorder_projects():
    """Reorder projects after drag and drop"""
    data = request.get_json()
    old_index = data.get('old_index')
    new_index = data.get('new_index')
    
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        return jsonify({'success': False, 'message': 'Portfolio not found'})
    
    projects = portfolio.projects.order_by('order_index').all()
    
    if old_index >= len(projects) or new_index >= len(projects):
        return jsonify({'success': False, 'message': 'Invalid index'})
    
    # Reorder projects
    moved_project = projects.pop(old_index)
    projects.insert(new_index, moved_project)
    
    # Update order indices
    for i, project in enumerate(projects):
        project.order_index = i
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Projects reordered successfully'})

# Skill Management APIs
@api.route('/skills/<int:skill_id>', methods=['DELETE'])
@login_required
def delete_skill(skill_id):
    """Delete a skill"""
    skill = Skill.query.get_or_404(skill_id)
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    
    if skill.portfolio_id != portfolio.id:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    db.session.delete(skill)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Skill deleted successfully'})

@api.route('/skills/reorder', methods=['POST'])
@login_required
def reorder_skills():
    """Reorder skills after drag and drop"""
    data = request.get_json()
    old_index = data.get('old_index')
    new_index = data.get('new_index')
    
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        return jsonify({'success': False, 'message': 'Portfolio not found'})
    
    skills = portfolio.skills.order_by('order_index').all()
    
    if old_index >= len(skills) or new_index >= len(skills):
        return jsonify({'success': False, 'message': 'Invalid index'})
    
    # Reorder skills
    moved_skill = skills.pop(old_index)
    skills.insert(new_index, moved_skill)
    
    # Update order indices
    for i, skill in enumerate(skills):
        skill.order_index = i
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Skills reordered successfully'})

# Testimonial Management APIs
@api.route('/testimonials/<int:testimonial_id>', methods=['DELETE'])
@login_required
def delete_testimonial(testimonial_id):
    """Delete a testimonial"""
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    
    if testimonial.portfolio_id != portfolio.id:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    db.session.delete(testimonial)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Testimonial deleted successfully'})

@api.route('/testimonials/reorder', methods=['POST'])
@login_required
def reorder_testimonials():
    """Reorder testimonials after drag and drop"""
    data = request.get_json()
    old_index = data.get('old_index')
    new_index = data.get('new_index')
    
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    if not portfolio:
        return jsonify({'success': False, 'message': 'Portfolio not found'})
    
    testimonials = portfolio.testimonials.order_by('order_index').all()
    
    if old_index >= len(testimonials) or new_index >= len(testimonials):
        return jsonify({'success': False, 'message': 'Invalid index'})
    
    # Reorder testimonials
    moved_testimonial = testimonials.pop(old_index)
    testimonials.insert(new_index, moved_testimonial)
    
    # Update order indices
    for i, testimonial in enumerate(testimonials):
        testimonial.order_index = i
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Testimonials reordered successfully'})

# Analytics APIs
@api.route('/analytics/portfolio/<int:portfolio_id>')
@login_required
def get_portfolio_analytics(portfolio_id):
    """Get portfolio analytics data"""
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    
    if portfolio.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get view analytics
    views = Analytics.query.filter_by(portfolio_id=portfolio_id, event_type='view').all()
    
    # Get inquiries
    inquiries = Inquiry.query.filter_by(portfolio_id=portfolio_id).all()
    
    # Calculate stats
    total_views = len(views)
    total_inquiries = len(inquiries)
    unread_inquiries = len([i for i in inquiries if not i.is_read])
    
    # Group views by date
    views_by_date = {}
    for view in views:
        date = view.timestamp.strftime('%Y-%m-%d')
        views_by_date[date] = views_by_date.get(date, 0) + 1
    
    result = {
        'total_views': total_views,
        'total_inquiries': total_inquiries,
        'unread_inquiries': unread_inquiries,
        'views_by_date': views_by_date,
        'recent_views': [{
            'timestamp': view.timestamp.isoformat(),
            'visitor_ip': view.visitor_ip,
            'user_agent': view.user_agent,
            'referrer': view.referrer
        } for view in views[-10:]],  # Last 10 views
        'recent_inquiries': [{
            'id': inquiry.id,
            'name': inquiry.name,
            'email': inquiry.email,
            'subject': inquiry.subject,
            'message': inquiry.message,
            'is_read': inquiry.is_read,
            'created_at': inquiry.created_at.isoformat()
        } for inquiry in inquiries[-10:]]  # Last 10 inquiries
    }
    
    return jsonify(result)

# Public Portfolio APIs
@api.route('/portfolios')
def get_portfolios():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    skill_filter = request.args.get('skill', '')
    location_filter = request.args.get('location', '')
    
    query = Portfolio.query.filter_by(is_public=True, is_approved=True)
    
    if skill_filter:
        query = query.join(Skill).filter(Skill.name.ilike(f'%{skill_filter}%'))
    
    if location_filter:
        query = query.filter(Portfolio.location.ilike(f'%{location_filter}%'))
    
    portfolios = query.order_by(desc(Portfolio.view_count)).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    result = {
        'portfolios': [{
            'id': p.id,
            'title': p.title,
            'bio': p.bio,
            'location': p.location,
            'view_count': p.view_count,
            'created_at': p.created_at.isoformat(),
            'skills': [skill.name for skill in p.skills.limit(5).all()],
            'user': {
                'username': p.user.username,
                'first_name': p.user.first_name,
                'last_name': p.user.last_name
            }
        } for p in portfolios.items],
        'total': portfolios.total,
        'pages': portfolios.pages,
        'current_page': portfolios.page,
        'has_next': portfolios.has_next,
        'has_prev': portfolios.has_prev
    }
    
    return jsonify(result)

@api.route('/portfolio/<int:portfolio_id>')
def get_portfolio(portfolio_id):
    portfolio = Portfolio.query.get_or_404(portfolio_id)
    
    if not portfolio.is_public or not portfolio.is_approved:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    result = {
        'id': portfolio.id,
        'title': portfolio.title,
        'bio': portfolio.bio,
        'location': portfolio.location,
        'website': portfolio.website,
        'linkedin': portfolio.linkedin,
        'github': portfolio.github,
        'profile_image': portfolio.profile_image,
        'view_count': portfolio.view_count,
        'created_at': portfolio.created_at.isoformat(),
        'user': {
            'username': portfolio.user.username,
            'first_name': portfolio.user.first_name,
            'last_name': portfolio.user.last_name
        },
        'projects': [{
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'image_url': project.image_url,
            'project_url': project.project_url,
            'github_url': project.github_url,
            'technologies': project.technologies,
            'category': project.category
        } for project in portfolio.projects.order_by('order_index').all()],
        'skills': [{
            'id': skill.id,
            'name': skill.name,
            'level': skill.level,
            'category': skill.category
        } for skill in portfolio.skills.order_by('order_index').all()],
        'testimonials': [{
            'id': testimonial.id,
            'client_name': testimonial.client_name,
            'client_company': testimonial.client_company,
            'client_position': testimonial.client_position,
            'client_image': testimonial.client_image,
            'testimonial_text': testimonial.testimonial_text,
            'rating': testimonial.rating
        } for testimonial in portfolio.testimonials.order_by('order_index').all()]
    }
    
    return jsonify(result)

@api.route('/search')
def search_portfolios():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    portfolios = Portfolio.query.filter(
        Portfolio.is_public == True,
        Portfolio.is_approved == True
    ).join(User).filter(
        db.or_(
            Portfolio.title.ilike(f'%{query}%'),
            Portfolio.bio.ilike(f'%{query}%'),
            User.first_name.ilike(f'%{query}%'),
            User.last_name.ilike(f'%{query}%')
        )
    ).all()
    
    result = {
        'portfolios': [{
            'id': p.id,
            'title': p.title,
            'bio': p.bio,
            'location': p.location,
            'view_count': p.view_count,
            'user': {
                'username': p.user.username,
                'first_name': p.user.first_name,
                'last_name': p.user.last_name
            }
        } for p in portfolios],
        'total': len(portfolios),
        'query': query
    }
    
    return jsonify(result)
