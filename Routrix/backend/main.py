# ROUTRIX Backend – GPS + OTP + POD + Booking + Career + Banner
# Run: uvicorn main:app --reload

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import ClientDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from email.message import EmailMessage
from dotenv import load_dotenv
import random
import smtplib
import ssl
import os
import jwt
import time
import threading
import mimetypes
import logging
from urllib.parse import urljoin
from sqlalchemy import create_engine, Column, String, Float, DateTime, Boolean, Integer, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.exceptions import Error as CloudinaryError

# =============================
# LOGGING SETUP
# =============================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ROUTRIX")

# =============================
# LOAD ENV
# =============================
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465") or "465")
SMTP_USERNAME = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASS")

BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
BACKEND_URL = os.getenv("BACKEND_URL", "https://routrix.onrender.com")
FRONTEND_URL = os.getenv("FRONTEND_URL")
CORS_ORIGINS_ENV = os.getenv("CORS_ORIGINS", "")
DATABASE_URL = os.getenv("DATABASE_URL")
BANNER_STORAGE_TYPE = os.getenv("BANNER_STORAGE_TYPE", "local").strip().lower()
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_ENDPOINT = os.getenv("AWS_S3_ENDPOINT")
BANNER_STORAGE_URL = os.getenv("BANNER_STORAGE_URL")

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# Initialize Cloudinary if credentials are provided
if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET
    )

# Career attachments should stay under Gmail size limits when encoded
CAREER_ATTACHMENT_MAX_BYTES = 8 * 1024 * 1024   # 8 MB per file
CAREER_ATTACHMENT_TOTAL_BYTES = 15 * 1024 * 1024  # 15 MB overall

SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

DRIVER_PASSWORD = os.getenv("DRIVER_PAGE_PASSWORD")

ALGORITHM = "HS256"

