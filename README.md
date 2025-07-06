# InsightIQ - AI-Powered Business Intelligence Platform

A comprehensive SaaS Business Analyst AI Tool built with Django, designed for multi-subsidiary organizations. The platform automates data analysis, generates insights, and creates professional reports with multi-tenancy, AI/ML analytics, dashboards, reporting, user management, security, and subscription billing.

## 🌟 Features

### Core Functionality
- **Multi-Tenant Architecture**: Support for multiple organizations with data isolation
- **Data Integration**: Upload and process CSV, Excel, and other data formats
- **AI/ML Analytics**: Automated data analysis and pattern recognition
- **Interactive Dashboards**: Real-time visualizations and metrics
- **Automated Reporting**: Generate professional reports in multiple formats (PDF, Excel, CSV, HTML)
- **AI Insights**: Machine learning-powered business insights and recommendations

### Advanced Features
- **User Management**: Role-based access control and team collaboration
- **Subscription Management**: Flexible pricing plans and billing
- **Real-time Collaboration**: Comments, sharing, and team features
- **API Access**: RESTful API for integrations
- **Scheduled Reports**: Automated report generation and delivery
- **Security**: Enterprise-grade security with data encryption

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite included for development)
- Redis (for Celery tasks)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd insight_iq
   ```

2. **Run the setup script**
   ```bash
   ./run.sh
   ```

   Or manually:

3. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Setup environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start development server**
   ```bash
   python manage.py runserver
   ```

### Access the Application

- **Main Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/v1/

## 📁 Project Structure

```
insight_iq/
├── insight_iq/              # Main project settings
├── tenants/                 # Multi-tenancy support
├── core/                    # Core functionality
├── analytics/               # Data analysis and ML
├── data_sources/            # Data integration
├── dashboards/              # Interactive dashboards
├── reports/                 # Report generation
├── ai_insights/             # AI-powered insights
├── user_management/         # User and team management
├── subscriptions/           # Subscription management
├── payments/                # Payment processing
├── api/                     # REST API
├── templates/               # HTML templates
├── static/                  # Static files
├── media/                   # User uploads
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── manage.py               # Django management
```

## 🏗️ Architecture

### Multi-Tenancy
- **Shared Database**: Single database with tenant isolation
- **Subdomain Routing**: Each tenant gets a unique subdomain
- **Data Isolation**: Complete separation of tenant data
- **Custom Domains**: Support for custom domain mapping

### Technology Stack
- **Backend**: Django 4.2+ with Python 3.8+
- **Database**: PostgreSQL (recommended) or SQLite (development)
- **Cache**: Redis for session and cache storage
- **Task Queue**: Celery for background processing
- **Frontend**: Bootstrap 5 with Chart.js
- **API**: Django REST Framework
- **Security**: Django security features + custom enhancements

### AI/ML Components
- **Data Processing**: Pandas, NumPy for data manipulation
- **Machine Learning**: Scikit-learn for analytics
- **Visualization**: Matplotlib, Seaborn for charts
- **Report Generation**: ReportLab for PDFs, OpenPyXL for Excel

## 📊 Key Components

### 1. Data Sources (`data_sources/`)
- File upload and processing
- Database connections
- API integrations
- Data validation and cleaning

### 2. Analytics (`analytics/`)
- Statistical analysis
- Machine learning models
- Pattern recognition
- Trend analysis

### 3. Dashboards (`dashboards/`)
- Interactive visualizations
- Real-time data updates
- Customizable widgets
- Responsive design

### 4. Reports (`reports/`)
- Automated report generation
- Multiple output formats
- Scheduling and delivery
- Template system

### 5. AI Insights (`ai_insights/`)
- Automated insights generation
- Recommendation engine
- Anomaly detection
- Predictive analytics

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Django settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:pass@localhost/insightiq

# Cache and Sessions
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# File Storage
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket

# API Keys
OPENAI_API_KEY=your-openai-key
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

### Database Setup

#### PostgreSQL (Recommended)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb insightiq
sudo -u postgres createuser insightiq_user
sudo -u postgres psql -c "ALTER USER insightiq_user CREATEDB;"
sudo -u postgres psql -c "ALTER USER insightiq_user WITH PASSWORD 'your-password';"
```

