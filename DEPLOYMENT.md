# ============================================
# 🚀 ROUTRIX DEPLOYMENT GUIDE
# ============================================

## Project Structure (After Organization)

```
routrix.in/
├── frontend/
│   ├── index.html
│   ├── booking.html
│   ├── tracking.html
│   ├── driver.html
│   ├── admin.html
│   ├── services.html
│   ├── about.html
│   ├── career.html
│   ├── legal.html
│   ├── help.html
│   ├── 404.html
│   ├── assets/
│   ├── static/
│   ├── banners/
│   ├── robots.txt
│   ├── sitemap.xml
│   └── manifest.json
│
├── backend/
│   ├── (Python backend files)
│
├── database/
├── uploads/
├── midia/
├── pod_images/
├── tests/
│
├── main.py (Backend server)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── .env.example
├── .env (create from .env.example)
├── .gitignore
└── README.md
```

---

## 🌐 Deployment Options

### **Option 1: Docker + Docker Compose (RECOMMENDED)**

#### Prerequisites
- Docker installed
- Docker Compose installed

#### Steps

1. **Clone/Setup the project**
```bash
cd /path/to/routrix.in
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your actual credentials
nano .env
```

3. **Build and start containers**
```bash
docker-compose up -d
```

4. **Verify services**
```bash
# Check backend health
curl http://localhost:8000/api

# Check frontend
curl http://localhost:80
```

5. **View logs**
```bash
docker-compose logs -f backend
docker-compose logs -f nginx
```

6. **Stop services**
```bash
docker-compose down
```

---

### **Option 2: Traditional VPS/Server Deployment**

#### Prerequisites
- Python 3.11+
- Nginx
- SSL Certificate (Let's Encrypt)
- Ubuntu/Debian server

#### Setup Backend

1. **SSH into server**
```bash
ssh user@your-server.com
```

2. **Clone repository**
```bash
cd /var/www
git clone https://github.com/yourusername/routrix.in.git
cd routrix.in
```

3. **Setup Python virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Create .env file**
```bash
cp .env.example .env
nano .env  # Add credentials
```

5. **Test backend locally**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

6. **Setup systemd service**
```bash
sudo nano /etc/systemd/system/routrix-backend.service
```

Add:
```ini
[Unit]
Description=ROUTRIX Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/routrix.in
Environment="PATH=/var/www/routrix.in/venv/bin"
ExecStart=/var/www/routrix.in/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable routrix-backend
sudo systemctl start routrix-backend
```

#### Setup Nginx

1. **Create Nginx config**
```bash
sudo nano /etc/nginx/sites-available/routrix.in
```

2. **Copy nginx.conf content to your server**

3. **Enable site**
```bash
sudo ln -s /etc/nginx/sites-available/routrix.in /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d routrix.in -d www.routrix.in
```

#### Setup Frontend

Frontend files are served by Nginx from `/usr/share/nginx/html`

1. **Copy frontend files**
```bash
sudo cp -r frontend/* /usr/share/nginx/html/
```

2. **Set permissions**
```bash
sudo chown -R www-data:www-data /usr/share/nginx/html
sudo chmod -R 755 /usr/share/nginx/html
```

---

### **Option 3: Cloud Platforms**

#### Deploy on Heroku
```bash
heroku create routrix-app
git push heroku main
heroku config:set SMTP_USER=your-email@gmail.com
heroku config:set SMTP_PASS=your-app-password
```

#### Deploy on AWS (Elastic Beanstalk)
```bash
eb init -p python-3.11 routrix
eb create routrix-prod
eb deploy
```

#### Deploy on DigitalOcean App Platform
- Connect GitHub repo
- Set environment variables
- Deploy

---

## 📋 Pre-Deployment Checklist

- [ ] Environment variables configured (.env)
- [ ] Database initialized and backed up
- [ ] SSL certificate installed
- [ ] CORS origins updated for production domain
- [ ] Email credentials verified
- [ ] All images and assets in place
- [ ] Frontend robots.txt and sitemap.xml in place
- [ ] Backend API endpoints tested
- [ ] Database migrations completed
- [ ] Logs configured and monitored
- [ ] Backup strategy in place
- [ ] Monitoring/alerting setup (optional)

---

## 🔒 Security Hardening

1. **Update .env passwords**
```bash
# Generate strong secrets
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Restrict file permissions**
```bash
chmod 600 .env
chmod 755 frontend/
```

3. **Enable firewall**
```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

4. **Backup database regularly**
```bash
# Add to crontab
0 2 * * * cd /var/www/routrix.in && python3 -c "import shutil; shutil.copy('database/routrix.db', f'backup/routrix_{datetime.now().isoformat()}.db')"
```

---

## 🚀 Running the Application

### Local Development
```bash
# Terminal 1: Backend
ENVIRONMENT=development uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Serve frontend (simple HTTP server)
cd frontend
python3 -m http.server 3000
```

### Production (Docker)
```bash
docker-compose -f docker-compose.yml up -d
```

### Production (Traditional)
```bash
sudo systemctl start routrix-backend
sudo systemctl restart nginx
```

---

## 📊 Monitoring & Logs

```bash
# Docker logs
docker-compose logs -f

# System logs
sudo journalctl -u routrix-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔄 CI/CD Pipeline (Optional)

Use GitHub Actions for automated deployment:

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main, production ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
        run: |
          # SSH and deploy
```

---

## ✅ Testing Endpoints

```bash
# Health check
curl http://localhost:8000/api

# Track shipment
curl http://localhost:8000/track/RTX-1234

# Create booking
curl -X POST http://localhost:8000/booking \
  -H "Content-Type: application/json" \
  -d '{"pickup":"Delhi","delivery":"Mumbai"}'
```

---

## 📞 Support & Troubleshooting

- Check logs first: `docker-compose logs`
- Verify environment variables: `cat .env`
- Test connectivity: `curl http://localhost:8000/api`
- Browser console for frontend errors (F12)

---

## License

ROUTRIX Logistics © 2026. All rights reserved.