# =============================
# APP INIT
# =============================
app = FastAPI(
    title="ROUTRIX Logistics Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===== DATABASE CONFIGURATION =====
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./routrix.db"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

SQLITE_MODE = DATABASE_URL.startswith("sqlite://")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLITE_MODE else {},
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class LiveLocation(Base):
    __tablename__ = "live_locations"
    lr = Column(String, primary_key=True, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    driver_name = Column(String, nullable=False)
    vehicle_no = Column(String, nullable=False)
    mobile = Column(String, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="in_transit")

class OTPRecord(Base):
    __tablename__ = "otp_records"
    lr = Column(String, primary_key=True, index=True)
    otp = Column(String, nullable=False)
    expires = Column(DateTime, nullable=False)
    verified = Column(Boolean, nullable=False, default=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class DeliveryRecord(Base):
    __tablename__ = "delivery_records"
    lr = Column(String, primary_key=True, index=True)
    receiver = Column(String, nullable=False)
    delivered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    email_sent = Column(Boolean, nullable=False, default=False)
    notes = Column(Text, nullable=True)

class Banner(Base):
    __tablename__ = "banners"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, nullable=False)
    storage_url = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def location_to_dict(location: LiveLocation) -> dict:
    return {
        "lr": location.lr,
        "lat": location.lat,
        "lng": location.lng,
        "driver_name": location.driver_name,
        "vehicle_no": location.vehicle_no,
        "mobile": location.mobile,
        "last_seen": location.last_seen.isoformat() if location.last_seen else None,
        "status": location.status,
    }


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=AWS_REGION,
        endpoint_url=AWS_S3_ENDPOINT or None
    )


def build_banner_url(filename: str) -> str:
    """
    Build banner URL - with Cloudinary migration, this primarily returns stored URLs from DB.
    For backward compatibility, still handles legacy storage types.
    """
    # For Cloudinary: storage_url is already the secure URL from Cloudinary
    # This function is kept for backward compatibility but mainly used for legacy cases
    if BANNER_STORAGE_TYPE == "cloudinary" or (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY):
        # Assume filename contains the public_id, construct URL if needed
        return f"https://res.cloudinary.com/{CLOUDINARY_CLOUD_NAME}/image/upload/{filename}"
    
    if BANNER_STORAGE_TYPE == "s3" and AWS_S3_BUCKET:
        if BANNER_STORAGE_URL:
            return f"{BANNER_STORAGE_URL.rstrip('/')}/{filename}"
        if AWS_S3_ENDPOINT:
            return f"{AWS_S3_ENDPOINT.rstrip('/')}/{AWS_S3_BUCKET}/{filename}"
        return f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"

    return f"{BACKEND_URL.rstrip('/')}/banners/{filename}"


def save_banner_file(file: UploadFile):
    """
    Upload banner to Cloudinary with automatic optimizations.
    Returns: (public_id, secure_url)
    """
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in {".jpg", ".jpeg", ".png"}:
        raise HTTPException(
            status_code=400, 
            detail="Only JPG, JPEG, and PNG images are supported"
        )
    
    # Read file contents
    contents = file.file.read() if hasattr(file.file, "read") else None
    if contents is None:
        raise HTTPException(status_code=400, detail="Invalid banner file")
    
    # Check Cloudinary configuration
    if not (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET):
        raise HTTPException(
            status_code=500, 
            detail="Cloudinary is not configured. Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET"
        )
    
    try:
        # Upload to Cloudinary with automatic optimizations
        # Store in 'routrix_banners' folder with timestamp for versioning
        public_id = f"routrix_banners/banner_{int(time.time() * 1000)}"
        
        upload_response = cloudinary.uploader.upload(
            contents,
            public_id=public_id,
            folder="routrix_banners",
            overwrite=False,
            resource_type="image",
            quality="auto",  # Automatic quality optimization
            fetch_format="auto",  # Automatic format optimization
            transformation=[
                {"width": 1200, "crop": "limit", "quality": "auto"}  # Max width 1200px
            ]
        )
        
        public_id = upload_response["public_id"]
        secure_url = upload_response["secure_url"]
        
        logger.info(f"[BANNER] Uploaded to Cloudinary: {public_id} -> {secure_url}")
        return public_id, secure_url
        
    except CloudinaryError as e:
        logger.error(f"[BANNER ERROR] Cloudinary upload failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Cloudinary upload failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[BANNER ERROR] Unexpected error during upload: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Banner upload failed: {str(e)}"
        )


@app.on_event("startup")
def startup_event():
    print("\n" + "="*60)
    print("🚀 ROUTRIX Backend Startup")
    print("="*60)
    
    # Initialize database
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database initialized (SQLAlchemy)")
    
    # Check banner storage configuration
    if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
        print(f"✓ Banner Storage: Cloudinary ({CLOUDINARY_CLOUD_NAME})")
    elif BANNER_STORAGE_TYPE == "s3":
        if not AWS_S3_BUCKET:
            print("✗ CRITICAL: BANNER_STORAGE_TYPE=s3 but AWS_S3_BUCKET not set")
            raise RuntimeError("BANNER_STORAGE_TYPE=s3 requires AWS_S3_BUCKET and AWS credentials")
        print(f"✓ Banner Storage: S3 ({AWS_S3_BUCKET})")
    else:
        print(f"✓ Banner Storage: Local filesystem (banners/)")
    
    # Check SMTP configuration
    if SMTP_USERNAME and SMTP_PASSWORD:
        print(f"✓ SMTP Configured: {SMTP_USERNAME} @ {SMTP_SERVER}:{SMTP_PORT}")
    else:
        print("⚠ WARNING: SMTP credentials not fully configured")
        print(f"   - SMTP_USER: {'SET' if SMTP_USERNAME else 'MISSING'}")
        print(f"   - SMTP_PASS: {'SET' if SMTP_PASSWORD else 'MISSING'}")
        print("   - Email delivery will FAIL")
    
    # Check other critical configuration
    if not SECRET_KEY:
        print("⚠ WARNING: SECRET_KEY not set - JWT tokens may fail")
    else:
        print("✓ JWT Secret Key configured")
    
    print(f"✓ Backend URL: {BACKEND_URL}")
    print(f"✓ Frontend URL: {FRONTEND_URL or '(not set)'}")
    print(f"✓ Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print("="*60 + "\n")


@app.middleware("http")
async def no_cache_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Force no-cache for all critical APIs
    if request.url.path.startswith(("/admin", "/track", "/update-location", "/verify-otp", "/submit-pod", "/booking", "/career", "/banners", "/api")):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        # Add additional headers to defeat browser caching
        response.headers["ETag"] = f'"{int(time.time())}"'
        response.headers["Last-Modified"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    return response

# ===== CORS CONFIGURATION =====
DEFAULT_ALLOWED_ORIGINS = [
    "https://routrix.in",
    "https://www.routrix.in",
    "https://routrix.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
]

allowed_origins = list(DEFAULT_ALLOWED_ORIGINS)
if FRONTEND_URL:
    allowed_origins.append(FRONTEND_URL)

if CORS_ORIGINS_ENV:
    allowed_origins.extend([origin.strip() for origin in CORS_ORIGINS_ENV.split(",") if origin.strip()])

# Remove duplicates while preserving order
seen = set()
allowed_origins = [origin for origin in allowed_origins if not (origin in seen or seen.add(origin))]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

security = HTTPBearer()

# serve banners folder
os.makedirs("banners", exist_ok=True)
app.mount("/banners", StaticFiles(directory="banners"), name="banners")

# =============================
# DATABASE-BACKED STORAGE
# =============================

# =============================
# MODELS
# =============================
class LocationUpdate(BaseModel):
    lr: str
    lat: float
    lng: float
    driver_name: str
    vehicle_no: str
    mobile: str


# ===== HEALTH CHECK =====
@app.get("/api")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "running",
        "service": "ROUTRIX Logistics Backend",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

# =============================
# ADMIN AUTH
# =============================
@app.post("/admin/login")
def admin_login(data: dict):

    password = data.get("password")

    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")

    token = jwt.encode(
        {"role": "admin", "exp": datetime.utcnow() + timedelta(hours=6)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {"access_token": token}


def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    


# =============================
# DRIVER PAGE AUTH
# ============================

# # =============================
# DRIVER LOGIN
# =============================
@app.post("/driver-login")
def driver_login(data: dict):

    password = data.get("password")

    if password != DRIVER_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid driver password")

    token = jwt.encode(
        {"role": "driver", "exp": datetime.utcnow() + timedelta(hours=12)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {"access_token": token}
    

# =============================
# BANNER MANAGEMENT
# =============================
@app.post("/admin/upload-banner")
async def upload_banner(file: UploadFile = File(...), admin=Depends(verify_admin)):
    try:
        public_id, secure_url = save_banner_file(file)

        with SessionLocal() as db:
            # Store public_id as filename and secure_url from Cloudinary
            banner = Banner(filename=public_id, storage_url=secure_url)
            db.add(banner)
            db.commit()
        
        logger.info(f"[BANNER OK] Banner uploaded: {public_id} -> {secure_url}")
        return {
            "success": True,
            "file": public_id,
            "url": secure_url,
            "timestamp": int(time.time())  # For cache-busting on client side
        }
        
    except HTTPException as e:
        logger.error(f"[BANNER ERROR] {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"[BANNER ERROR] Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Banner upload failed: {str(e)}")

@app.get("/banners")
def get_banners(response: Response):
    """
    Get all banners with cache-busting headers.
    Returns list of banners with URLs directly from Cloudinary.
    """
    # Add cache-busting headers to prevent stale banner caching
    response.headers["Cache-Control"] = "public, max-age=3600, must-revalidate"
    response.headers["ETag"] = f'"{int(time.time())}"'
    
    with SessionLocal() as db:
        banners = db.query(Banner).order_by(Banner.created_at.desc()).all()

    if banners:
        banner_list = [
            {
                "filename": banner.filename,  # Cloudinary public_id
                "url": banner.storage_url    # Cloudinary secure_url
            }
            for banner in banners
            if banner.storage_url
        ]
        logger.info(f"[BANNER OK] Retrieved {len(banner_list)} banners from database")
        return {"banners": banner_list}

    logger.info("[BANNER] No banners found in database")
    return {"banners": []}

# =============================
# DELETE BANNER
# =============================

@app.delete("/admin/delete-banner/{filename}")
def delete_banner(filename: str, admin=Depends(verify_admin)):
    """
    Delete banner from both Cloudinary and database.
    filename parameter is the Cloudinary public_id.
    """
    try:
        # First, delete from database
        with SessionLocal() as db:
            banner = db.query(Banner).filter(Banner.filename == filename).first()
            if not banner:
                raise HTTPException(
                    status_code=404,
                    detail=f"Banner {filename} not found in database"
                )
            
            db.delete(banner)
            db.commit()
            logger.info(f"[BANNER OK] Removed from database: {filename}")

        # Then, delete from Cloudinary using public_id
        if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
            try:
                result = cloudinary.uploader.destroy(filename)
                if result.get("result") == "ok":
                    logger.info(f"[BANNER OK] Deleted from Cloudinary: {filename}")
                else:
                    logger.warning(f"[BANNER WARN] Cloudinary deletion response: {result}")
            except CloudinaryError as e:
                logger.error(f"[BANNER ERROR] Cloudinary deletion failed: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Could not delete banner from Cloudinary: {str(e)}"
                )
        
        return {
            "success": True,
            "message": f"Banner {filename} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[BANNER ERROR] Unexpected error deleting {filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting banner: {str(e)}"
        )

# =============================
# DRIVER GPS UPDATE
# =============================
@app.post("/update-location")
def update_location(data: LocationUpdate):
    lr = data.lr.strip()

    with SessionLocal() as db:
        location = db.query(LiveLocation).filter(LiveLocation.lr == lr).first()
        if not location:
            send_start_email(lr, data.driver_name, data.vehicle_no)
            location = LiveLocation(
                lr=lr,
                lat=data.lat,
                lng=data.lng,
                driver_name=data.driver_name,
                vehicle_no=data.vehicle_no,
                mobile=data.mobile,
                last_seen=datetime.utcnow(),
                status="in_transit"
            )
            db.add(location)
        else:
            location.lat = data.lat
            location.lng = data.lng
            location.driver_name = data.driver_name
            location.vehicle_no = data.vehicle_no
            location.mobile = data.mobile
            location.last_seen = datetime.utcnow()
            location.status = "in_transit"
        db.commit()

    return {"success": True}


# =============================
# ADMIN VIEW LIVE TRUCKS
# =============================
@app.get("/admin/live-trucks")
def get_live_trucks(admin=Depends(verify_admin)):
    with SessionLocal() as db:
        locations = db.query(LiveLocation).order_by(LiveLocation.last_seen.desc()).all()
    return {location.lr: location_to_dict(location) for location in locations}


# =============================
# CLIENT TRACKING
# =============================
@app.get("/track/{lr}")
def track_vehicle(lr: str):
    lr = lr.strip()
    with SessionLocal() as db:
        location = db.query(LiveLocation).filter(LiveLocation.lr == lr).first()

    if not location:
        return {"error": "Tracking ID not found"}

    return location_to_dict(location)


# =============================
# OTP GENERATION
# =============================
@app.post("/admin/generate-otp/{lr}")
def generate_otp(lr: str, admin=Depends(verify_admin)):

    otp = str(random.randint(100000, 999999))
    with SessionLocal() as db:
        record = db.query(OTPRecord).filter(OTPRecord.lr == lr).first()
        if not record:
            record = OTPRecord(
                lr=lr,
                otp=otp,
                expires=datetime.utcnow() + timedelta(minutes=10),
                verified=False,
                updated_at=datetime.utcnow()
            )
            db.add(record)
        else:
            record.otp = otp
            record.expires = datetime.utcnow() + timedelta(minutes=10)
            record.verified = False
            record.updated_at = datetime.utcnow()
        db.commit()

    return {"lr": lr, "otp": otp}


# =============================
# OTP VERIFY
# =============================
@app.post("/verify-otp")
def verify_otp(payload: dict):

    lr = payload.get("lr", "").strip()
    otp = payload.get("otp", "").strip()

    with SessionLocal() as db:
        record = db.query(OTPRecord).filter(OTPRecord.lr == lr).first()

        if not record:
            return {"success": False, "error": "OTP not generated"}

        if datetime.utcnow() > record.expires:
            return {"success": False, "error": "OTP expired"}

        if record.otp != otp:
            return {"success": False, "error": "Invalid OTP"}

        record.verified = True
        record.updated_at = datetime.utcnow()
        db.commit()

    return {"success": True}

# =============================
# DELETE POD AFTER 24 HOURS 
# =============================
def delete_pod_after_delay(path):
    time.sleep(86400)  # 24 hours

    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"🗑 POD deleted after 24h: {path}")
        except Exception as e:
            print("Delete error:", e)

# =============================
# POD SUBMIT
# =============================
@app.post("/submit-pod")
async def submit_pod(
    lr: str = Form(...),
    receiver_name: str = Form(...),
    image: UploadFile = File(...)
):
    try:
        with SessionLocal() as db:
            otp_record = db.query(OTPRecord).filter(OTPRecord.lr == lr).first()
            if not otp_record or not otp_record.verified:
                print(f"[POD ERROR] OTP not verified for {lr}")
                return {"success": False, "error": "OTP not verified"}

        os.makedirs("pod_images", exist_ok=True)
        image_path = f"pod_images/pod_{lr}.jpg"

        with open(image_path, "wb") as f:
            f.write(await image.read())

        email_sent = send_pod_email(lr, receiver_name, image_path)
        if email_sent:
            try:
                os.remove(image_path)
                print(f"[POD OK] POD image deleted after successful email: {image_path}")
            except Exception as e:
                print(f"[POD WARNING] Could not delete POD image {image_path}: {e}")
        else:
            print(f"[POD ERROR] Email failed for {lr}, keeping image for 24h")
            threading.Thread(
                target=delete_pod_after_delay,
                args=(image_path,),
                daemon=True
            ).start()

        with SessionLocal() as db:
            delivery = DeliveryRecord(
                lr=lr,
                receiver=receiver_name,
                delivered_at=datetime.utcnow(),
                email_sent=email_sent,
                notes=None
            )
            db.merge(delivery)
            db.commit()

            location = db.query(LiveLocation).filter(LiveLocation.lr == lr).first()
            if location:
                location.status = "delivered"
                db.commit()

        if not email_sent:
            print(f"[POD ERROR] Failed to send POD email for {lr}")
            return {"success": False, "error": "POD image captured but email delivery failed. Your delivery has been recorded."}

        print(f"[POD OK] POD submitted successfully for {lr}")
        return {"success": True, "message": "POD submitted and email sent successfully"}
        
    except Exception as e:
        print(f"[POD ERROR] Exception in submit_pod: {e}")
        return {"success": False, "error": f"An error occurred while submitting POD: {str(e)[:100]}"}


# =============================
# BOOKING FORM EMAIL (ADVANCED)
# =============================
@app.post("/booking")
async def booking_form(request: Request):
    try:
        data = await request.form()

        # ===== REQUEST ID =====
        sender_name = data.get('Sender Name', '').strip()
        sender_mobile = data.get('Sender Mobile', '').strip()
        # Clean name: take first word, remove spaces, upper case
        name_part = ''.join(sender_name.split()).upper()[:10]  # limit to 10 chars
        mobile_part = sender_mobile[-5:] if len(sender_mobile) >= 5 else sender_mobile
        request_id = f"{name_part}{mobile_part}"

        # ===== HANDLE ARRAYS =====
        services = data.getlist("Services[]") if "Services[]" in data else []
        services_text = ", ".join(services) if services else "None"

        # ===== SAFE VALUE FUNCTION =====
        def val(x):
            return x if x else "N/A"

        # ===== SMART SUBJECT =====
        subject = f"ROUTRIX BOOKING | {val(data.get('From City'))} → {val(data.get('To City'))} |  {val(data.get('Sender Name'))}, {val(data.get('Sender Mobile'))}"
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SMTP_USERNAME
        msg["To"] = SMTP_USERNAME

        # ===== EMAIL BODY =====
        msg.set_content(f"""
🚚 ROUTRIX BOOKING RECEIVED
REQUEST ID: {request_id}

==============================
👤 CONSIGNOR (SENDER)
==============================
Name: {val(data.get('Sender Name'))}
Mobile: {val(data.get('Sender Mobile'))}
Email: {val(data.get('Sender Email'))}
GST: {val(data.get('Sender GSTIN'))}

Pickup Address:
{val(data.get('Pickup Address'))}

==============================
📦 CONSIGNEE (RECEIVER)
==============================
Name: {val(data.get('Receiver Name'))}
Mobile: {val(data.get('Receiver Mobile'))}
Email: {val(data.get('Receiver Email'))}
GST: {val(data.get('Receiver GSTIN'))}

Delivery Address:
{val(data.get('Delivery Address'))}

==============================
🚛 MOVEMENT
==============================
From: {val(data.get('From City'))}
To: {val(data.get('To City'))}
Value: ₹{val(data.get('Value of Goods (INR)'))}

==============================
📦 GOODS DETAILS
==============================
Description: {val(data.get('Goods Description'))}
Weight: {val(data.get('Approx Weight (kg)'))} kg
Items: {val(data.get('Total Items'))}
Fragile: {val(data.get('Fragile'))}
Cargo Type: {val(data.get('Cargo Type'))}
Breakdown: {val(data.get('Goods Breakdown'))}

==============================
🛠 SERVICES SELECTED
==============================
{services_text}

==============================
📄 E-WAY BILL
==============================
Status: {val(data.get('E-Way Bill Status'))}
Number: {val(data.get('E-Way Bill Number'))}

==============================
⚡ SYSTEM INFO
==============================
Request ID: {request_id}
Time: {datetime.utcnow()}
""")

        email_success = send_email(msg)
        if not email_success:
            print(f"[BOOKING ERROR] Failed to send admin email for Request ID: {request_id}")
            return {"success": False, "error": "Failed to send booking notification to our team. Please contact us directly."}

        print(f"[BOOKING OK] Admin email sent for Request ID: {request_id}")
        time.sleep(1)

        # ===== SEND EMAIL TO CUSTOMER IF EMAIL PROVIDED =====
        customer_email = data.get('Sender Email', '').strip()
        if customer_email:
            # Safely escape HTML special characters
            safe_name = (data.get('Sender Name', 'Valued Client')).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
            safe_request_id = request_id.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            html_msg = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>ROUTRIX Booking Confirmation</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap" rel="stylesheet">
</head>

<body style="margin:0; padding:0; background:#0b0b0b; font-family:Arial, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#0b0b0b; padding:20px;">
<tr>
<td align="center">

<table width="600" cellpadding="0" cellspacing="0" style="background:#111; border-radius:10px; overflow:hidden; border:1px solid #222;">

<!-- HEADER -->
<tr>
<td style="background:#000; padding:25px; text-align:center;">

<h1 style="color:#fff; margin:0; font-size:30px; letter-spacing:3px; font-family:'Orbitron', Arial, sans-serif;">
ROUTRIX
</h1>

<p style="color:#e10600; font-size:12px; margin-top:8px;">
Goods Transport & Logistics Services
</p>

<p style="color:#aaa; font-size:11px; letter-spacing:2px; margin-top:6px;">
WE TRANSPORT ANYTHING ANYWHERE
</p>

</td>
</tr>

<!-- BODY -->
<tr>
<td style="padding:30px; color:#ddd;">

<h2 style="color:#fff;">Thank you """ + safe_name + """, for booking with ROUTRIX!</h2>

<p style="font-size:14px; line-height:1.6;">
Your shipment request has been successfully received and is under processing.
Our team is reviewing your details and assigning the most suitable vehicle.
Tracking details will be shared with you shortly.
</p>

<!-- ORDER ID -->
<div style="background:#1a1a1a; border-left:4px solid #e10600; padding:15px; margin:20px 0;">
<p style="margin:0; font-size:13px;">
<strong style="color:#fff;">Your Order ID:</strong><br>
<span style="color:#e10600; font-size:16px; font-weight:bold;">""" + safe_request_id + """</span>
</p>
</div>

<!-- ONLY PLANT IMAGE -->
<div style="text-align:center; margin:20px 0;">
<img src="https://cdn-icons-png.flaticon.com/512/2909/2909766.png" width="70" alt="Plant">
</div>

<!-- SAVE EARTH -->
<div style="background:#0f1a0f; border-left:4px solid #22c55e; padding:15px; margin:20px 0;">
<p style="margin:0; font-size:14px;">
🌱 <strong>You are now part of our "Save Earth" mission.</strong><br><br>
For every 100 bookings, ROUTRIX plants 100 trees in the name of our valued clients.<br>
Together, we are building a greener future.
</p>
</div>

<!-- ABOUT -->
<h3 style="color:#fff;">About ROUTRIX</h3>

<p style="font-size:14px; line-height:1.6;">
ROUTRIX provides reliable logistics and goods transport services across India.
From local deliveries to construction logistics and business transport, we ensure safe, timely, and efficient movement of goods.
</p>

<ul style="font-size:13px; line-height:1.6; padding-left:18px;">
<li>Goods Transport by Road</li>
<li>Local & Intercity Delivery</li>
<li>Construction Logistics</li>
<li>Packaging & Last-Mile Delivery</li>
<li>Business Logistics Support</li>
</ul>

<!-- CONTACT BLOCK -->
<div style="background:#101820; border-left:4px solid #e10600; padding:15px; margin:20px 0;">
<p style="margin:0; font-size:13px; line-height:1.6;">

<strong style="color:#fff;">ROUTRIX Logistics</strong><br><br>

📞 Mobile: +91 8826282253<br>

📍 Office Address:<br>
Flat No. 127, 2nd Floor, PKT-A2,<br>
Sector-17, Rohini, New Delhi – 110085<br>
Landmark: Near Sec-17 Bus Stand

</p>
</div>

<!-- LINKS -->
<p style="font-size:14px;">
🌐 Website: <a href="https://www.routrix.in" style="color:#e10600;">www.routrix.in</a><br>
📧 Email: routrix.info@gmail.com<br>
📱 Instagram: @routrix.in<br>
📘 Facebook & ▶ YouTube: ROUTRIX
</p>

<!-- PAYMENT -->
<div style="background:#1a0000; border-left:4px solid #e10600; padding:12px; margin:20px 0;">
<p style="margin:0; font-size:13px;">
⚠️ Please ensure all payments are made only in the name of <strong>ROUTRIX</strong>.
</p>
</div>

</td>
</tr>

<!-- FOOTER -->
<tr>
<td style="background:#000; text-align:center; padding:20px;">

<p style="color:#fff; font-size:13px; margin:0;">
<strong>Driven by Trust. Delivered with Care.</strong>
</p>

<p style="color:#777; font-size:12px; margin-top:10px;">
ROUTRIX – Goods Transport & Logistics Services
</p>

<p style="color:#777; font-size:12px;">
Founder & CEO – Mr. Suraj Jha
</p>

</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""
            customer_msg = EmailMessage()
            customer_msg["Subject"] = f"Booking Confirmation - ROUTRIX | Order ID: {request_id}"
            customer_msg["From"] = SMTP_USERNAME
            customer_msg["To"] = customer_email
            customer_msg["Cc"] = SMTP_USERNAME  # CC admin to track customer notifications
            customer_msg.set_content("Please view this email in HTML format.")
            customer_msg.add_alternative(html_msg, subtype="html")
            customer_sent = send_email(customer_msg)
            if not customer_sent:
                print(f"[BOOKING ERROR] Failed to send customer email to {customer_email} for Request ID: {request_id}")
                return {"success": False, "error": "Failed to send booking confirmation email to you. We have received your booking and will contact you shortly."}

            print(f"[BOOKING OK] Customer email sent to {customer_email} for Request ID: {request_id}")

        return {
            "success": True,
            "request_id": request_id,
            "message": "Booking submitted successfully!"
        }
    except Exception as e:
        print(f"[BOOKING ERROR] Exception in booking handler: {e}")
        return {
            "success": False,
            "error": f"An error occurred while processing your booking: {str(e)[:100]}"
        }

# =============================
# CAREER FORM EMAIL
# =============================
@app.post("/career")
async def career_form(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.form()
    except ClientDisconnect:
        print("Career form aborted: client disconnected during upload")
        return {"success": False, "error": "Request aborted before upload completed"}
    except Exception as e:
        print(f"Career form parse error: {e}")
        return {"success": False, "error": "Unable to parse career form data"}

    if not data:
        return {"success": False, "error": "No form data received"}

    category = data.get("category", "Career").strip() or "Career"
    applicant_name = f"{data.get('first_name', '').strip()} {data.get('last_name', '').strip()}".strip() or "Applicant"
    subject = data.get("_subject") or f"ROUTRIX CAREER REQUEST | {category} | {applicant_name}"
    cc_email = data.get("_cc")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_USERNAME
    msg["To"] = SMTP_USERNAME
    if cc_email:
        msg["Cc"] = cc_email

    def label_for(key: str) -> str:
        label_map = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'age': 'Age',
            'vehicle_number': 'Vehicle Number',
            'mobile': 'Mobile Number',
            'whatsapp_same': 'WhatsApp Same',
            'role': 'Role',
            'vehicle_type': 'Vehicle Type',
            'other_vehicle_type': 'Other Vehicle Type',
            'base_location': 'Base Location',
            'routes': 'Preferred Routes',
            'price_10km': 'Minimum Charge (10 km)',
            'driving license': 'Driving License',
            'aadhaar': 'Aadhaar / ID Proof',
            'city': 'City / Area',
            'experience': 'Experience (Years)',
            'availability': 'Availability',
            'rate': 'Daily Rate Expectation (₹)',
            'notes': 'Additional Notes',
            'logistics_exp': 'Logistics Experience',
            'resume': 'Resume',
            'category': 'Category',
        }
        key = key.strip()
        return label_map.get(key, key.replace('_', ' ').replace('-', ' ').title())

    def format_value(value):
        if hasattr(value, 'filename') and value.filename:
            return None
        if isinstance(value, (list, tuple)):
            values = [str(item).strip() for item in value if str(item).strip()]
            return ', '.join(values) if values else 'N/A'
        text = str(value).strip()
        return text or 'N/A'

    text_lines = [f"New Career Inquiry ({category})", "", f"Applicant: {applicant_name}", ""]
    html_rows = []
    attachment_names = []
    attachments = []
    skipped_attachments = []
    skip_keys = {"_subject", "_cc", "_captcha"}

    for key, value in data.multi_items():
        if key.startswith("_") or key in skip_keys or key == "category":
            continue

        if key == 'other_vehicle_type' and str(data.get('vehicle_type', '')).strip().lower() == 'other' and data.get('other_vehicle_type'):
            continue

        if hasattr(value, "filename") and value.filename:
            filename = os.path.basename(value.filename)
            attachment_names.append((key, filename))
            attachments.append((key, filename, value))
            continue

        if key == 'vehicle_type' and str(value).strip().lower() == 'other':
            other_value = data.get('other_vehicle_type', '')
            if other_value:
                value = other_value

        display_label = label_for(key)
        field_value = format_value(value)
        text_lines.append(f"{display_label}: {field_value}")
        html_rows.append(
            f"<tr><td style='padding:8px 12px;border:1px solid #333;background:#0b0b0b;color:#ccc;width:220px;font-weight:700;'>{display_label}</td>"
            f"<td style='padding:8px 12px;border:1px solid #333;background:#080808;color:#eee;'>{field_value}</td></tr>"
        )

    accepted_attachments = []
    total_attachment_bytes = 0

    for field, filename, upload_file in attachments:
        file_bytes = await upload_file.read()
        file_size = len(file_bytes)

        if file_size == 0:
            skipped_attachments.append((filename, "empty file"))
            continue

        if file_size > CAREER_ATTACHMENT_MAX_BYTES:
            skipped_attachments.append((filename, f"file too large ({file_size // 1024} KB)"))
            continue

        if total_attachment_bytes + file_size > CAREER_ATTACHMENT_TOTAL_BYTES:
            skipped_attachments.append((filename, "skipped to keep email under size limits"))
            continue

        total_attachment_bytes += file_size
        accepted_attachments.append((filename, file_bytes))

    # Note: CAREER_ATTACHMENT_MAX_BYTES and CAREER_ATTACHMENT_TOTAL_BYTES were misspelled, now fixed

    if skipped_attachments:
        text_lines.append("")
        text_lines.append("Some attachments were not included due to size limits:")
        for filename, reason in skipped_attachments:
            text_lines.append(f"- {filename}: {reason}")

    html_parts = [
        "<html>",
        "  <body style='margin:0;padding:0;font-family:Arial, sans-serif;background:#050505;color:#fff;'>",
        "    <table width='100%' cellpadding='0' cellspacing='0' style='background:#050505;padding:24px;'>",
        "      <tr>",
        "        <td align='center'>",
        "          <table width='680' cellpadding='0' cellspacing='0' style='background:#0a0a0a;border:1px solid #222;border-radius:14px;overflow:hidden;'>",
        "            <tr><td style='padding:25px 28px;background:#000;text-align:center;'>",
        "              <h1 style='margin:0;font-family:Orbitron,Arial,sans-serif;font-size:28px;color:#fff;'>ROUTRIX</h1>",
        "              <p style='margin:8px 0 0;color:#e10600;font-size:12px;letter-spacing:2px;'>Career Request Notification</p>",
        "              <p style='margin:10px 0 0;color:#aaa;font-size:13px;'>New job request received from the career page.</p>",
        "            </td></tr>",
        "            <tr><td style='padding:0 28px 22px;'>",
        "              <table width='100%' cellpadding='0' cellspacing='0' style='border-collapse:collapse;'>",
        "                <tr><td style='padding:12px 12px;border:1px solid #333;background:#0b0b0b;color:#ccc;width:220px;font-weight:700;'>Category</td><td style='padding:12px 12px;border:1px solid #333;background:#080808;color:#eee;'>" + category + "</td></tr>",
        "                <tr><td style='padding:12px 12px;border:1px solid #333;background:#0b0b0b;color:#ccc;font-weight:700;'>Applicant</td><td style='padding:12px 12px;border:1px solid #333;background:#080808;color:#eee;'>" + applicant_name + "</td></tr>",
        *html_rows,
        "              </table>",
        "            </td></tr>",
        "            <tr><td style='padding:20px 28px 24px;background:#090909;'>",
        "              <p style='margin:0;color:#ccc;font-size:14px;'>Attachments:</p>",
        "              <ul style='margin:8px 0 0;padding-left:18px;color:#ddd;font-size:14px;'>"
    ]

    if attachment_names:
        for field, filename in attachment_names:
            html_parts.append(f"                <li>{field.replace('_', ' ').title()}: {filename}</li>")
    else:
        html_parts.append("                <li>No attachment uploaded.</li>")

    if skipped_attachments:
        for filename, reason in skipped_attachments:
            html_parts.append(f"                <li>{filename}: skipped ({reason})</li>")

    html_parts.extend([
        "              </ul>",
        "            </td></tr>",
        "          </table>",
        "        </td>",
        "      </tr>",
        "    </table>",
        "  </body>",
        "</html>"
    ])

    html_body = "\n".join(html_parts)
    msg.set_content("\n".join(text_lines))
    msg.add_alternative(html_body, subtype='html')

    attachments_added = 0
    for filename, file_bytes in accepted_attachments:
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            maintype, subtype = mime_type.split("/", 1)
        else:
            maintype, subtype = "application", "octet-stream"
        msg.add_attachment(
            file_bytes,
            maintype=maintype,
            subtype=subtype,
            filename=filename
        )
        attachments_added += 1

    email_result = send_email(msg)
    if not email_result:
        print(f"Failed to send career email for {applicant_name}. Subject: {subject}")
        return {"success": False, "error": "Failed to send career application email. Please try again."}
    
    print(f"Career email sent successfully. Subject: {subject}. Attachments: {attachments_added}")
    return {"success": True}


# =============================
# EMAIL FUNCTIONS
# =============================
def send_start_email(lr, driver, vehicle):

    msg = EmailMessage()

    msg["Subject"] = f"ROUTRIX TRIP STARTED | {lr}"
    msg["From"] = SMTP_USERNAME
    msg["To"] = SMTP_USERNAME

    msg.set_content(f"""
Trip Started

Tracking ID: {lr}
Driver: {driver}
Vehicle: {vehicle}
Time: {datetime.utcnow()}
""")

    send_email(msg)


def send_pod_email(lr, receiver, image_path):

    msg = EmailMessage()

    msg["Subject"] = f"{lr} DELIVERY COMPLETED"
    msg["From"] = SMTP_USERNAME
    msg["To"] = SMTP_USERNAME

    msg.set_content(f"""
Delivery Completed

Tracking ID: {lr}
Receiver: {receiver}
Time: {datetime.utcnow()}
""")

    with open(image_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="image",
            subtype="jpeg",
            filename=os.path.basename(image_path)
        )

    return send_email(msg)


def send_email(msg):
    """Stable email sender with retry + timeout + logging"""

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print("ERROR: SMTP credentials not configured (SMTP_USER or SMTP_PASS missing)")
        return False

    context = ssl.create_default_context()
    
    # Try SSL on port 465 first (preferred for Gmail)
    for attempt in range(3):  # retry 3 times
        try:
            print(f"[SMTP SSL] Connecting to {SMTP_SERVER}:{SMTP_PORT} (Attempt {attempt+1}/3)")
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=15, context=context) as smtp:
                print(f"[SMTP SSL] Connected, logging in as {SMTP_USERNAME}")
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                smtp.send_message(msg)
                print(f"[SMTP] Email sent successfully via SSL (Attempt {attempt+1})")
                return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"[SMTP ERROR] Authentication failed: {e}")
            print(f"[SMTP ERROR] Ensure you're using an app password, not your regular Gmail password")
            return False  # don't retry auth errors

        except smtplib.SMTPException as e:
            print(f"[SMTP ERROR] SSL attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2)

        except Exception as e:
            print(f"[SMTP ERROR] SSL attempt {attempt+1} general error: {e}")
            if attempt < 2:
                time.sleep(2)

    print("[SMTP] SSL failed, falling back to STARTTLS on port 587")
    
    # Fallback to STARTTLS
    for attempt in range(3):
        try:
            print(f"[SMTP STARTTLS] Connecting to {SMTP_SERVER}:587 (Attempt {attempt+1}/3)")
            with smtplib.SMTP(SMTP_SERVER, 587, timeout=15) as smtp:
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()
                print(f"[SMTP STARTTLS] Connected, logging in as {SMTP_USERNAME}")
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                smtp.send_message(msg)
                print(f"[SMTP] Email sent successfully via STARTTLS (Attempt {attempt+1})")
                return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"[SMTP ERROR] Authentication failed: {e}")
            print(f"[SMTP ERROR] Ensure you're using an app password, not your regular Gmail password")
            return False

        except smtplib.SMTPException as e:
            print(f"[SMTP ERROR] STARTTLS attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(2)

        except Exception as e:
            print(f"[SMTP ERROR] STARTTLS attempt {attempt+1} general error: {e}")
            if attempt < 2:
                time.sleep(2)

    print("[SMTP CRITICAL] Email failed after all SMTP attempts (SSL + STARTTLS)")
    return False


# =============================
# BOOKING PAGE (SERVE HTML)
# =============================


#1. Show all ACTIVE trips
#2. Allow cancel/reset any trip
#3. Fix wrong LR easily

@app.get("/admin/active-trips")
def get_active_trips(admin=Depends(verify_admin)):
    with SessionLocal() as db:
        locations = db.query(LiveLocation).order_by(LiveLocation.last_seen.desc()).all()
    return {location.lr: location_to_dict(location) for location in locations}

# Admin can reset/cancel a trip by LR – this deletes live location and OTP, allowing a fresh start

@app.post("/admin/reset-trip/{lr}")
def reset_trip(lr: str, admin=Depends(verify_admin)):
    with SessionLocal() as db:
        location = db.query(LiveLocation).filter(LiveLocation.lr == lr).first()
        if location:
            db.delete(location)
        otp_record = db.query(OTPRecord).filter(OTPRecord.lr == lr).first()
        if otp_record:
            db.delete(otp_record)
        db.commit()

    return {"success": True}
# =============================
# HEALTH CHECK
# =============================
