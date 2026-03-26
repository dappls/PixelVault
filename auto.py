import os
import json
import re
import aiohttp
import asyncio
from aiohttp import ClientSession

TEMPLATE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="icon" type="image/png" href="../../images/favicon.png">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Play {GAME_NAME} | PixelVault</title>
    <meta name="description" content="Play {GAME_NAME} unblocked on PixelVault. No downloads required.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://dappls.github.io/games/{GAME_SLUG}/">
    <meta property="og:title" content="Play {GAME_NAME} | PixelVault">
    <meta property="og:description" content="Play {GAME_NAME} unblocked on PixelVault. No downloads required.">
    <meta property="og:image" content="{GAME_COVER}">
    <meta name="google-adsense-account" content="ca-pub-3633320799834823">
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-NEGSCDQJH1"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag() { dataLayer.push(arguments); }
        gtag('js', new Date());
        gtag('config', 'G-NEGSCDQJH1');
    </script>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3633320799834823" crossorigin="anonymous"></script>
    <link rel="stylesheet" href="../../styles/style.css">
</head>
<body class="dark-mode">
    <header>
        <div class="header-content">
            <a class="logo" href="../../" style="text-decoration: none; color: inherit;">PixelVault</a>
            <div class="control-buttons">
                <button id="settings">Settings</button>
            </div>
        </div>
    </header>

    <main class="game-container">
        <h1 class="game-title">{GAME_NAME}</h1>
        <div class="game-frame-container">
            <iframe class="game-frame" id="gameFrame" allowfullscreen sandbox="allow-scripts allow-same-origin allow-forms allow-pointer-lock allow-orientation-lock allow-downloads"></iframe>
            <button class="fullscreen-btn" onclick="document.getElementById('gameFrame').requestFullscreen()">Fullscreen</button>
            <button class="newtab-btn" onclick="window.open(new URL('../../iframe/{PATHNAME}', window.location.href).href, '_blank')">New Tab</button>
        </div>
    </main>


    <div id="popupOverlay">
        <div class="popup">
            <div class="popup-header">
                <h3 id="popupTitle">Title</h3>
                <button id="popupClose" onclick="closePopup()">×</button>
            </div>
            <div id="popupBody"></div>
        </div>
    </div>

    <footer>
        <div class="footer-links">
            <a href="#" onclick="showContact(); return false;">Contact</a>
            <a href="#" onclick="loadPrivacy(); return false;">Privacy Policy</a>
        </div>
    </footer>

    <script>
        document.getElementById("gameFrame").src = "../../iframe/{PATHNAME}";
    </script>
    <script src="../../javascript/index.js"></script>
    <script src="../../javascript/game-ads.js"></script>
</body>
</html>
"""

sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://dappls.github.io/</loc>
  </url>
"""

async def fetch_json(session: ClientSession, url: str) -> dict:
    async with session.get(url) as response:
        return await response.json()

async def fetch_text(session: ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()

# Iframe files that have been manually fixed and must not be overwritten from CDN
PROTECTED_IFRAMES = {
    '66.html',  # Basket Random — removed obfuscated ad injector (api.js)
}

async def process_game(session: ClientSession, game: dict, OUTPUT_DIR: str, GAME_DIR: str) -> str:
    game_id = str(game['id'])
    if game_id == '-1':
        return None

    game_name = game['name']
    game_cover = game['cover'].replace("{COVER_URL}", "https://cdn.jsdelivr.net/gh/gn-math/covers@main")
    pathname = game['url'].split('/')[1]
    game_slug = re.sub(r'[^a-zA-Z0-9-]', '', game_name.replace(' ', '-').lower()).replace('--', '-')

    game_folder = os.path.join(OUTPUT_DIR, game_slug)
    os.makedirs(game_folder, exist_ok=True)
    os.makedirs(GAME_DIR, exist_ok=True)

    html_content = TEMPLATE_HTML \
        .replace('{GAME_NAME}', game_name) \
        .replace('{GAME_SLUG}', game_slug) \
        .replace('{GAME_COVER}', game_cover) \
        .replace('{PATHNAME}', pathname)

    game_file_path = os.path.join(GAME_DIR, pathname)
    if pathname not in PROTECTED_IFRAMES:
        game_url = f'https://cdn.jsdelivr.net/gh/gn-math/html@main/{pathname}'
        game_html = await fetch_text(session, game_url)
        with open(game_file_path, 'w', encoding='utf-8') as f:
            f.write(game_html)
    else:
        print(f"Skipping protected iframe: {pathname}")

    index_path = os.path.join(OUTPUT_DIR, game_slug, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    global sitemap
    sitemap += f"  <url>\n    <loc>https://dappls.github.io/games/{game_slug}/</loc>\n  </url>\n"
    print(f"Made {index_path}")
    return game_file_path

async def main():
    OUTPUT_DIR = 'games'
    GAME_DIR = 'iframe'

    async with ClientSession() as session:
        hash_response = await fetch_json(session, "https://api.github.com/repos/gn-math/assets/commits")
        latest_hash = hash_response[0]['sha']
        print(f"Latest hash: {latest_hash}")

        zones_url = f'https://cdn.jsdelivr.net/gh/gn-math/assets@{latest_hash}/zones.json'
        games = await fetch_json(session, zones_url)
        print(f"Loaded {len(games)} zones")

        tasks = [process_game(session, game, OUTPUT_DIR, GAME_DIR) for game in games]
        game_paths = [p for p in await asyncio.gather(*tasks) if p is not None]

        with open('games.json', 'w', encoding='utf-8') as f:
            json.dump(game_paths, f, indent=4)
        print("games.json done")

        global sitemap
        sitemap += "</urlset>"
        with open('sitemap.xml', 'w', encoding='utf-8') as f:
            f.write(sitemap)
        print("sitemap.xml done")

    print("Done")

if __name__ == '__main__':
    asyncio.run(main())
