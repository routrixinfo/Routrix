# ROUTRIX Backend – GPS + OTP + POD + Booking + Career + Banner
# Run: uvicorn main:app --reload

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import ClientDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict
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

# =============================
# LOAD ENV
# =============================
load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USERNAME = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASS")

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

# ===== CORS CONFIGURATION =====
ALLOWED_ORIGINS = [
    "https://routrix.in",
    "https://www.routrix.in",
    "https://routrix.vercel.app",  # Vercel deployment
    "http://localhost:3000",        # Local frontend
    "http://localhost:5173",        # Vite dev
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
# IN MEMORY DATABASE
# =============================
live_locations: Dict[str, dict] = {}
otp_store: Dict[str, dict] = {}
delivery_records: Dict[str, dict] = {}

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

    if not file.filename.lower().endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Only JPG allowed")

    os.makedirs("banners", exist_ok=True)

    # unique filename
    filename = f"banner_{int(time.time())}.jpg"
    path = f"banners/{filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    return {"success": True, "file": filename}

@app.get("/banners")
def get_banners():

    if not os.path.exists("banners"):
        return {"banners": []}

    files = os.listdir("banners")

    # only valid jpg files
    images = [f for f in files if f.endswith(".jpg")]

    # sort newest first
    images.sort(reverse=True)

    return {"banners": images}
# =============================
# DELETE BANNER
# =============================

@app.delete("/admin/delete-banner/{filename}")
def delete_banner(filename: str, admin=Depends(verify_admin)):

    path = f"banners/{filename}"

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(path)

    return {"success": True}

# =============================
# DRIVER GPS UPDATE
# =============================
@app.post("/update-location")
def update_location(data: LocationUpdate):

    lr = data.lr.strip()

    # first update -> trip started email
    if lr not in live_locations:
        send_start_email(lr, data.driver_name, data.vehicle_no)

    live_locations[lr] = {
        "lat": data.lat,
        "lng": data.lng,
        "driver_name": data.driver_name,
        "vehicle_no": data.vehicle_no,
        "mobile": data.mobile,
        "last_seen": datetime.utcnow().isoformat(),
        "status": "in_transit"
    }

    return {"success": True}


# =============================
# ADMIN VIEW LIVE TRUCKS
# =============================
@app.get("/admin/live-trucks")
def get_live_trucks(admin=Depends(verify_admin)):
    return live_locations


# =============================
# CLIENT TRACKING
# =============================
@app.get("/track/{lr}")
def track_vehicle(lr: str):

    lr = lr.strip()

    if lr not in live_locations:
        return {"error": "Tracking ID not found"}

    return live_locations[lr]


# =============================
# OTP GENERATION
# =============================
@app.post("/admin/generate-otp/{lr}")
def generate_otp(lr: str, admin=Depends(verify_admin)):

    otp = str(random.randint(100000, 999999))

    otp_store[lr] = {
        "otp": otp,
        "expires": datetime.utcnow() + timedelta(minutes=10),
        "verified": False
    }

    return {"lr": lr, "otp": otp}


# =============================
# OTP VERIFY
# =============================
@app.post("/verify-otp")
def verify_otp(payload: dict):

    lr = payload.get("lr", "").strip()
    otp = payload.get("otp", "").strip()

    if lr not in otp_store:
        return {"success": False, "error": "OTP not generated"}

    record = otp_store[lr]

    if datetime.utcnow() > record["expires"]:
        return {"success": False, "error": "OTP expired"}

    if record["otp"] != otp:
        return {"success": False, "error": "Invalid OTP"}

    record["verified"] = True

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

    if lr not in otp_store or not otp_store[lr]["verified"]:
        return {"success": False, "error": "OTP not verified"}

    os.makedirs("pod_images", exist_ok=True)

    image_path = f"pod_images/pod_{lr}.jpg"

    # ✅ save image
    with open(image_path, "wb") as f:
        f.write(await image.read())

    # ✅ send email first
    email_sent = send_pod_email(lr, receiver_name, image_path)

    if email_sent:
        try:
            os.remove(image_path)
            print(f"🗑 POD deleted immediately after email: {image_path}")
        except Exception as e:
            print("POD delete error:", e)
    else:
        # fallback cleanup after 24 hours if email did not go through
        threading.Thread(
            target=delete_pod_after_delay,
            args=(image_path,),
            daemon=True
        ).start()

    # ✅ save delivery record
    delivery_records[lr] = {
        "receiver": receiver_name,
        "delivered_at": datetime.utcnow().isoformat()
    }

    # ✅ update status
    if lr in live_locations:
        live_locations[lr]["status"] = "delivered"

    return {"success": True}


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

        try:
            send_email(msg)
            print(f"Admin email sent for Request ID: {request_id}")

            time.sleep(1) 

        except Exception as e:
            print(f"Failed to send admin email: {str(e)}")

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
            try:
                send_email(customer_msg)
                print(f"Customer email sent to {customer_email} for Request ID: {request_id}")
            except Exception as e:
                print(f"Failed to send customer email to {customer_email}: {str(e)}")

        return {
            "success": True,
            "request_id": request_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
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

    background_tasks.add_task(send_email, msg)
    print(f"Queued career email send. Subject: {subject}. Attachments: {attachments_added}")
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

    context = ssl.create_default_context()
    for attempt in range(3):  # retry 3 times
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=15, context=context) as smtp:
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                smtp.send_message(msg)

                print(f"Email sent successfully (SSL attempt {attempt+1})")
                return True

        except smtplib.SMTPAuthenticationError:
            print("SMTP Authentication Error: Check credentials")
            return False  # don't retry auth errors

        except smtplib.SMTPException as e:
            print(f"SMTP SSL Error (Attempt {attempt+1}): {e}")
            time.sleep(2)

        except Exception as e:
            print(f"SMTP SSL General Error (Attempt {attempt+1}): {e}")
            time.sleep(2)

    print("Falling back to STARTTLS on port 587")
    for attempt in range(3):
        try:
            with smtplib.SMTP(SMTP_SERVER, 587, timeout=15) as smtp:
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                smtp.send_message(msg)

                print(f"Email sent successfully (STARTTLS attempt {attempt+1})")
                return True

        except smtplib.SMTPAuthenticationError:
            print("SMTP Authentication Error: Check credentials")
            return False

        except smtplib.SMTPException as e:
            print(f"SMTP STARTTLS Error (Attempt {attempt+1}): {e}")
            time.sleep(2)

        except Exception as e:
            print(f"SMTP STARTTLS General Error (Attempt {attempt+1}): {e}")
            time.sleep(2)

    print("Email failed after all SMTP attempts")
    return False


# =============================
# BOOKING PAGE (SERVE HTML)
# =============================
@app.get("/booking", response_class=HTMLResponse)
def booking_page():
    with open("booking.html", "r", encoding="utf-8") as f:
        return f.read()


# =============================
# CAREER PAGE (SERVE HTML)
# =============================
@app.get("/career", response_class=HTMLResponse)
def career_page():
    with open("career.html", "r", encoding="utf-8") as f:
        return f.read()



#1. Show all ACTIVE trips
#2. Allow cancel/reset any trip
#3. Fix wrong LR easily

@app.get("/admin/active-trips")
def get_active_trips():
    return live_locations

# Admin can reset/cancel a trip by LR – this deletes live location and OTP, allowing a fresh start

@app.post("/admin/reset-trip/{lr}")
def reset_trip(lr: str):

    if lr in live_locations:
        del live_locations[lr]

    if lr in otp_store:
        del otp_store[lr]

    return {"success": True}
# =============================
# HEALTH CHECK
# =============================
