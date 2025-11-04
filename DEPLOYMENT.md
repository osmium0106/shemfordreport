# Student Report System - Deployment Guide

## 🚀 Deployment Options

This Flask application can be deployed on multiple platforms. Choose the option that best fits your needs:

### 1. **GitHub Repository Setup**

First, let's get your code on GitHub:

```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial commit: Student Report System"

# Create repository on GitHub.com and add remote
git remote add origin https://github.com/yourusername/student-report-system.git
git branch -M main
git push -u origin main
```

### 2. **AWS EC2 Deployment** (Recommended for scalability)

#### Prerequisites:
- AWS Account
- Domain name from GoDaddy
- Basic Linux knowledge

#### Step-by-Step Guide:

**A. Launch EC2 Instance:**
```bash
# 1. Launch Ubuntu 22.04 LTS instance (t3.micro for testing, t3.small+ for production)
# 2. Configure Security Group:
#    - SSH (22): Your IP
#    - HTTP (80): 0.0.0.0/0
#    - HTTPS (443): 0.0.0.0/0
#    - Custom TCP (5000): 0.0.0.0/0 (for testing)
```

**B. Connect and Setup Server:**
```bash
# Connect to your EC2 instance
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker ubuntu
sudo systemctl enable docker
sudo systemctl start docker

# Install Git and other tools
sudo apt install -y git nginx certbot python3-certbot-nginx

# Logout and login again for docker group to take effect
exit
ssh -i "your-key.pem" ubuntu@your-ec2-public-ip
```

**C. Deploy Application:**
```bash
# Clone your repository
git clone https://github.com/yourusername/student-report-system.git
cd student-report-system

# Create environment file
cp .env.example .env
nano .env  # Edit with your configuration

# Build and run with Docker
docker-compose up -d

# Check if running
docker-compose ps
curl http://localhost:5000
```

**D. Configure Domain (GoDaddy):**
1. Go to GoDaddy DNS Management
2. Add/Edit A Record:
   - Name: @ (for root domain) or www
   - Value: Your EC2 Public IP
   - TTL: 600

**E. Setup SSL with Let's Encrypt:**
```bash
# Install SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

**F. Setup Nginx (Production):**
```bash
# Edit nginx configuration
sudo nano /etc/nginx/sites-available/student-report

# Add configuration:
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com www.your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/student-report /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. **Hostinger Deployment** (Budget-friendly option)

Hostinger supports Python applications on their Business/Premium plans:

#### Prerequisites:
- Hostinger Business/Premium plan
- SSH access enabled

#### Step-by-Step Guide:

**A. Access Your Hosting:**
```bash
# Connect via SSH (enable in Hostinger control panel first)
ssh username@your-domain.com
```

**B. Setup Python Environment:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Clone your repository
git clone https://github.com/yourusername/student-report-system.git
cd student-report-system

# Install dependencies
pip install -r requirements.txt
```

**C. Configure for Shared Hosting:**
Create `passenger_wsgi.py` in your domain's public folder:
```python
import sys
import os

# Add your project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import your Flask app
from app_simple import app as application

if __name__ == "__main__":
    application.run()
```

**D. Setup Domain:**
1. In Hostinger control panel, point your domain to the folder containing `passenger_wsgi.py`
2. Enable Python app in the hosting control panel
3. Set Python version to 3.8+

### 4. **Alternative: Heroku Deployment** (Easiest)

**A. Create Heroku-specific files:**
```bash
# Create Procfile
echo "web: gunicorn app_simple:app" > Procfile

# Create runtime.txt
echo "python-3.11.5" > runtime.txt
```

**B. Deploy to Heroku:**
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-app-name

# Deploy
git push heroku main

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key

# Open app
heroku open
```

### 5. **DigitalOcean Droplet** (Similar to AWS)

Similar to AWS EC2 but potentially cheaper:
1. Create Ubuntu 22.04 droplet
2. Follow same Docker setup as AWS
3. Configure domain DNS to point to droplet IP

## 📊 **Cost Comparison**

| Platform | Monthly Cost | Pros | Cons |
|----------|-------------|------|------|
| **AWS EC2** | $10-50+ | Scalable, reliable | Complex setup |
| **Hostinger** | $3-15 | Cheap, managed | Limited control |
| **Heroku** | $7-25 | Easy deployment | Limited free tier |
| **DigitalOcean** | $6-40 | Simple, good docs | Less features than AWS |

## 🔧 **Post-Deployment Checklist**

- [ ] Test all functionality
- [ ] Setup monitoring/logging
- [ ] Configure backups
- [ ] Setup CI/CD pipeline
- [ ] Monitor SSL certificate renewal
- [ ] Setup error tracking (Sentry)
- [ ] Configure domain email forwarding

## 🆘 **Troubleshooting**

**Common Issues:**
1. **Port already in use**: `sudo lsof -i :5000` and kill process
2. **Permission denied**: Check file permissions and user groups
3. **SSL certificate issues**: Verify domain DNS propagation
4. **App not starting**: Check logs with `docker-compose logs`

## 📞 **Support**

For deployment assistance:
1. Check platform-specific documentation
2. Review application logs
3. Test locally first with Docker
4. Verify all environment variables are set

---

**Recommendation**: Start with **AWS EC2** for full control and scalability, or **Hostinger** for budget-conscious deployment.