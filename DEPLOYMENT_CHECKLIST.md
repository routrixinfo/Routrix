# ✅ ROUTRIX Deployment Checklist & Verification Guide

## 📋 Phase 1: Project Organization Review

```
✅ Frontend Structure Created
  ├── ✅ frontend/ directory created
  ├── ✅ robots.txt (SEO optimization)
  ├── ✅ sitemap.xml (SEO sitemap)
  └── ✅ .htaccess (Apache caching & security rules)

✅ Backend Structure Created
  ├── ✅ backend/ directory created
  ├── ✅ backend/database/ (SQLite storage)
  ├── ✅ backend/uploads/ (User files)
  ├── ✅ backend/pod_images/ (Proof of Delivery)
  ├── ✅ backend/banners/ (Dynamic banners)
  ├── ✅ backend/media/ (Assets)
  ├── ✅ backend/pdf/ (Generated documents)
  ├── ✅ backend/README.md (Backend docs)
  ├── ✅ backend/deploy.sh (Linux/Mac deployment)
  └── ✅ backend/deploy.bat (Windows deployment)

✅ Deployment Configuration Files
  ├── ✅ Dockerfile (Backend containerization)
  ├── ✅ docker-compose.yml (Multi-service orchestration)
  ├── ✅ nginx.conf (Reverse proxy & static files)
  ├── ✅ .env.example (Environment template)
  ├── ✅ .gitignore (Security - exclude sensitive files)
  ├── ✅ requirements-prod.txt (Production dependencies)
  ├── ✅ DEPLOYMENT.md (Comprehensive deployment guide)
  └── ✅ README.md (Updated with deployment info)
```

---

## 🔄 Phase 2: Pre-Deployment Setup

### Step 1: Clone/Prepare Project

```bash
cd /path/to/routrix.in
git init
git add .
git commit -m "Initial deployment-ready structure"
```

### Step 2: Create Environment File

Windows:
```powershell
Copy-Item .env.example .env
```

Linux/Mac:
```bash
cp .env.example .env
```

Edit `.env` with **actual values**:

```env
# CHANGE THESE VALUES!
SMTP_USER=your-gmail@gmail.com
SMTP_PASS=your-app-specific-password
SECRET_KEY=generate-strong-secret-key-32-chars-min
ADMIN_PASSWORD=strong-admin-password-here
DRIVER_PAGE_PASSWORD=strong-driver-password-here
CORS_ORIGINS=https://routrix.in,https://www.routrix.in
ENVIRONMENT=production
```

**⚠️ CRITICAL: Never commit .env to git!** ✅ Already in .gitignore

### Step 3: Verify File Structure

```bash
# Check directory structure
ls -la        # Linux/Mac
dir /s        # Windows

# Expected output includes:
# - frontend/
# - backend/
# - docker-compose.yml
# - nginx.conf
# - Dockerfile
# - .env
# - DEPLOYMENT.md
```

---

## 🚀 Phase 3: Deployment Options

Choose one deployment strategy:

### Option A: Docker Deployment (⭐ RECOMMENDED)

**Requirements:**
- Docker installed
- Docker Compose installed

**Steps:**

1. **Build Docker image**
   ```bash
   docker build -t routrix-backend:latest .
   ```

2. **Verify image**
   ```bash
   docker images | grep routrix
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Check service status**
   ```bash
   docker-compose ps
   # Should show: backend (UP), nginx (UP)
   ```

5. **Verify backend health**
   ```bash
   curl http://localhost:8000/api
   # Response: {"status": "ROUTRIX backend running"}
   ```

6. **Access application**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option B: Traditional VPS Deployment

**Requirements:**
- Ubuntu/Debian server
- Python 3.11+
- Nginx
- SSL certificate

**Steps:**

1. **SSH into server**
   ```bash
   ssh user@your-server.com
   ```

2. **Navigate to backend**
   ```bash
   cd /path/to/routrix.in/backend
   ```

3. **Run deployment script**
   ```bash
   bash deploy.sh production
   ```
   
   Or on Windows:
   ```bash
   deploy.bat production
   ```

4. **Setup Nginx**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/routrix
   sudo ln -s /etc/nginx/sites-available/routrix /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. **Setup SSL with Let's Encrypt**
   ```bash
   sudo certbot --nginx -d routrix.in -d www.routrix.in
   ```

### Option C: Cloud Platform Deployment

#### Heroku
```bash
heroku create routrix-app
heroku config:set SMTP_USER=...
git push heroku main
```

#### DigitalOcean App Platform
- Connect GitHub repo in DigitalOcean dashboard
- Add environment variables from .env
- Auto-deploy on push

#### AWS Elastic Beanstalk
```bash
eb init routrix
eb create production
eb deploy
```

---

## ✅ Phase 4: Post-Deployment Verification

### 4.1: Backend Health Checks

```bash
# Health endpoint
curl http://your-domain.com/api
# Expected: {"status": "ROUTRIX backend running"}

# Track endpoint
curl http://your-domain.com/track/RTX-1234
# Should return tracking data or 404

# Swagger UI
curl -I http://your-domain.com/docs
# Expected: 200 OK
```

### 4.2: Frontend Verification

| Page | URL | Status |
|------|-----|--------|
| Homepage | `/` | ✅ Should load |
| Tracking | `/tracking.html` | ✅ Should load |
| Booking | `/booking.html` | ✅ Should load |
| Admin | `/admin.html` | ✅ Should load |
| 404 Page | `/nonexistent` | ✅ Should show 404 |

### 4.3: Security Checks

```bash
# Check security headers
curl -I http://your-domain.com
# Should see:
# X-Content-Type-Options: nosniff
# X-Frame-Options: SAMEORIGIN

