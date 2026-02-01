"""
Main FastAPI application for Astronomy API
"""
from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="Astronomy API",
    description="API for astronomical calculations including day of week, sun/moon positions, and more",
    version="0.1.0"
)

# Include the routes
app.include_router(router, prefix="/api/v1", tags=["astronomy"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Astronomy API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "ok"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
