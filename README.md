# 🚀 ROUTRIX Logistics Platform

**A modern, scalable logistics management system with real-time GPS tracking, OTP authentication, POD management, and booking system.**

Live: https://routrix.in | Dashboard: https://routrix.in/admin

---

## 📋 Table of Contents

1. [Project Structure](#project-structure)
2. [Quick Start](#quick-start)
3. [Deployment](#deployment)
4. [API Documentation](#api-documentation)
5. [Configuration](#configuration)
6. [Contributing](#contributing)
7. [License](#license)

---

## 📁 Project Structure

```
routrix.in/
│
├── 📂 frontend/                    # Frontend web application
│   ├── index.html
│   ├── tracking.html
│   ├── booking.html
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
├── 📂 backend/                     # FastAPI backend (Python)
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   ├── database/
│   ├── uploads/
│   ├── banners/
│   ├── pod_images/
│   ├── media/
│   └── pdf/
│
├── 📂 tests/
├── 📂 media/
├── 🐳 docker-compose.yml
├── 🐳 Dockerfile
├── 🔧 nginx.conf
├── 📖 DEPLOYMENT.md
└── 📝 requirements.txt
```

---

## 🎯 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)
- Git

### Development Setup (Windows)

#### 1️⃣ Setup Backend

```powershell
# Activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file
Copy-Item .env.example .env

# Run backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

#### 2️⃣ Serve Frontend

```powershell
cd frontend
python -m http.server 3000
```

Frontend: `http://localhost:3000`

### Development Setup (Linux/Mac)

```bash
# Activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env
cp .env.example .env

# Run backend
cd backend
uvicorn main:app --reload
```

---

## 🚀 Deployment

### Docker Deployment (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Traditional Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- VPS/Server setup
- Nginx configuration
- SSL certificate installation
- Systemd service setup
- Cloud platform deployment

---

## 🔐 Configuration

### Environment Variables (.env)

```env
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SECRET_KEY=your-secret-key
ADMIN_PASSWORD=admin-password
DRIVER_PAGE_PASSWORD=driver-password
```

---

## 📚 API Endpoints

- `GET /api` - Health check
- `GET /track/{lr}` - Track shipment
- `POST /booking-submit` - Create booking
- `GET /admin/active-trips` - View trips
- `POST /driver-login` - Driver login

Full docs at `/docs`

---

## 📞 Support

- **Docs**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: GitHub Issues
- **Email**: support@routrix.in

---

## 📄 License

ROUTRIX Logistics © 2026. All rights reserved.
