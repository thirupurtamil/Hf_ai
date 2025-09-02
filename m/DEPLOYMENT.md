# Mobile AI Django - Deployment Guide

## Quick Start for Mobile/Termux

### 1. Install Termux (Android)
```bash
# Download from F-Droid or GitHub releases
# https://github.com/termux/termux-app/releases
```

### 2. Setup Termux Environment
```bash
# Update packages
pkg update && pkg upgrade -y

# Install required packages
pkg install python git redis clang make cmake python-pip

# Give storage permission
termux-setup-storage

# Install additional dependencies
pip install --upgrade pip setuptools wheel
```

### 3. Clone and Setup Project
```bash
# Clone the project
git clone <your-repository-url>
cd mobile_ai_django

# Run setup script
python setup.py

# Or manual setup:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy and edit environment file
cp .env.example .env
nano .env

# Add your API keys:
# OPENAI_API_KEY=your-key-here
# HUGGINGFACE_API_KEY=your-key-here
```

### 5. Initialize Database
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 6. Start Services
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Django
python manage.py runserver 0.0.0.0:8000

# Terminal 3: Start Celery Worker
celery -A mobile_ai_django worker --loglevel=info

# Terminal 4: Start Celery Beat (optional)
celery -A mobile_ai_django beat --loglevel=info
```

## Raspberry Pi Zero 2W Deployment

### 1. Install Raspberry Pi OS
```bash
# Use Raspberry Pi Imager
# Enable SSH and configure WiFi during setup
```

### 2. System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv git redis-server nginx
sudo apt install python3-dev build-essential

# Enable services
sudo systemctl enable redis-server
sudo systemctl enable nginx
```

### 3. Deploy Application
```bash
# Clone project
cd /var/www/
sudo git clone <your-repository> mobile_ai_django
sudo chown -R pi:pi mobile_ai_django
cd mobile_ai_django

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### 4. Configure Services

#### Gunicorn Service
```bash
# Create service file
sudo nano /etc/systemd/system/mobile-ai-django.service
```

```ini
[Unit]
Description=Mobile AI Django
After=network.target

[Service]
User=pi
Group=pi
WorkingDirectory=/var/www/mobile_ai_django
ExecStart=/var/www/mobile_ai_django/venv/bin/gunicorn mobile_ai_django.wsgi:application --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Celery Worker Service
```bash
sudo nano /etc/systemd/system/celery-worker.service
```

```ini
[Unit]
Description=Celery Worker
After=network.target redis.target

[Service]
User=pi
Group=pi
WorkingDirectory=/var/www/mobile_ai_django
ExecStart=/var/www/mobile_ai_django/venv/bin/celery -A mobile_ai_django worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Celery Beat Service
```bash
sudo nano /etc/systemd/system/celery-beat.service
```

```ini
[Unit]
Description=Celery Beat
After=network.target redis.target

[Service]
User=pi
Group=pi
WorkingDirectory=/var/www/mobile_ai_django
ExecStart=/var/www/mobile_ai_django/venv/bin/celery -A mobile_ai_django beat --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5. Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/mobile_ai_django
```

```nginx
server {
    listen 80;
    server_name your-domain.com;  # or IP address

    location /static/ {
        alias /var/www/mobile_ai_django/staticfiles/;
    }

    location /media/ {
        alias /var/www/mobile_ai_django/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/mobile_ai_django /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Start All Services
```bash
# Enable and start services
sudo systemctl enable mobile-ai-django celery-worker celery-beat
sudo systemctl start mobile-ai-django celery-worker celery-beat

# Check status
sudo systemctl status mobile-ai-django
sudo systemctl status celery-worker
sudo systemctl status celery-beat
```

## Production Optimizations

### 1. Database Optimization
```python
# In settings.py for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mobile_ai_django',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### 2. Security Settings
```python
# Production security
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'your-ip-address']

# Use strong secret key
SECRET_KEY = 'your-very-long-random-secret-key'

# HTTPS settings
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### 3. Performance Settings
```python
# Caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session storage
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

## Monitoring and Maintenance

### 1. Log Files
```bash
# Django logs
tail -f /var/www/mobile_ai_django/django.log

# System logs
sudo journalctl -u mobile-ai-django -f
sudo journalctl -u celery-worker -f
```

### 2. Database Maintenance
```bash
# Backup database
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# Clean old data (via Django admin or management command)
python manage.py cleanup_old_data
```

### 3. Update Application
```bash
# Pull updates
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart mobile-ai-django celery-worker celery-beat
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```bash
   sudo systemctl start redis-server
   redis-cli ping  # Should return PONG
   ```

2. **Permission Errors**
   ```bash
   sudo chown -R pi:pi /var/www/mobile_ai_django
   chmod +x manage.py
   ```

3. **Port Already in Use**
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

4. **Memory Issues (Pi Zero)**
   ```bash
   # Increase swap
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=1024
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

### Performance Tuning for Low-Resource Devices

1. **Optimize Celery**
   ```bash
   # Run with fewer concurrent processes
   celery -A mobile_ai_django worker --concurrency=2 --loglevel=info
   ```

2. **Database Optimization**
   ```python
   # Use connection pooling
   DATABASES['default']['CONN_MAX_AGE'] = 600
   ```

3. **Memory Management**
   ```python
   # Limit query results
   DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440  # 2.5 MB
   FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440   # 2.5 MB
   ```

## SSL Certificate (Optional)

```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

This deployment guide ensures your Mobile AI Django application runs efficiently on resource-constrained devices while maintaining security and performance.
