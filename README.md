# 🚀 ROUTRIX Logistics Platform

**Next-Generation AI-Driven Logistics Ecosystem for Real-Time Transport, Smart Tracking, and Intelligent Delivery Operations.**

🌐 Live Platform: https://routrix.in
🛠 Admin Dashboard: https://routrix.in/admin

---

## 🔥 Overview

ROUTRIX is a modern logistics infrastructure platform designed to deliver **speed, transparency, and intelligence** in goods transportation across India.

It combines:

* 🚚 Real-time GPS tracking
* 🔐 OTP-based delivery verification
* 📸 Proof of Delivery (POD) system
* 📦 Smart booking & dispatch system
* 🧠 Scalable backend for automation & AI integration

---

## ⚡ Key Features

### 🚚 Logistics Engine

* Real-time vehicle tracking
* Live route updates
* Driver-side telemetry sync

### 🔐 Secure Delivery System

* OTP-based delivery verification
* Fraud prevention layer
* Delivery authentication logs

### 📸 Proof of Delivery (POD)

* Camera capture with metadata overlay
* Timestamp + GPS stamping
* Secure upload & storage

### 🧑‍✈️ Driver Command Panel

* Trip lifecycle control
* GPS auto-sync
* Resume interrupted deliveries

### 📦 Booking System

* Customer shipment creation
* Backend processing & assignment
* Dynamic logistics handling

### 🛠 Admin Dashboard

* Active trip monitoring
* Banner/content management
* Operational control panel

---

## 🏗️ Project Architecture

```
ROUTRIX.IN/
│
├── frontend/        # UI Layer (Vercel)
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
│   ├── robots.txt
│   ├── sitemap.xml
│   └── manifest.json
│
├── backend/         # FastAPI Backend (Render)
│   ├── main.py
│   ├── requirements.txt
│   ├── database/
│   ├── uploads/
│   ├── banners/
│   ├── pod_images/
│   ├── media/
│   └── pdf/
│
└── .gitignore
```

---

## 🧠 Tech Stack

### Frontend

* HTML5, CSS3, JavaScript
* PWA (Service Worker + Manifest)
* Responsive UI (Mobile + Desktop)

### Backend

* FastAPI (Python)
* Uvicorn (ASGI server)
* JWT Authentication
* File Upload Handling

### Infrastructure

* Vercel (Frontend Hosting)
* Render (Backend Hosting)
* GitHub (Version Control)

---

## ⚙️ Quick Start (Local Development)

### 🔹 Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

👉 Runs on: `http://127.0.0.1:8000`
👉 Docs: `http://127.0.0.1:8000/docs`

---

### 🔹 Frontend

```bash
cd frontend
python -m http.server 3000
```

👉 Runs on: `http://localhost:3000`

---

## 🔐 Environment Variables

Create `.env` inside `backend/`

```env
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
SECRET_KEY=your_secret_key
ADMIN_PASSWORD=admin_password
DRIVER_PAGE_PASSWORD=driver_password
```

---

## 🌐 Deployment

### Backend (Render)

* Build:

```bash
pip install -r requirements.txt
```

* Start:

```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

---

### Frontend (Vercel)

* Deploy `frontend/` directory
* Set API base URL in:

```js
const BACKEND = "https://your-backend.onrender.com";
```

---

## 📡 API Endpoints

| Method | Endpoint           | Description      |
| ------ | ------------------ | ---------------- |
| GET    | `/api`             | Health check     |
| POST   | `/booking`         | Create booking   |
| GET    | `/track/{lr}`      | Track shipment   |
| POST   | `/update-location` | GPS update       |
| POST   | `/verify-otp`      | OTP verification |
| POST   | `/submit-pod`      | Upload POD       |
| POST   | `/driver-login`    | Driver auth      |

👉 Full docs: `/docs`

---

## 🔒 Security

* JWT-based authentication
* OTP verification system
* Environment-based secrets
* Input validation & error handling

---

## 🚀 Future Roadmap

* 🤖 AI-based route optimization
* 📊 Analytics dashboard
* 🌍 Multi-country expansion
* 📱 Native mobile app
* ☁️ Cloud storage (S3 / CDN)

---

## 🤝 Contributing

Currently private development.
Collaboration coming soon.

---

## 📄 License

ROUTRIX Logistics © 2026
All rights reserved.

---

## 💡 Vision

**ROUTRIX is not just logistics — it's a technology-driven transport intelligence system built for the future of global commerce.**

## 📞 Customer Support

Need help with your shipment or platform?

Reach out to our support team:

📧 routrix.in@gmail.com  , Routrix.info@gmail.com 

📩 surajjhastudy01@gmail.com  

Our team is available to assist you with bookings, tracking, and delivery queries.
