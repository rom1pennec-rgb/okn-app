const CACHE_NAME = 'okn-app-v2';
const ASSETS = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png'];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Page HTML : toujours essayer le réseau d'abord (pour voir les mises à jour tout de suite),
  // le cache ne sert que de secours hors-ligne.
  if(event.request.mode === 'navigate' || event.request.destination === 'document'){
    event.respondWith(
      fetch(event.request)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          return res;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }
  // Reste des fichiers (icônes, manifest) : cache d'abord, réseau si absent.
  event.respondWith(
    caches.match(event.request).then((cached) => cached || fetch(event.request))
  );
});
