#!/bin/bash

# InsightIQ Development Setup and Run Script

echo "🚀 Starting InsightIQ Development Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your actual configuration"
fi

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Creating superuser...')
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Setup complete!"
echo ""
echo "🌟 InsightIQ is ready to run!"
echo ""
echo "🔗 Access URLs:"
echo "   - Main application: http://localhost:8000"
echo "   - Admin panel: http://localhost:8000/admin"
echo "   - API documentation: http://localhost:8000/api/v1/"
echo ""
echo "👤 Default admin credentials:"
echo "   - Username: admin"
echo "   - Password: admin123"
echo ""
echo "🚀 Starting development server..."
python manage.py runserver
