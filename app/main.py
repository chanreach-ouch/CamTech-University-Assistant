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

# Serve mirrored site from frontend/mirrored_site/camtech.edu.kh
if os.path.exists("frontend/mirrored_site/camtech.edu.kh"):
    from fastapi.responses import RedirectResponse
    
    @app.get("/camtech.edu.kh/")
    def redirect_old_path():
        return RedirectResponse(url="/")
        
    @app.get("/camtech.edu.kh")
    def redirect_old_path_no_slash():
        return RedirectResponse(url="/")

    app.mount(
        "/", StaticFiles(directory="frontend/mirrored_site/camtech.edu.kh", html=True), name="frontend"
    )
else:

    @app.get("/")
    def read_root():
        return {
            "status": "ok",
            "message": "Mirrored site not found. Please run wget to mirror the site.",
        }
