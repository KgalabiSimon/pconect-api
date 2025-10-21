from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Starter", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Hello World endpoint"""
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

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
