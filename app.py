import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse


from backend.database import init_db
from backend.seed import seed_database
from backend.routes import (
    dashboard, facilities, allocation, bookings,
    analytics, conflicts, simulation, settings, history
)

# Initialize database and seed if missing
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "campusflow.db")
if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
    print("Database not found. Initializing and seeding CampusFlow database...")
    seed_database()
else:
    init_db()

app = FastAPI(
    title="CampusFlow AI Engine API",
    description="Intelligent Resource Allocation System for Campus Facilities",
    version="1.0.0"
)

# Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(dashboard.router)
app.include_router(facilities.router)
app.include_router(allocation.router)
app.include_router(bookings.router)
app.include_router(analytics.router)
app.include_router(conflicts.router)
app.include_router(simulation.router)
app.include_router(settings.router)
app.include_router(history.router)

# Serve static frontend build if dist exists
dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")
if os.path.exists(dist_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api"):
            return JSONResponse(status_code=404, content={"detail": "API endpoint not found"})
        file_path = os.path.join(dist_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_dir, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "name": "CampusFlow AI API Server",
            "status": "running",
            "docs": "/docs",
            "version": "1.0.0"
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"Starting CampusFlow AI Server on http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
