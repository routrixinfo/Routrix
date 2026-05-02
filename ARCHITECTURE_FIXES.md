# ROUTRIX Production Architecture - Comprehensive Fixes

## ISSUES IDENTIFIED

### 1. **SMTP INCONSISTENCY** ✓ FOUND ROOT CAUSE
- Career form: Hardcoded URL `https://routrix.onrender.com/career` 
- Booking form: Uses `BACKEND` variable correctly
- **Fix:** Replace hardcoded URLs with `BACKEND` variable in career.html

### 2. **FRONTEND-BACKEND CONNECTION** 
- api-config.js loads correctly but:
  - Some forms bypass it (career.html action attribute)
  - Need to ensure BACKEND is loaded before any form submission
  
### 3. **ADMIN JWT VALIDATION**
- admin.html doesn't validate token on page load
- Expired tokens not detected until first API call fails
- **Fix:** Add JWT validation check on page load, auto-logout if expired

### 4. **DRIVER LR CONFLICTS**
- Same LR can be used by multiple drivers
- LiveLocation table uses `lr` as primary key (only 1 value allowed)
- **Need:** Check for LR ownership or warn about overwrites

### 5. **DATABASE CLEANUP**
- OTP records never expire from DB
- Completed trips never reset
- **Need:** Add background task to cleanup old records

### 6. **CLOUDINARY INTEGRATION**
- Backend fixes already implemented in previous commits
- Need to verify banners upload/delete works globally

### 7. **CACHE & BROWSER ISSUES**
- Works in incognito (no cache)
- Fails in normal mode (cached responses)
- **Fix:** Add proper cache-control headers + cache-busting

### 8. **PWA CONFIGURATION**
- manifest.json exists but may not be optimal
- Service worker may be caching old files
- **Fix:** Proper PWA setup with version control

---

## ACTION PLAN

### Phase 1: CRITICAL FIXES (SMTP)
1. [ ] Replace hardcoded URLs in career.html with BACKEND variable
2. [ ] Ensure api-config.js loads first in all HTML files
3. [ ] Test booking and career form submissions

### Phase 2: AUTH & VALIDATION
4. [ ] Add JWT validation to admin.html on page load
5. [ ] Add auto-logout on token expiry
6. [ ] Add error handling for auth failures

### Phase 3: DATABASE & CLEANUP
7. [ ] Add database cleanup tasks (OTP expiry, trip reset)
8. [ ] Add LR ownership validation or warning
9. [ ] Verify Cloudinary integration

### Phase 4: CACHING & PWA
10. [ ] Add cache-busting for all API calls
11. [ ] Update manifest.json
12. [ ] Update service worker version handling

---

## FILES TO MODIFY

**Frontend:**
- Routrix/frontend/career.html - Replace hardcoded URLs
- Routrix/frontend/admin.html - Add JWT validation
- Routrix/frontend/manifest.json - Verify/update PWA config
- Routrix/frontend/sw.js - Update cache versioning

**Backend:**
- Routrix/backend/main.py - Add cleanup tasks, LR validation

---

## EXPECTED OUTCOMES

✅ Booking & Career emails work consistently
✅ Admin panel validates JWT on load
✅ PWA works reliably on all devices  
✅ No more 404 cache issues
✅ Database cleaned up automatically
✅ No silent failures - all errors logged
