const BLOCKED_DOMAINS = [
    'gamemonetize.com',
    'gamedistribution.com',
    'cpmstar.com',
    'mochiads.com',
    'imasdk.googleapis.com',   // Google IMA video ad SDK (inside games, not AdSense)
    'adinplay.com',
    'cdn.cpx.to',
    'vidazoo.com',
    'adnxs.com',               // AppNexus / Xandr
    'rubiconproject.com',
    'pubmatic.com',
    'openx.net',
    'adsafeprotected.com',
    'smartadserver.com',
    'criteo.com',
    'taboola.com',
    'outbrain.com',
];

self.addEventListener('fetch', function (event) {
    try {
        var host = new URL(event.request.url).hostname;
        if (BLOCKED_DOMAINS.some(function (d) { return host.indexOf(d) !== -1; })) {
            event.respondWith(new Response('', { status: 200 }));
            return;
        }
    } catch (e) {}
});
