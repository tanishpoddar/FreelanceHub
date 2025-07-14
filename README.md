# FreelanceHub 🚀

**Your Gateway to Freelance Success**

> **License:** This project is licensed under the GNU General Public License v3.0 (GPLv3). See the [LICENSE](LICENSE) file for details.

A modern, responsive portfolio showcase platform built with Flask that helps freelancers create stunning portfolios, connect with clients, and grow their freelance business.

![FreelanceHub](https://img.shields.io/badge/FreelanceHub-Your%20Gateway%20to%20Freelance%20Success-blue?style=for-the-badge&logo=freelance)

## ✨ Features

### 🎨 **Professional Portfolio Creation**
- Drag-and-drop portfolio editor
- Customizable themes and layouts
- Professional project showcase
- Skills and testimonials management
- Real-time preview and editing

### 🔍 **Advanced Search & Discovery**
- Smart search functionality
- Category-based filtering
- Sort by popularity, date, or name
- Responsive grid layouts
- SEO-optimized portfolio pages

### 📊 **Analytics & Insights**
- Portfolio view tracking
- Visitor analytics
- Performance insights
- Engagement metrics
- Real-time statistics

### 💬 **Client Communication**
- Integrated contact forms
- Email notifications
- Inquiry management
- Professional messaging system

### 🎯 **SEO & Marketing**
- SEO-optimized pages
- Open Graph meta tags
- Twitter Card support
- Google Analytics integration
- Social media sharing

### 📱 **Responsive Design**
- Mobile-first approach
- Cross-device compatibility
- Touch-friendly interface
- Progressive Web App features

### 🔐 **Security & Authentication**
- Secure user authentication
- CSRF protection
- Password reset functionality
- Admin panel with moderation tools

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - ORM for database management
- **SQLite** - Lightweight database (production-ready alternatives supported)
- **Flask-Login** - User session management
- **Flask-WTF** - Form handling and CSRF protection
- **Flask-Mail** - Email functionality

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with custom properties
- **JavaScript (ES6+)** - Interactive functionality
- **Tailwind CSS** - Utility-first CSS framework
- **Inter Font** - Modern typography

### Features
- **Custom Scrollbar** - Beautiful gradient scrollbar
- **Animations** - Smooth transitions and micro-interactions
- **Glass Morphism** - Modern UI effects
- **Dark Mode Support** - System preference detection
- **Accessibility** - WCAG compliant design

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/freelancehub.git
   cd freelancehub
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create a .env file
   cp .env.example .env
   
   # Edit .env with your configuration
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=development
   ```

5. **Initialize the database**
   ```bash
   flask init-db
   ```

6. **Create admin user**
   ```bash
   flask create-admin
   ```

7. **Run the application**
   ```bash
   python app/app.py
   ```

8. **Access the application**
   - Open your browser and go to `http://127.0.0.1:5000`
   - Admin panel: `http://127.0.0.1:5000/admin`
   - Default admin credentials: `admin@freelancehub.com` / `admin123`

## 📁 Project Structure

```
freelance-portfolio/
├── app/
│   ├── app.py              # Flask application factory
│   ├── config.py           # Configuration settings
│   ├── models.py           # Database models
│   ├── forms.py            # Form definitions
│   ├── routes/             # Route blueprints
│   │   ├── main.py         # Main routes (home, browse)
│   │   ├── auth.py         # Authentication routes
│   │   ├── portfolio.py    # Portfolio management
│   │   ├── admin.py        # Admin panel
│   │   └── api.py          # API endpoints
│   └── services/           # Business logic
│       └── email_service.py
├── static/
│   ├── css/
│   │   ├── custom.css      # Custom styles
│   │   └── portfolio-editor.css
│   ├── js/
│   │   └── main.js         # Main JavaScript
│   └── uploads/            # File uploads
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Homepage
│   ├── auth/               # Authentication templates
│   ├── portfolio/          # Portfolio templates
│   └── admin/              # Admin templates
├── migrations/             # Database migrations
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎨 Customization

### Styling
The application uses a comprehensive CSS system with:
- CSS Custom Properties for theming
- Tailwind CSS for utility classes
- Custom animations and transitions
- Responsive design patterns

### Branding
Update the branding in `app/config.py`:
```python
SITE_NAME = 'Your Brand Name'
SITE_DESCRIPTION = 'Your site description'
SITE_KEYWORDS = 'your, keywords, here'
```

### Colors
Modify the color scheme in `static/css/custom.css`:
```css
:root {
    --primary-500: #your-color;
    --primary-600: #your-color;
    /* ... more colors */
}
```

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY` - Flask secret key
- `FLASK_ENV` - Environment (development/production)
- `DATABASE_URL` - Database connection string
- `MAIL_SERVER` - SMTP server settings
- `GOOGLE_ANALYTICS_ID` - Google Analytics tracking ID

### Database
The application supports multiple database backends:
- **SQLite** (default) - Great for development
- **PostgreSQL** - Recommended for production
- **MySQL** - Alternative production option

## 📊 Analytics

FreelanceHub includes comprehensive analytics:
- Portfolio view tracking
- User engagement metrics
- Search analytics
- Performance monitoring

## 🔒 Security Features

- CSRF protection on all forms
- Secure password hashing
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## 🌐 Deployment

### Production Deployment
1. Set `FLASK_ENV=production`
2. Use a production database (PostgreSQL recommended)
3. Configure a production WSGI server (Gunicorn)
4. Set up reverse proxy (Nginx)
5. Configure SSL certificates
6. Set up monitoring and logging

### Docker Deployment
```bash
# Build the image
docker build -t freelancehub .

# Run the container
docker run -p 5000:5000 freelancehub
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the GNU General Public License v3.0 (GPLv3) - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/tanishpoddar/freelancehub/issues)

## 🚀 Roadmap

- [ ] Advanced portfolio themes
- [ ] Client dashboard
- [ ] Payment integration
- [ ] Mobile app
- [ ] AI-powered recommendations
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] API documentation

---

**Made with ❤️ by [Tanish Poddar](https://tanish-poddar.is-a.dev/)**

*Your Gateway to Freelance Success* 