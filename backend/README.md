# 🚀 ROUTRIX Backend

**FastAPI-powered backend for ROUTRIX Logistics platform**
Handles GPS tracking, OTP authentication, POD uploads, booking system, and admin controls.

---

## ⚡ Overview

This backend is designed as a **pure API service**, connected to:

* 🌐 Frontend → Vercel
* ⚙️ Backend → Render

---

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI app
├── requirements.txt     # Dependencies
├── banners/             # Banner images
├── uploads/             # User uploads
├── pod_images/          # POD images
├── media/               # Static media
├── pdf/                 # Generated PDFs
├── database/            # Optional storage
```

---

## 🚀 Run Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

👉 API Docs: http://127.0.0.1:8000/docs

---

## 🌐 Deployment (Render)

### Settings:

* **Root Directory:** `backend`
* **Build Command:**

```bash
pip install -r requirements.txt
```

* **Start Command:**

```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

---

## 🔐 Environment Variables

Set in **Render Dashboard (not .env file)**

```env
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_password
SECRET_KEY=your_secret
ADMIN_PASSWORD=admin_pass
DRIVER_PAGE_PASSWORD=driver_pass
```

---

## 📡 API Endpoints

### Health

* `GET /api`

### Tracking

* `GET /track/{lr}`
* `POST /update-location`

### OTP

* `POST /admin/generate-otp/{lr}`
* `POST /verify-otp`

### POD

* `POST /submit-pod`

### Booking

* `POST /booking`

### Career

* `POST /career`

### Admin

* `POST /admin/login`
* `GET /admin/live-trucks`
* `GET /admin/active-trips`
* `POST /admin/reset-trip/{lr}`
* `POST /admin/upload-banner`
* `DELETE /admin/delete-banner/{filename}`

---

## 🖼 Static Files

* `/banners/{filename}` → Banner images

---

## 🔒 Security

* JWT-based authentication
* OTP verification system
* CORS restricted to frontend domains
* File validation for uploads

---

## ⚠️ Important Notes

* ❌ Backend does NOT serve HTML
* ❌ Frontend handled separately (Vercel)
* ❌ Do NOT commit `.env`

---

## 📞 Support

📧 [support@routrix.in](mailto:support@routrix.in)
📩 [surajjhastudy01@gmail.com](mailto:surajjhastudy01@gmail.com)

---

## 📄 License

ROUTRIX Logistics © 2026
All rights reserved.
