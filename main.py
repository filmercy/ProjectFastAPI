"""Tennis Shop Management System - FastAPI Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, clients, categories, products, client_rackets, maintenance

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="A management system for tennis shop stringing services",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Tennis Shop Management System API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(clients.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(products.router, prefix=settings.API_V1_PREFIX)
app.include_router(client_rackets.router, prefix=settings.API_V1_PREFIX)
app.include_router(maintenance.router, prefix=settings.API_V1_PREFIX)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    print(f"*** {settings.APP_NAME} v{settings.APP_VERSION} started! ***")
    print(f"API documentation: http://localhost:8000/docs")
    print(f"Database: SQLite (tennis_shop.db)")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    print(f"{settings.APP_NAME} shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
