/**
 * ROUTRIX Frontend API Configuration
 * This file centralizes all backend API calls
 * 
 * Usage: Import this in your HTML files and use the functions
 * Example: <script src="static/js/api-config.js"></script>
 */

// ===== API CONFIGURATION =====;

// ===== ROUTRIX FINAL API CONFIG (STABLE) =====

const API_BASE_URL = "https://routrix.onrender.com";
const BACKEND = API_BASE_URL;

console.log("[API] Using backend URL:", BACKEND);



// ===== HELPER: Make API Calls =====
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
        ...options.headers
      },
      ...options
    });

    // Check if response is OK
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || error.error || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`[API Error] ${endpoint}:`, error.message);
    throw error;
  }
}

// ===== API ENDPOINTS =====

// 1. TRACKING
async function trackShipment(lr) {
  return fetchAPI(`/track/${lr}`, { method: "GET" });
}

// 2. LIVE LOCATION UPDATE (Driver)
async function updateLocation(lr, lat, lng, driverName, vehicleNo, mobile) {
  return fetchAPI("/update-location", {
    method: "POST",
    body: JSON.stringify({
      lr, lat, lng, driver_name: driverName, vehicle_no: vehicleNo, mobile
    })
  });
}

// 3. BANNERS
async function getBanners() {
  return fetchAPI("/banners", { method: "GET" });
}

// 4. DRIVER LOGIN
async function driverLogin(password) {
  return fetchAPI("/driver-login", {
    method: "POST",
    body: JSON.stringify({ password })
  });
}

// 5. ADMIN LOGIN
async function adminLogin(password) {
  return fetchAPI("/admin/login", {
    method: "POST",
    body: JSON.stringify({ password })
  });
}

// 6. ADMIN: GET LIVE TRUCKS
async function getLiveTrucks(adminToken) {
  return fetchAPI("/admin/live-trucks", {
    method: "GET",
    headers: { "Authorization": `Bearer ${adminToken}` }
  });
}

// 7. ADMIN: UPLOAD BANNER
async function uploadBanner(file, adminToken) {
  const formData = new FormData();
  formData.append("file", file);

  return fetch(`${API_BASE_URL}/admin/upload-banner`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${adminToken}` },
    body: formData
  }).then(res => res.json());
}

// 8. ADMIN: DELETE BANNER
async function deleteBanner(filename, adminToken) {
  return fetchAPI(`/admin/delete-banner/${filename}`, {
    method: "DELETE",
    headers: { "Authorization": `Bearer ${adminToken}` }
  });
}

// 9. ADMIN: GENERATE OTP
async function generateOTP(lr, adminToken) {
  return fetchAPI(`/admin/generate-otp/${lr}`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${adminToken}` }
  });
}

// 10. VERIFY OTP
async function verifyOTP(lr, otp) {
  return fetchAPI("/verify-otp", {
    method: "POST",
    body: JSON.stringify({ lr, otp })
  });
}

// 11. SUBMIT POD (Proof of Delivery)
async function submitPOD(lr, receiverName, file) {
  const formData = new FormData();
  formData.append("lr", lr);
  formData.append("receiver_name", receiverName);
  formData.append("image", file);

  return fetch(`${API_BASE_URL}/submit-pod`, {
    method: "POST",
    body: formData
  }).then(res => res.json());
}

// 12. HEALTH CHECK
async function checkBackendHealth() {
  return fetchAPI("/api", { method: "GET" });
}

// ===== LOCAL STORAGE HELPERS =====

// Store authentication token
function setAuthToken(token, role = "admin") {
  localStorage.setItem(`${role}_token`, token);
}

// Get authentication token
function getAuthToken(role = "admin") {
  return localStorage.getItem(`${role}_token`);
}

// Clear authentication token
function clearAuthToken(role = "admin") {
  localStorage.removeItem(`${role}_token`);
}

// ===== ERROR HANDLER =====
function handleAPIError(error) {
  console.error("API Error:", error.message);
  alert(`Error: ${error.message}`);
}

// Export for use (if using modules)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    API_BASE_URL,
    fetchAPI,
    trackShipment,
    updateLocation,
    getBanners,
    driverLogin,
    adminLogin,
    getLiveTrucks,
    uploadBanner,
    deleteBanner,
    generateOTP,
    verifyOTP,
    submitPOD,
    checkBackendHealth,
    setAuthToken,
    getAuthToken,
    clearAuthToken,
    handleAPIError
  };
}
