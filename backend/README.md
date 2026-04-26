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



## 📞 Support

For issues, check:
1. Application logs: `logs/`
2. Backend console output
3. Database integrity

## License

ROUTRIX Logistics © 2026. All rights reserved.
