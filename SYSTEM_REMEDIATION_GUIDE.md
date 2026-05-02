# ROUTRIX System Remediation - Production-Ready Architecture

## CRITICAL ISSUES & IMMEDIATE FIXES

### 1. SMTP EMAIL FAILURES (BOOKING & CAREER)

**Root Cause Found:**
- `career.html` uses **HARDCODED URL**: `https://routrix.onrender.com/career` 
- `booking.html` correctly uses `BACKEND` variable
- `api-config.js` loaded at END of body (too late for forms)

**FIX:**
```html
<!-- In career.html HEAD, ADD before all other scripts (except meta): -->
<script src="/static/js/api-config.js"></script>

<!-- Then replace these 3 lines: -->
<!-- OLD: -->
<form id="f1" onsubmit="buildDriverSubject()" action="https://routrix.onrender.com/career" method="POST"...
<form id="f2" onsubmit="buildLabourSubject()" action="https://routrix.onrender.com/career" method="POST"...
<form id="f3" onsubmit="buildOpsSubject()" action="https://routrix.onrender.com/career" method="POST"...

<!-- NEW: -->
<form id="f1" onsubmit="submitCareerForm(event)" method="POST" enctype="multipart/form-data">
<form id="f2" onsubmit="submitCareerForm(event)" method="POST" enctype="multipart/form-data">
<form id="f3" onsubmit="submitCareerForm(event)" method="POST" enctype="multipart/form-data">
```

**Add this JavaScript at end of career.html (before closing body):**
```javascript
async function submitCareerForm(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);
  
  try {
    const response = await fetch(`${BACKEND}/career`, {
      method: 'POST',
      body: formData
    });
    const result = await response.json();
    
    if (result.success) {
      console.log('Career form submitted successfully');
      alert('Thank you! Your application has been submitted.');
      form.reset();
    } else {
      alert(`Error: ${result.error || 'Failed to submit'}`);
    }
  } catch (error) {
    console.error('Career submission error:', error);
    alert('Error submitting form. Please try again.');
  }
}
```

---

### 2. ADMIN PANEL JWT VALIDATION

**Add to admin.html in HEAD (before body):**
```javascript
<script>
  // Validate JWT on page load
  function validateAdminToken() {
    const token = localStorage.getItem('adminToken');
    
    if (!token) {
      document.getElementById('loginCard').classList.remove('hidden');
      document.getElementById('adminPanel').classList.add('hidden');
      return false;
    }
    
    // Decode JWT without verification (for expiry check only)
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiryTime = payload.exp * 1000;
      const now = Date.now();
      
      if (now >= expiryTime) {
        console.warn('Token expired');
        localStorage.removeItem('adminToken');
        document.getElementById('loginCard').classList.remove('hidden');
        document.getElementById('adminPanel').classList.add('hidden');
        return false;
      }
      
      // Token valid - show admin panel
      document.getElementById('loginCard').classList.add('hidden');
      document.getElementById('adminPanel').classList.remove('hidden');
      return true;
    } catch (e) {
      console.error('Invalid token format:', e);
      localStorage.removeItem('adminToken');
      return false;
    }
  }
  
  // Run on page load
  window.addEventListener('load', validateAdminToken);
  
  // Also check periodically
  setInterval(validateAdminToken, 60000); // Check every minute
</script>
```

---

### 3. DRIVER LR CONFLICTS

**Backend Issue:** LiveLocation table allows only 1 record per LR (primary key).

**Solution Options:**

**Option A: Prevent Duplicate LR (Recommended)**
```python
# In backend main.py, modify update_location():

@app.post("/update-location")
def update_location(data: LocationUpdate):
    lr = data.lr.strip()
    
    with SessionLocal() as db:
        location = db.query(LiveLocation).filter(LiveLocation.lr == lr).first()
        
        if location and location.driver_name != data.driver_name:
            # Different driver trying to use same LR
            logger.warning(f"LR {lr} already in use by {location.driver_name}, new request from {data.driver_name}")
            raise HTTPException(
                status_code=409,
                detail=f"This LR is already being used by another driver. Please use a different LR."
            )
        
        if not location:
            send_start_email(lr, data.driver_name, data.vehicle_no)
            location = LiveLocation(...)
            db.add(location)
        else:
            # Same driver, same LR - just update
            location.lat = data.lat
            location.lng = data.lng
            # ... update other fields
        
        db.commit()
    
    return {"success": True}
```

**Option B: Add Driver Table (Better for Multi-Driver)**
```python
# Create driver table in backend
class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True)
    driver_id = Column(String, unique=True, nullable=False)  # UUID or auto-generated
    name = Column(String, nullable=False)
    vehicle_no = Column(String, nullable=False)
    mobile = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class LiveLocation(Base):
    __tablename__ = "live_locations"
    lr = Column(String, primary_key=True)
    driver_id = Column(String, ForeignKey("drivers.driver_id"), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    # ... rest of fields
```