#### Redis Setup
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

## 🚀 Deployment

### Production Settings
1. **Update environment variables**
2. **Set DEBUG=False**
3. **Configure proper database**
4. **Set up static file serving**
5. **Configure email backend**
6. **Set up Celery workers**

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment
1. **Prepare server** (Ubuntu/CentOS)
2. **Install dependencies** (Python, PostgreSQL, Redis, Nginx)
3. **Deploy code** and install requirements
4. **Configure web server** (Nginx + Gunicorn)
5. **Set up SSL** (Let's Encrypt)
6. **Configure monitoring** (optional)

## 🧪 Testing

### Run Tests
```bash
# All tests
python manage.py test

# Specific app
python manage.py test tenants

# With coverage
coverage run --source='.' manage.py test
coverage report
```

### API Testing
```bash
# Using curl
curl -X GET http://localhost:8000/api/v1/datasets/ \
  -H "Authorization: Token your-api-token"

# Using httpie
http GET localhost:8000/api/v1/datasets/ \
  Authorization:"Token your-api-token"
```

## 📡 API Documentation

### Authentication
```bash
# Get token
POST /api/v1/auth/login/
{
  "username": "your-username",
  "password": "your-password"
}
```

### Key Endpoints
- `GET /api/v1/datasets/` - List datasets
- `POST /api/v1/datasets/` - Create dataset
- `GET /api/v1/analyses/` - List analyses
- `POST /api/v1/analyses/` - Create analysis
- `GET /api/v1/dashboards/` - List dashboards
- `POST /api/v1/reports/` - Generate report

## 🔐 Security

### Built-in Security Features
- **CSRF Protection**: Django CSRF middleware
- **SQL Injection Protection**: ORM usage
- **XSS Protection**: Template auto-escaping
- **Clickjacking Protection**: X-Frame-Options
- **HTTPS Enforcement**: Security middleware
- **Password Hashing**: PBKDF2 with salt

### Additional Security
- **Rate Limiting**: API throttling
- **Input Validation**: Form and serializer validation
- **File Upload Security**: Type and size restrictions
- **Data Encryption**: Sensitive data encryption
- **Audit Logging**: User action tracking

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit changes** (`git commit -m 'Add amazing feature'`)
4. **Push to branch** (`git push origin feature/amazing-feature`)
5. **Open Pull Request**

### Development Guidelines
- **Follow PEP 8** style guide
- **Write tests** for new features
- **Update documentation** as needed
- **Use meaningful commit messages**

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- **Installation Guide**: See above
- **User Manual**: Available in `/docs`
- **API Reference**: Available at `/api/v1/docs`

### Community
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Email**: support@insightiq.com

### Commercial Support
For enterprise support, custom development, or consulting services, contact our team at enterprise@insightiq.com.

## 🗺️ Roadmap

### Version 2.0 (Planned)
- [ ] Advanced ML models
- [ ] Real-time data streaming
- [ ] Mobile application
- [ ] Advanced visualization options
- [ ] Multi-language support

### Version 1.5 (In Progress)
- [x] Multi-tenant architecture
- [x] Basic report generation
- [x] Dashboard functionality
- [ ] Advanced AI insights
- [ ] Email notifications

### Version 1.0 (Current)
- [x] Core functionality
- [x] User management
- [x] Basic analytics
- [x] File upload
- [x] Basic dashboards

## 🎯 Getting Started Guide

### For Business Users
1. **Sign up** for an account
2. **Upload your data** (CSV, Excel files)
3. **Create dashboards** to visualize your data
4. **Generate reports** to share insights
5. **Set up automated reporting** for regular updates

### For Developers
1. **Clone the repository** and set up development environment
2. **Explore the codebase** starting with the main apps
3. **Run tests** to ensure everything works
4. **Check the API documentation** for integration options
5. **Contribute** by fixing bugs or adding features

### For System Administrators
1. **Review deployment options** (Docker, manual, cloud)
2. **Configure environment variables** for your setup
3. **Set up monitoring** and logging
4. **Configure backups** for data protection
5. **Review security settings** for production use

---

**InsightIQ** - Empowering organizations with AI-driven business intelligence.

For more information, visit our [website](https://insightiq.com) or contact us at info@insightiq.com.
