const CACHE = 'gordo-calc-v58-2026-08-22';
const SHELL = [
  './', 'index.html', 'manifest.json',
  'icon-192.png', 'icon-512.png', 'icon-512-maskable.png', 'apple-touch-icon.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) {
    // v50.4: cache the Chart.js CDN bundle so installed copies render charts offline
    if (url.hostname === 'cdnjs.cloudflare.com' && url.pathname.indexOf('chart') !== -1) {
      e.respondWith(
        caches.match(req).then((r) => r || fetch(req).then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
          return res;
        }))
      );
    }
    return; // other cross-origin (Google Fonts) stays network-direct
  }

  const isPage = req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html');
  if (isPage) {
    // network-first so a new build always wins; fall back to cache offline
    e.respondWith(
      fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
        return res;
      }).catch(() => caches.match(req).then((r) => r || caches.match('index.html')))
    );
  } else {
    // cache-first for icons/manifest/static
    e.respondWith(
      caches.match(req).then((r) => r || fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
        return res;
      }))
    );
  }
});
