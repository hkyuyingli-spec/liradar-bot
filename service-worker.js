const CACHE_NAME = 'dennis-ai-cache-v1';
const urlsToCache = [
  '/',
  'https://cdn-icons-png.flaticon.com/512/1998/1998664.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
