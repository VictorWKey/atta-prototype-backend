from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os

from database import engine, get_db
from models import Base
from routers import auth, users, clients, equipment, service_reports
from core.config import settings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ATTA MONTACARGAS API",
    description="API para gestión de reportes de servicio de ATTA MONTACARGAS",
    version="1.0.0",
)

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

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(equipment.router, prefix="/api/equipment", tags=["Equipment"])
app.include_router(service_reports.router, prefix="/api/service-reports", tags=["Service Reports"])

@app.get("/")
async def root():
    return {
        "message": "ATTA MONTACARGAS API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Database connection failed")
