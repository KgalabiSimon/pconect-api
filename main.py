from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, users, profile
from app.api.routes import building, programme, verify_qr
from app.api.routes import auth, users, profile, building, checkin,spaces
from app.api.routes import amenity, booking, employees, visitor
from sqlalchemy.orm import Session
from app.db.database import get_db

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="P-Connect API - Employee and Visitor Management System"
)

# Include routers with tags
app.include_router(
    auth.router,
    tags=["Authentication"]
)
app.include_router(
    users.router,
    tags=["Users"]
)

app.include_router(
    profile.router,
    tags=["Profile"]
)

# Register building management router
app.include_router(
    building.router,
    tags=["Buildings"]
)

# Register programme router
app.include_router(
    programme.router,
    tags=["Programmes"]
)

# Include check-in router
app.include_router(
    checkin.router,
    tags=["Check-In"]
)

# Register QR verification router
app.include_router(
    verify_qr.router,
    tags=["QR Verification"]
)

# Register spaces router
app.include_router(
    spaces.router,
    tags=["Spaces"]
)

# Register amenities router
app.include_router(
    amenity.router,
    tags=["Amenities"]
)

# Register booking router
app.include_router(
    booking.router,
    tags=["Booking"]
)

# Register employees router
app.include_router(
    employees.router,
    tags=["Employees"]
)

# Register visitor router
app.include_router(
    visitor.router,
    tags=["Visitors"]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to P-Connect API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}

@app.get("/db-test")
async def test_db(db: Session = Depends(get_db)):
    """Test database connection"""
    try:
        from sqlalchemy import text
        # Try to execute a simple query using proper SQLAlchemy text()
        result = db.execute(text("SELECT 1"))
        result.scalar()  # Actually fetch the result
        return {"status": "Database connection successful"}
    except Exception as e:
        return {"status": "Database connection failed", "error": str(e)}
