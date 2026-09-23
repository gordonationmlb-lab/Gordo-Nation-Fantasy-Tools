const CACHE = 'gordo-calc-v88-2026-09-13-v51.15';
const SHELL = [
  './', 'index.html', 'mobile.html', 'manifest.json',
  'icon-192.png', 'icon-512.png', 'icon-512-maskable.png', 'apple-touch-icon.png',
  // v50.22 moved every inline <script> out of the two pages so the CSP could drop
  // 'unsafe-inline'. The pages went from 6.4 MB each to ~114 KB and these carry the
  // difference, so the offline shell is incomplete without them. gn-app.js is the
  // 6.2 MB one: it holds PLAYERS/GNDAILY/GNROS/HISTORY/OPTIONS_DATA and all the logic,
  // and it is now shared by both pages instead of duplicated into each.
  'gn-boot.js', 'gn-install-tip.js', 'gn-buildlink.js', 'gn-app.js', 'gn-sw-register.js',
  'gn-detail-v45.js', 'gn-timeview.js', 'gn-ros-v46.js', 'gn-a11y-keys.js', 'gn-build-stamp.js'
];

self.addEventListener('install', (e) => {
  // Precache entry by entry, not with one addAll. addAll is all-or-nothing across all 18
  // entries, so a deploy that dropped a single file left the cache created and EMPTY and the
  // worker never activated at all — measured, with register() still resolving and nothing in
  // the console naming the cause. A worker holding 17 of 18 files is strictly better than no
  // worker, so note what is missing, say so once, and activate anyway. 'reload' skips the HTTP
  // cache here: a precache that stores what the browser already had defeats the point.
  e.waitUntil(
    caches.open(CACHE).then((c) => {
      const missed = [];
      return Promise.all(SHELL.map((u) =>
        fetch(new Request(u, { cache: 'reload' }))
          .then((res) => {
            if (!res.ok) throw new Error('HTTP ' + res.status);
            return c.put(u, res);
          })
          .catch((err) => { missed.push(u + ' (' + ((err && err.message) || 'failed') + ')'); })
      )).then(() => {
        if (missed.length && self.console && console.warn) {
          console.warn('[gordo-calc] precache incomplete: ' + missed.length + ' of ' +
            SHELL.length + ' missing — ' + missed.join(', ') +
            '. Offline will be partial. Check the deploy uploaded every file.');
        }
        return self.skipWaiting();
      });
    })
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
  if (url.origin !== location.origin) return; // Chart.js + Google Fonts load straight from CDN

  // One place decides what gets stored, so the two branches below cannot drift apart.
  //  - the res.ok gate: without it a 404 was written straight into the cache and served back
  //    offline. Measured: two bad requests took the store from 18 entries to 20, both 404s.
  //    Under cache-first that is permanent, because a cached entry is never re-fetched.
  //  - clone AFTER the gate: an error response is no longer copied at all, and a 6.2 MB
  //    gn-app.js is not duplicated in memory for a response we were about to throw away.
  //  - waitUntil, not a bare .then: this write used to be a floating promise. Nothing consumed
  //    its rejection (QuotaExceededError is real at 6.2 MB on a phone) and nothing kept the
  //    worker alive to finish it, so the copy network-first exists to maintain could silently
  //    never land. waitUntil both holds the worker open and gives the rejection an owner.
  const keep = (res) => {
    if (!res || !res.ok) return res;
    const copy = res.clone();
    e.waitUntil(
      caches.open(CACHE).then((c) => c.put(req, copy)).catch((err) => {
        if (self.console && console.warn) {
          console.warn('[gordo-calc] could not cache ' + url.pathname + ':', err);
        }
      })
    );
    return res;
  };

  const isPage = req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html');
  // Our own scripts take the page's freshness rule, not the icon rule. Until v50.22 the
  // data and the logic sat inline in the page, so network-first covered them and a build
  // that changed only code or only numbers needed no cache bump. Externalising them would
  // have quietly moved all of that under cache-first, pinning a returning visitor to a
  // stale PLAYERS blob until the cache name happened to change. fetch() still revalidates
  // against the HTTP cache, so an unchanged gn-app.js answers 304 with no body.
  const isCode = url.pathname.endsWith('.js');
  if (isPage || isCode) {
    // network-first so a new build always wins; fall back to cache offline
    e.respondWith(
      fetch(req).then(keep).catch(() => caches.match(req).then(
        (r) => r || (isPage ? caches.match('index.html') : Response.error())))
    );
  } else {
    // cache-first for icons/manifest/static
    e.respondWith(
      caches.match(req).then((r) => r || fetch(req).then(keep))
    );
  }
});
