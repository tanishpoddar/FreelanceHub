from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, make_response
from flask_login import current_user
from sqlalchemy import desc, func
from datetime import datetime, timedelta
try:
    from ..models import db, Portfolio, User, Project, Skill, Testimonial, Analytics
except ImportError:
    from models import db, Portfolio, User, Project, Skill, Testimonial, Analytics

main = Blueprint('main', __name__)

@main.route('/sitemap.xml')
def sitemap():
    """Generate sitemap.xml for SEO"""
    try:
        # Get all public portfolios
        portfolios = Portfolio.query.filter_by(is_public=True, is_approved=True).all()
        
        # Create sitemap XML
        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        
        # Add static pages
        static_pages = [
            ('/', '1.0', 'daily'),
            ('/browse', '0.8', 'daily'),
            ('/faqs', '0.6', 'weekly'),
            ('/contact', '0.5', 'monthly'),
            ('/privacy', '0.3', 'monthly'),
            ('/terms', '0.3', 'monthly'),
        ]
        
        for page, priority, changefreq in static_pages:
            sitemap_xml += f'  <url>\n'
            sitemap_xml += f'    <loc>{current_app.config["SITE_URL"]}{page}</loc>\n'
            sitemap_xml += f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>\n'
            sitemap_xml += f'    <changefreq>{changefreq}</changefreq>\n'
            sitemap_xml += f'    <priority>{priority}</priority>\n'
            sitemap_xml += f'  </url>\n'
        
        # Add portfolio pages
        for portfolio in portfolios:
            sitemap_xml += f'  <url>\n'
            sitemap_xml += f'    <loc>{current_app.config["SITE_URL"]}/portfolio/{portfolio.id}</loc>\n'
            sitemap_xml += f'    <lastmod>{portfolio.updated_at.strftime("%Y-%m-%d")}</lastmod>\n'
            sitemap_xml += f'    <changefreq>weekly</changefreq>\n'
            sitemap_xml += f'    <priority>0.7</priority>\n'
            sitemap_xml += f'  </url>\n'
        
        sitemap_xml += '</urlset>'
        
        response = make_response(sitemap_xml)
        response.headers['Content-Type'] = 'application/xml'
        return response
        
    except Exception as e:
        current_app.logger.error(f"Error generating sitemap: {e}")
        return make_response('Error generating sitemap', 500)

@main.route('/')
def index():
    """Homepage with featured and recent portfolios."""
    # Redirect admin users to admin dashboard
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    try:
        # Get featured portfolios (portfolios with most views)
        featured_portfolios = Portfolio.query.filter(
            Portfolio.is_public == True,
            Portfolio.is_approved == True
        ).order_by(
            Portfolio.view_count.desc()
        ).limit(3).all()
        
        # Get recent portfolios
        recent_portfolios = Portfolio.query.filter(
            Portfolio.is_public == True,
            Portfolio.is_approved == True
        ).order_by(
            Portfolio.updated_at.desc()
        ).limit(8).all()
        
        # Get some basic stats
        total_portfolios = Portfolio.query.filter_by(is_public=True, is_approved=True).count()
        total_users = User.query.count()
        
        return render_template('index.html', 
                             featured_portfolios=featured_portfolios,
                             recent_portfolios=recent_portfolios,
                             total_portfolios=total_portfolios,
                             total_users=total_users)
    except Exception as e:
        current_app.logger.error(f"Error in index route: {e}")
        return render_template('index.html', 
                             featured_portfolios=[],
                             recent_portfolios=[],
                             total_portfolios=0,
                             total_users=0)

