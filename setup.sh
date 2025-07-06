#!/bin/bash

# InsightIQ Setup Script
echo "🚀 Setting up InsightIQ..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Create static directory
mkdir -p static

# Run migrations
echo "🗄️ Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Creating superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Create initial tenant
echo "🏢 Creating initial tenant..."
python manage.py shell -c "
from tenants.models import Tenant, Domain
from django.contrib.auth.models import User

# Create public tenant if it doesn't exist
if not Tenant.objects.filter(schema_name='public').exists():
    tenant = Tenant.objects.create(
        name='Public',
        schema_name='public',
        company_name='InsightIQ',
        company_description='AI-Powered Business Intelligence Platform',
        contact_email='admin@example.com',
        subscription_plan='enterprise',
        subscription_status='active',
        is_active=True,
        max_users=1000,
        max_storage_gb=1000,
        max_monthly_uploads=10000,
        ai_insights_enabled=True,
        advanced_analytics_enabled=True,
        custom_branding_enabled=True,
        api_access_enabled=True
    )
    print('Public tenant created')
else:
    tenant = Tenant.objects.get(schema_name='public')
    print('Public tenant already exists')

# Create domains for localhost access
domains = ['localhost', '127.0.0.1', '0.0.0.0']
for domain_name in domains:
    if not Domain.objects.filter(domain=domain_name).exists():
        Domain.objects.create(
            domain=domain_name,
            tenant=tenant,
            is_primary=domain_name == 'localhost'
        )
        print(f'Domain {domain_name} created')
    else:
        print(f'Domain {domain_name} already exists')
"

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Setup complete!"
echo ""
echo "🌐 You can now access the application at:"
echo "   http://localhost:8000"
echo ""
echo "🔑 Admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "🚀 To start the server, run:"
echo "   python manage.py runserver"
