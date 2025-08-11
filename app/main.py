from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
import os

from database import engine, get_db
from models import Base
from routers import auth, users, clients, equipment, service_reports
from core.config import settings

app = FastAPI(
    title="ATTA MONTACARGAS API",
    description="API para gestión de reportes de servicio de ATTA MONTACARGAS",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event():
    """Create database tables on startup."""
    try:
        # Only create tables if database is available
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created/verified")
    except OperationalError as e:
        print(f"Warning: Could not create tables: {e}")
        # Don't fail startup - tables might be created by init script

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
os.makedirs("/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="/uploads"), name="uploads")

# Import routers
from routers import auth, users, clients, equipment, service_reports, inspection_catalog

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(equipment.router, prefix="/api/equipment", tags=["Equipment"])
app.include_router(service_reports.router, prefix="/api/service-reports", tags=["Service Reports"])
app.include_router(inspection_catalog.router, prefix="/api/inspection", tags=["Inspection Catalog"])

@app.get("/")
async def root():
    return {
        "message": "ATTA MONTACARGAS API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/test-mobile")
async def test_mobile_endpoint(request: Request):
    """Simple test endpoint for mobile debugging"""
    return {
        "success": True,
        "message": "Mobile connection successful",
        "timestamp": str(request.headers.get("date", "no-date")),
        "user_agent": request.headers.get("user-agent", "unknown"),
        "client_ip": request.client.host if request.client else "unknown",
        "headers": dict(request.headers),
        "method": request.method,
        "url": str(request.url)
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection with SQLAlchemy 2.0 syntax
        from sqlalchemy import text
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")
