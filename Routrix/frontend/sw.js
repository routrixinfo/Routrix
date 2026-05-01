const CACHE_NAME = "routrix-v1";

const urlsToCache = [
  "/",
  "/driver.html",
  "/services.html",
  "/tracking.html",
  "/assets/routrixlogo.png"
];

// INSTALL → cache files
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log("Caching files...");
      return cache.addAll(urlsToCache);
    })
  );
});

// ACTIVATE → clean old cache
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
});

// FETCH → use network-first for dynamic requests, cache static files
self.addEventListener("fetch", event => {
  const requestUrl = new URL(event.request.url);
  const apiPaths = ["/api", "/admin", "/track", "/update-location", "/verify-otp", "/submit-pod", "/booking", "/career", "/banners"];
  const isApiRequest = apiPaths.some(path => requestUrl.pathname.startsWith(path));

  if (event.request.method !== "GET" || isApiRequest) {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request).then(networkResponse => {
        return caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, networkResponse.clone());
          return networkResponse;
        });
      });
    })
  );
});