---

### 4. DATABASE CLEANUP - OTP EXPIRY

**Add to backend main.py:**
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', minutes=5)
def cleanup_expired_otps():
    """Delete expired OTP records every 5 minutes"""
    with SessionLocal() as db:
        try:
            expired_count = db.query(OTPRecord).filter(
                OTPRecord.expires < datetime.utcnow()
            ).delete()
            db.commit()
            if expired_count > 0:
                logger.info(f"[CLEANUP] Deleted {expired_count} expired OTP records")
        except Exception as e:
            logger.error(f"[CLEANUP ERROR] Failed to cleanup OTPs: {e}")
            db.rollback()

# Start scheduler on app startup
@app.on_event("startup")
def startup():
    if not scheduler.running:
        scheduler.start()
        logger.info("[SCHEDULER] Background cleanup scheduler started")
```

---

### 5. CACHE STRATEGY - NO MORE 404 CACHING

**Update frontend vercel.json:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".",
  "cleanUrls": true,
  "trailingSlash": false,
  "headers": [
    {
      "source": "/admin",
      "headers": [
        { "key": "Cache-Control", "value": "no-store, no-cache, must-revalidate" }
      ]
    },
    {
      "source": "/career",
      "headers": [
        { "key": "Cache-Control", "value": "no-store, no-cache, must-revalidate" }
      ]
    },
    {
      "source": "/(.*)\\.html$",
      "headers": [
        { "key": "Cache-Control", "value": "no-store, no-cache, must-revalidate" }
      ]
    },
    {
      "source": "/assets/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    },
    {
      "source": "/static/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }
      ]
    }
  ],
  "rewrites": [
    { "source": "/admin", "destination": "/admin.html" },
    { "source": "/career", "destination": "/career.html" },
    { "source": "/booking", "destination": "/booking.html" },
    { "source": "/about", "destination": "/about.html" },
    { "source": "/services", "destination": "/services.html" },
    { "source": "/help", "destination": "/help.html" },
    { "source": "/tracking", "destination": "/tracking.html" },
    { "source": "/driver", "destination": "/driver.html" },
    { "source": "/legal", "destination": "/Legal.html" }
  ]
}
```

---

### 6. PWA SERVICE WORKER - VERSION CONTROL

**Update frontend sw.js:**
```javascript
const CACHE_VERSION = 'v1.0.0'; // Increment on each deployment
const CACHE_NAME = `routrix-${CACHE_VERSION}`;

self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Don't cache API calls
  if (event.request.url.includes('/api/') || event.request.url.includes('/booking') || event.request.url.includes('/career')) {
    return event.respondWith(fetch(event.request));
  }
  
  // Cache-first for static assets
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request).then((response) => {
        return caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, response.clone());
          return response;
        });
      });
    })
  );
});
```

---

### 7. API CONFIGURATION - SINGLE SOURCE OF TRUTH

**Ensure all HTML files load api-config.js in HEAD:**
```html
<!-- In all HTML files, add to <head> right after <meta> tags: -->
<script src="/static/js/api-config.js"></script>
```

**Files to update:**
- ✓ booking.html (already correct, uses BACKEND)
- ✗ career.html (FIX: hardcoded URLs)
- ✓ admin.html (FIX: add token validation)
- ✓ driver.html (already correct)
- ✓ tracking.html (already correct)

---

## DEPLOYMENT CHECKLIST

- [ ] Fix career.html URLs and move api-config.js to HEAD
- [ ] Add JWT validation to admin.html
- [ ] Implement LR conflict prevention in backend
- [ ] Add OTP cleanup scheduler in backend
- [ ] Update vercel.json with proper cache headers
- [ ] Update sw.js with version control
- [ ] Test booking form email
- [ ] Test career form email
- [ ] Test admin login & token expiry
- [ ] Clear browser cache & test in incognito
- [ ] Test PWA install & offline mode
- [ ] Monitor backend logs for errors

---

## EXPECTED RESULTS AFTER FIXES

✅ Booking & Career emails work consistently  
✅ Admin panel validates JWT on load  
✅ PWA works reliably on all devices  
✅ No more 404 cache issues  
✅ Database cleaned up automatically  
✅ No silent failures - all errors logged  
✅ Production ready for scaling

---

## MONITORING & LOGGING

**Add comprehensive logging to backend:**
```python
# Log all API calls
logger.info(f"[API] {request.method} {request.url} - Status: {response.status_code}")

# Log all emails
logger.info(f"[EMAIL] {subject} sent to {recipient}")

# Log all DB operations
logger.info(f"[DB] INSERT {table} - ID: {id}")
```

**Monitor error patterns:**
- SMTP failures
- JWT validation failures
- LR conflicts
- Cloudinary API errors

---

## NEXT STEPS

1. Implement all fixes above
2. Run comprehensive testing
3. Deploy to production
4. Monitor logs for 24 hours
5. Scale infrastructure if needed
