#!/bin/bash

# Hostinger Deployment Script for Student Report System
# Run this script on your Hostinger shared hosting via SSH

set -e

echo "🌐 Starting Hostinger deployment for Student Report System..."

# Check if we're in the right environment
if [[ "$PWD" != *"public_html"* ]]; then
    echo "⚠️ Warning: You should run this script from your public_html directory"
    echo "Current directory: $PWD"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Clone or update repository
if [ ! -d "student-report-system" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/yourusername/student-report-system.git
else
    echo "📝 Updating repository..."
    cd student-report-system
    git pull origin main
    cd ..
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
cd student-report-system
pip install -r requirements.txt
cd ..

# Create passenger_wsgi.py for Hostinger
echo "⚙️ Creating Passenger WSGI configuration..."
cat > passenger_wsgi.py << 'EOL'
import sys
import os

# Add your project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'student-report-system'))

# Activate virtual environment
activate_this = os.path.join(os.path.dirname(__file__), 'venv/bin/activate_this.py')
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

# Import your Flask app
try:
    from student_report_system.app_simple import app as application
except ImportError:
    # Fallback import path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'student-report-system'))
    from app_simple import app as application

# Set production environment
os.environ['FLASK_ENV'] = 'production'

if __name__ == "__main__":
    application.run()
EOL

# Create .htaccess for URL rewriting
echo "🔀 Creating .htaccess configuration..."
cat > .htaccess << 'EOL'
# Passenger Configuration
PassengerEnabled On
PassengerPython venv/bin/python

# Force HTTPS (optional)
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Handle Flask static files
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^static/(.*)$ student-report-system/static/$1 [L]
EOL

# Create environment file
if [ ! -f "student-report-system/.env" ]; then
    echo "📝 Creating environment configuration..."
    cd student-report-system
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "change-this-secret-key-$(date +%s)")
    sed -i "s/your-secret-key-here-change-this-to-a-random-string/$SECRET_KEY/" .env
    cd ..
fi

# Create startup script
echo "🚀 Creating startup script..."
cat > start_app.py << 'EOL'
#!/usr/bin/env python3
import sys
import os

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'student-report-system'))

# Set environment
os.environ['FLASK_ENV'] = 'production'

# Import and run app
from student_report_system.app_simple import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
EOL

chmod +x start_app.py

# Test the application
echo "🧪 Testing application..."
cd student-report-system
python3 -c "from app_simple import app; print('✅ Application imports successfully')" || {
    echo "❌ Application import failed. Check your dependencies."
    exit 1
}
cd ..

echo "🎉 Hostinger deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. In your Hostinger control panel:"
echo "   - Go to Advanced → Python"
echo "   - Set Python version to 3.8 or higher"
echo "   - Set application root to current directory"
echo "   - Set startup file to 'passenger_wsgi.py'"
echo ""
echo "2. Configure your domain:"
echo "   - Ensure your domain points to this directory"
echo "   - Check that Python app is enabled for your domain"
echo ""
echo "3. Update environment settings:"
echo "   nano student-report-system/.env"
echo ""
echo "4. Test your application:"
echo "   Visit: https://your-domain.com"
echo ""
echo "📁 File structure created:"
echo "   passenger_wsgi.py (main entry point)"
echo "   .htaccess (URL rewriting)"
echo "   venv/ (Python virtual environment)"
echo "   student-report-system/ (your application)"
echo ""
echo "🔄 To update your application:"
echo "   cd student-report-system && git pull && cd .. && touch tmp/restart.txt"
echo ""
echo "📊 To check logs:"
echo "   Check Hostinger control panel → Error Logs"