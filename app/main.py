from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import chat, health, threads
import os

app = FastAPI(title="CamTech University Assistant")

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

# Serve widget.js and widget.css from frontend/
app.mount("/widget.js", StaticFiles(directory="frontend", html=False), name="widget_js")
app.mount(
    "/widget.css", StaticFiles(directory="frontend", html=False), name="widget_css"
)

# Serve mirrored site from frontend/mirrored_site/camtech.edu.kh
if os.path.exists("frontend/mirrored_site"):
    from fastapi.responses import RedirectResponse

    @app.get("/")
    def read_root_redirect():
        return RedirectResponse(url="/camtech.edu.kh/")

    app.mount(
        "/", StaticFiles(directory="frontend/mirrored_site", html=True), name="frontend"
    )
else:

    @app.get("/")
    def read_root():
        return {
            "status": "ok",
            "message": "Mirrored site not found. Please run wget to mirror the site.",
        }
