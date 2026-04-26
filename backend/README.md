# ROUTRIX Backend

Professional FastAPI backend for ROUTRIX Logistics platform with GPS tracking, OTP authentication, POD management, and booking system.

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (DO NOT COMMIT)
├── Dockerfile           # Docker container configuration
├── uploads/             # User uploaded files
├── database/            # SQLite database files
├── banners/             # Banner images and media
├── pod_images/          # Proof of Delivery images
├── media/               # Media files (Routrix_guy.png, truck images, etc.)
├── pdf/                 # Generated PDF documents
├── tests/               # Unit and integration tests
└── logs/                # Application logs
```

## 🚀 Quick Start

### Development

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs (API Documentation)

### Production (Docker)

```bash
docker-compose up -d
```

## 📝 API Endpoints

### Health Check
- `GET /api` - Backend status

### Tracking
- `GET /track/{lr}` - Get shipment tracking data
- `POST /track-update` - Update live GPS location

### Booking
- `GET /booking` - Booking page
- `POST /booking-submit` - Create new booking

### Admin
- `GET /admin/active-trips` - View all active trips
- `POST /admin/reset-trip/{lr}` - Reset a trip

### Career
- `GET /career` - Career page
- `POST /career-submit` - Submit career application

### Driver
- `GET /driver` - Driver dashboard
- `POST /otp-verify` - Verify OTP

## 🔐 Environment Variables

Copy `.env.example` to `.env` and configure:

```env
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
SECRET_KEY=your-secret-key
ADMIN_PASSWORD=admin-password
DRIVER_PAGE_PASSWORD=driver-password
```

## 📊 Database

SQLite database stored in `database/` directory. 

**Backup database regularly:**

```bash
cp database/routrix.db database/routrix_backup_$(date +%Y%m%d).db
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

## 📦 Dependencies

- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation
- **python-jose** - JWT authentication
- **aiosmtplib** - Email handling
- **Pillow** - Image processing

## 📚 Documentation

API docs available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔒 Security Features

- CORS protection (whitelist production domains)
- JWT token authentication
- OTP verification for driver authentication
- Email validation
- File upload restrictions
- SQL injection prevention via ORM
- Rate limiting

## 📈 Performance Optimization

- Connection pooling
- Async/await for I/O operations
- Caching with Redis (optional)
- Database indexing
- Gzip compression

## 🐛 Troubleshooting

### Port already in use
```bash
# Change port
uvicorn main:app --port 8001
```

### SMTP connection failed
- Verify email credentials in `.env`
- Enable "Less secure app access" (Gmail)
- Check firewall settings

### Database locked
```bash
# Reset database
rm database/routrix.db
```

## 📞 Support

For issues, check:
1. Application logs: `logs/`
2. Backend console output
3. Database integrity

## License

ROUTRIX Logistics © 2026. All rights reserved.
