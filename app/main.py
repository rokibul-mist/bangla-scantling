import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.templating import Jinja2Templates
from app.api.v1 import api_router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure static files and data are accessible
    yield
    # Shutdown logic if needed

app = FastAPI(
    title="Bangladesh Naval Architecture Scantling System",
    description="Statutory structural scantlings and lightship estimation per Bangladesh Inland Shipping Rules 2001 & SRO 308",
    version="2.0.0",
    lifespan=lifespan
)
 
# Enable CORS for cross-origin integration and dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP middleware to disable caching on HTML, JS, CSS for live development
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path == "/" or path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Mount static directory
static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount Jinja2 templates directory
templates_dir = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)

# Include modular API routers
app.include_router(api_router, prefix="/api")
app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    """
    Renders the modular UI from templates with no-cache headers.
    """
    try:
        response = templates.TemplateResponse(request, "index.html", context={})
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        print(f"Template rendering error: {e}")
        # Fallback to pre-rendered static index.html if templates fail
        index_file = os.path.join(BASE_DIR, "static", "index.html")
        if os.path.exists(index_file):
            with open(index_file, "r", encoding="utf-8") as f:
                return HTMLResponse(
                    content=f.read(),
                    headers={
                        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
                        "Pragma": "no-cache",
                        "Expires": "0"
                    }
                )
        return HTMLResponse(content="<h1>Bangla Scantling System Initializing...</h1>")

@app.get("/favicon.ico")
async def favicon():
    icon_path = os.path.join(BASE_DIR, "static", "favicon.ico")
    if os.path.exists(icon_path):
        return FileResponse(icon_path)
    return Response(status_code=204)