@main.route('/browse')
def browse():
    """Browse all portfolios with search and filters."""
    # Block admin users from browsing portfolios
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        sort_by = request.args.get('sort', 'recent')
        
        # Base query
        query = Portfolio.query.filter(Portfolio.is_public == True, Portfolio.is_approved == True)
        
        # Apply search filter
        if search:
            query = query.filter(
                db.or_(
                    Portfolio.title.ilike(f'%{search}%'),
                    Portfolio.bio.ilike(f'%{search}%'),
                    User.first_name.ilike(f'%{search}%'),
                    User.last_name.ilike(f'%{search}%')
                )
            ).join(User)
        
        # Apply category filter
        if category:
            query = query.filter(Portfolio.category == category)
        
        # Apply sorting
        if sort_by == 'views':
            query = query.order_by(Portfolio.view_count.desc())
        elif sort_by == 'name':
            query = query.join(User).order_by(User.first_name.asc())
        else:  # recent
            query = query.order_by(Portfolio.updated_at.desc())
        
        # Paginate results
        per_page = current_app.config.get('PORTFOLIOS_PER_PAGE', 12)
        portfolios = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get categories for filter
        categories = db.session.query(Portfolio.category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        return render_template('browse.html',
                             portfolios=portfolios,
                             search=search,
                             category=category,
                             sort_by=sort_by,
                             categories=categories)
    except Exception as e:
        current_app.logger.error(f"Error in browse route: {e}")
        return render_template('browse.html',
                             portfolios=None,
                             search='',
                             category='',
                             sort_by='recent',
                             categories=[])

@main.route('/portfolio/<int:portfolio_id>')
def view_portfolio(portfolio_id):
    """View a specific portfolio."""
    # Block admin users from viewing individual portfolios
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    try:
        portfolio = Portfolio.query.get_or_404(portfolio_id)
        
        # Check if portfolio is public or user is owner
        if not portfolio.is_public and (not current_user.is_authenticated or current_user.id != portfolio.user_id):
            return render_template('errors/404.html'), 404
        
        # Increment view count
        portfolio.view_count = (portfolio.view_count or 0) + 1
        
        # Track analytics
        if current_user.is_authenticated:
            analytics = Analytics(
                user_id=current_user.id if current_user.id != portfolio.user_id else portfolio.user_id,
                portfolio_id=portfolio.id,
                event_type='view',
                visitor_ip=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.session.add(analytics)
        
        db.session.commit()
        
        return render_template('portfolio/view.html', portfolio=portfolio)
    except Exception as e:
        current_app.logger.error(f"Error in view_portfolio route: {e}")
        return render_template('errors/404.html'), 404

@main.route('/search')
def search():
    """Search portfolios and return JSON results."""
    # Block admin users from searching portfolios
    if current_user.is_authenticated and current_user.is_admin:
        return jsonify([])
    
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify([])
        
        portfolios = Portfolio.query.filter(
            Portfolio.is_public == True,
            Portfolio.is_approved == True,
            db.or_(
                Portfolio.title.ilike(f'%{query}%'),
                Portfolio.bio.ilike(f'%{query}%'),
                User.first_name.ilike(f'%{query}%'),
                User.last_name.ilike(f'%{query}%')
            )
        ).join(User).limit(10).all()
        
        results = []
        for portfolio in portfolios:
            results.append({
                'id': portfolio.id,
                'title': portfolio.title or f"{portfolio.user.first_name}'s Portfolio",
                'name': f"{portfolio.user.first_name} {portfolio.user.last_name or ''}",
                'bio': portfolio.bio[:100] + '...' if portfolio.bio and len(portfolio.bio) > 100 else portfolio.bio,
                'url': f'/portfolio/{portfolio.id}'
            })
        
        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Error in search route: {e}")
        return jsonify([])

@main.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check basic functionality
        total_users = User.query.count()
        total_portfolios = Portfolio.query.count()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'total_users': total_users,
            'total_portfolios': total_portfolios
        })
    except Exception as e:
        current_app.logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@main.route('/api/stats')
def api_stats():
    """API endpoint for site statistics."""
    # Block admin users from accessing public stats
    if current_user.is_authenticated and current_user.is_admin:
        return jsonify({})
    
    try:
        total_portfolios = Portfolio.query.filter_by(is_public=True, is_approved=True).count()
        total_users = User.query.count()
        total_projects = Project.query.count()
        total_views = db.session.query(func.sum(Portfolio.view_count)).scalar() or 0
        
        # Recent activity
        recent_portfolios = Portfolio.query.filter_by(is_public=True, is_approved=True).order_by(
            Portfolio.created_at.desc()
        ).limit(5).all()
        
        recent_activity = []
        for portfolio in recent_portfolios:
            recent_activity.append({
                'id': portfolio.id,
                'title': portfolio.title or f"{portfolio.user.first_name}'s Portfolio",
                'user': f"{portfolio.user.first_name} {portfolio.user.last_name or ''}",
                'created_at': portfolio.created_at.isoformat(),
                'url': f'/portfolio/{portfolio.id}'
            })
        
        return jsonify({
            'total_portfolios': total_portfolios,
            'total_users': total_users,
            'total_projects': total_projects,
            'total_views': total_views,
            'recent_activity': recent_activity
        })
    except Exception as e:
        current_app.logger.error(f"Error in api_stats route: {e}")
        return jsonify({
            'total_portfolios': 0,
            'total_users': 0,
            'total_projects': 0,
            'total_views': 0,
            'recent_activity': []
        })