# Check CORS
curl -H "Origin: https://routrix.in" \
     -H "Access-Control-Request-Method: GET" \
     -I http://your-domain.com/api
# Should allow if origin in CORS_ORIGINS
```

### 4.4: Database Verification

```bash
# Check database file exists
ls -la backend/database/routrix.db

# Backup database
cp backend/database/routrix.db backend/database/routrix_backup_$(date +%s).db
```

### 4.5: Log Verification

```bash
# Docker logs
docker-compose logs -f backend

# Traditional deployment logs
tail -f /var/log/nginx/access.log
sudo journalctl -u routrix-backend -f
```

---

## 🔐 Phase 5: Security Hardening

### 5.1: File Permissions

```bash
# Restrict .env access
chmod 600 .env

# Set proper directory permissions
chmod 755 frontend/
chmod 755 backend/
chmod 700 database/
```

### 5.2: SSL/HTTPS

```bash
# On production, enforce HTTPS
# Nginx automatically redirects HTTP → HTTPS

# Verify SSL certificate
curl -I https://routrix.in
# Should show: 200 OK with SSL
```

### 5.3: Firewall Setup

```bash
# Ubuntu/Debian firewall
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### 5.4: Update Environment Variables

```bash
# Generate new SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env with all new secure values
nano .env
```

---

## 📊 Phase 6: Monitoring & Maintenance

### 6.1: Daily Checks

```bash
# Container health (Docker)
docker-compose ps

# Service status (Traditional)
sudo systemctl status routrix-backend
sudo systemctl status nginx

# Quick API test
curl http://your-domain.com/api
```

### 6.2: Weekly Backups

```bash
# Backup database
cd backend
cp database/routrix.db database/rotated_backup_$(date +%Y%m%d).db

# Cleanup old backups (keep last 30 days)
find database/ -name "rotated_backup_*" -mtime +30 -delete
```

### 6.3: Monthly Updates

```bash
# Update dependencies
pip install --upgrade -r requirements-prod.txt

# Update Docker images
docker pull python:3.11-slim
docker pull nginx:latest
docker-compose up -d --pull always
```

### 6.4: Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/routrix

# Add:
/var/log/nginx/routrix*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
}
```

---

## 🆘 Troubleshooting

### Issue: Backend not responding

```bash
# Check if port is in use
lsof -i :8000  # Linux/Mac
netstat -ano | grep :8000  # Windows

# Check logs
docker-compose logs backend

# Restart service
docker-compose restart backend
```

### Issue: SMTP/Email not working

```bash
# Verify credentials in .env
cat .env | grep SMTP

# Test SMTP connection
python3 -c "
import smtplib
try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=5)
    server.login('$SMTP_USER', '$SMTP_PASS')
    print('✅ SMTP connection successful')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

### Issue: Database locked

```bash
# Clear database
rm backend/database/routrix.db
# Backend will recreate on next run
```

### Issue: 502 Bad Gateway (Nginx)

```bash
# Check backend is running
docker ps  # or systemctl status routrix-backend

# Check nginx config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

---

## 🎯 Final Deployment Checklist

Before marking as "Production Ready":

- [ ] All environment variables configured in .env
- [ ] Database initialized and tested
- [ ] SSL/HTTPS certificate installed
- [ ] Frontend robots.txt and sitemap.xml accessible
- [ ] Backend health check (`/api`) responding
- [ ] API documentation (`/docs`) accessible
- [ ] Email functionality tested (SMTP working)
- [ ] CORS origins updated for production domain
- [ ] Security headers verified
- [ ] Firewall configured
- [ ] Backup strategy implemented
- [ ] Monitoring/alerting in place
- [ ] Database backup completed
- [ ] Error pages (404, 500) tested
- [ ] All HTML pages load without errors
- [ ] Assets (images, CSS, JS) loading correctly
- [ ] Docker containers running healthily
- [ ] Logs configured and monitored
- [ ] Performance baseline established
- [ ] Documentation updated

---

## 🚨 Critical Security Reminders

1. **🔑 Never commit .env** - Already in .gitignore
2. **🔐 Change default passwords** - Update ADMIN_PASSWORD, DRIVER_PAGE_PASSWORD
3. **📧 Use app-specific email password** - Not your main Gmail password
4. **🛡️ Enable 2FA** - On GitHub and hosting accounts
5. **📝 Keep .env.example updated** - But never with real values
6. **🔄 Rotate secrets regularly** - Every 90 days recommended
7. **💾 Backup before updates** - Database and code

---

## 📞 Support Resources

- **Deployment Guide**: See `DEPLOYMENT.md`
- **Backend Docs**: See `backend/README.md`
- **Issues**: Check logs first
- **Contact**: support@routrix.in

---

## ✨ You're All Set!

```bash
# Deployment successful? Run:
curl https://routrix.in/api
# Should return: {"status": "ROUTRIX backend running"}

# 🎉 ROUTRIX is live!
```

---

**Last Updated:** April 24, 2026  
**Status:** ✅ Production Ready  
**Maintained by:** ROUTRIX Team
