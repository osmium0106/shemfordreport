#!/bin/bash

# AWS EC2 Deployment Script for Student Report System
# Run this script on your EC2 Ubuntu instance

set -e  # Exit on any error

echo "🚀 Starting AWS EC2 deployment for Student Report System..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "🛠️ Installing Docker, Git, and Nginx..."
sudo apt install -y docker.io docker-compose-v2 git nginx certbot python3-certbot-nginx curl

# Add user to docker group
sudo usermod -aG docker $USER

# Start and enable Docker
sudo systemctl enable docker
sudo systemctl start docker

# Create application directory
APP_DIR="/home/ubuntu/student-report-system"
echo "📁 Setting up application directory at $APP_DIR..."

# Clone repository (replace with your actual repository URL)
if [ ! -d "$APP_DIR" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/yourusername/student-report-system.git $APP_DIR
else
    echo "📝 Updating existing repository..."
    cd $APP_DIR
    git pull origin main
fi

cd $APP_DIR

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/your-secret-key-here-change-this-to-a-random-string/$SECRET_KEY/" .env
    
    echo "🔑 Generated random secret key. Please update .env file with your domain and other settings."
fi

# Build and start the application
echo "🏗️ Building and starting the application..."
docker-compose up -d --build

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 30

# Test if application is running
if curl -f http://localhost:5000 > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
else
    echo "❌ Application failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Configure firewall
echo "🔥 Configuring UFW firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp
sudo ufw --force enable

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update your .env file with your domain name:"
echo "   nano $APP_DIR/.env"
echo ""
echo "2. Configure your domain DNS to point to this server's IP:"
echo "   Public IP: $(curl -s ifconfig.me)"
echo ""
echo "3. Setup SSL certificate (replace 'your-domain.com' with your actual domain):"
echo "   sudo certbot --nginx -d your-domain.com -d www.your-domain.com"
echo ""
echo "4. Configure Nginx reverse proxy:"
echo "   sudo nano /etc/nginx/sites-available/student-report"
echo ""
echo "5. Test your application:"
echo "   http://$(curl -s ifconfig.me):5000"
echo ""
echo "📊 Application logs:"
echo "   docker-compose logs -f"
echo ""
echo "🔄 To update the application:"
echo "   cd $APP_DIR && git pull && docker-compose up -d --build"