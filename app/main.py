from dotenv import load_dotenv

load_dotenv()  # Load .env into os.environ BEFORE any app imports

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import chat, health, threads
from app.memory.store import init_db
import os

app = FastAPI(title="CamTech University Assistant")


@app.on_event("startup")
def on_startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(threads.router, prefix="/api")

from fastapi.responses import FileResponse

@app.get("/widget.js")
def get_widget_js():
    return FileResponse("frontend/widget.js")

@app.get("/widget.css")
def get_widget_css():
    return FileResponse("frontend/widget.css")

import mimetypes
import urllib.parse
import requests
from fastapi.responses import RedirectResponse, Response, HTMLResponse

MIRROR_DIR = os.path.abspath("frontend/mirrored_site/camtech.edu.kh")

PUA_MAP = {
    '?': '\uf03f',
    '*': '\uf02a',
    ':': '\uf03a',
    '"': '\uf022',
    '<': '\uf03c',
    '>': '\uf03e',
    '|': '\uf07c',
}


def resolve_mirrored_path(rel_path: str):
    clean_path = urllib.parse.unquote(rel_path).lstrip("/\\")
    if not clean_path:
        clean_path = "index.html"

    # 1. Try standard path
    candidate = os.path.join(MIRROR_DIR, clean_path)
    try:
        if os.path.isfile(candidate):
            return candidate
        if os.path.isdir(candidate):
            idx = os.path.join(candidate, "index.html")
            if os.path.isfile(idx):
                return idx
    except OSError:
        pass

    # 2. Try Windows PUA character mapping (e.g. ? -> \uf03f)
    pua_path = clean_path
    for char, pua in PUA_MAP.items():
        pua_path = pua_path.replace(char, pua)

    candidate_pua = os.path.join(MIRROR_DIR, pua_path)
    try:
        if os.path.isfile(candidate_pua):
            return candidate_pua
    except OSError:
        pass

    return None


def fetch_and_cache_remote(rel_path: str):
    clean_path = urllib.parse.unquote(rel_path).lstrip("/\\")
    asset_exts = ('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.css', '.js', '.woff', '.woff2', '.ttf', '.eot', '.ico')
    if not clean_path.lower().endswith(asset_exts) and not clean_path.startswith(('wp-content', 'wp-includes')):
        return None

    remote_url = f"https://camtech.edu.kh/{clean_path}"
    try:
        resp = requests.get(remote_url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            local_file = os.path.join(MIRROR_DIR, clean_path)
            os.makedirs(os.path.dirname(local_file), exist_ok=True)
            with open(local_file, "wb") as f:
                f.write(resp.content)
            return local_file
    except Exception:
        pass
    return None


@app.get("/camtech.edu.kh/{full_path:path}")
def redirect_camtech_prefix(full_path: str):
    return RedirectResponse(url=f"/{full_path}")


@app.get("/{full_path:path}")
def serve_mirrored_site(full_path: str = ""):
    local_path = resolve_mirrored_path(full_path)

    if not local_path:
        local_path = fetch_and_cache_remote(full_path)

    if local_path and os.path.isfile(local_path):
        mime, _ = mimetypes.guess_type(local_path)

        # For HTML pages, ensure widget is injected
        if mime == "text/html" or local_path.endswith((".html", ".htm")):
            with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if "/widget.js" not in content:
                widget_tag = '\n<!-- CamTech Assistant Widget -->\n<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>\n<link rel="stylesheet" href="/widget.css?v=10">\n<script src="/widget.js?v=10"></script>\n</body>'
                content = content.replace("</body>", widget_tag)
            return HTMLResponse(content)

        return FileResponse(local_path, media_type=mime)

    # Fallback to root index if not found
    root_index = os.path.join(MIRROR_DIR, "index.html")
    if os.path.isfile(root_index):
        return FileResponse(root_index, media_type="text/html")

    return Response(status_code=404)

