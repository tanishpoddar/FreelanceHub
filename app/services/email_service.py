from flask import render_template, url_for, current_app
from flask_mail import Message
from threading import Thread
import requests
from datetime import datetime

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        from app.app import mail
        mail.send(msg)

def send_email_async(subject, recipients, template, **kwargs):
    """Send email asynchronously using threading"""
    app = current_app._get_current_object()
    msg = Message(subject, recipients=recipients)
    msg.html = render_template(f'emails/{template}.html', **kwargs)
    
    Thread(target=send_async_email, args=(app, msg)).start()

def get_location_from_ip(ip_address):
    """Get location information from IP address"""
    try:
        if ip_address and ip_address != '127.0.0.1':
            response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}"
        return "Unknown Location"
    except:
        return "Unknown Location"

def get_device_info(user_agent):
    """Extract device information from user agent"""
    if not user_agent:
        return "Unknown Device"
    
    user_agent = user_agent.lower()
    
    if 'mobile' in user_agent:
        return "Mobile Device"
    elif 'tablet' in user_agent:
        return "Tablet"
    elif 'windows' in user_agent:
        return "Windows Desktop"
    elif 'mac' in user_agent:
        return "Mac Desktop"
    elif 'linux' in user_agent:
        return "Linux Desktop"
    else:
        return "Desktop"

def send_portfolio_view_notification(portfolio, analytics_record):
    """Send email notification when portfolio is viewed"""
    if not portfolio.user.email:
        return
    
    # Get location and device info
    location = get_location_from_ip(analytics_record.visitor_ip)
    device = get_device_info(analytics_record.user_agent)
    
    # Get total views
    total_views = portfolio.view_count
    
    # Prepare email data
    email_data = {
        'portfolio': portfolio,
        'view_time': analytics_record.timestamp.strftime('%Y-%m-%d %H:%M'),
        'viewer_location': location,
        'viewer_device': device,
        'total_views': total_views,
        'portfolio_url': url_for('main.view_portfolio', portfolio_id=portfolio.id, _external=True),
        'unsubscribe_url': url_for('portfolio.unsubscribe_views', _external=True)
    }
    
    # Send email
    send_email_async(
        subject=f"🎯 Your portfolio '{portfolio.title}' was viewed!",
        recipients=[portfolio.user.email],
        template='portfolio_view',
        **email_data
    )

def send_inquiry_notification(inquiry):
    """Send email notification for new inquiry"""
    portfolio = inquiry.portfolio
    if not portfolio.user.email:
        return
    
    # Prepare email data
    email_data = {
        'portfolio': portfolio,
        'inquiry': inquiry,
        'inquiry_url': url_for('portfolio.inquiries', _external=True),
        'unsubscribe_url': url_for('portfolio.unsubscribe_inquiries', _external=True)
    }
    
    # Send email
    send_email_async(
        subject=f"💼 New inquiry for your portfolio '{portfolio.title}'",
        recipients=[portfolio.user.email],
        template='inquiry_notification',
        **email_data
    )

def send_welcome_email(user):
    """Send welcome email to new users"""
    email_data = {
        'user': user,
        'portfolio_url': url_for('portfolio.editor', _external=True),
        'browse_url': url_for('main.browse', _external=True)
    }
    
    send_email_async(
        subject="Welcome to Freelance Portfolio! 🎉",
        recipients=[user.email],
        template='welcome',
        **email_data
    )

def send_portfolio_published_notification(portfolio):
    """Send notification when portfolio is published"""
    if not portfolio.user.email:
        return
    
    email_data = {
        'portfolio': portfolio,
        'portfolio_url': url_for('main.view_portfolio', portfolio_id=portfolio.id, _external=True),
        'analytics_url': url_for('portfolio.analytics', _external=True)
    }
    
    send_email_async(
        subject=f"🎉 Your portfolio '{portfolio.title}' is now live!",
        recipients=[portfolio.user.email],
        template='portfolio_published',
        **email_data
    ) 