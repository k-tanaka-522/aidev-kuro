from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn
from contextlib import asynccontextmanager

from app.config import settings
from app.api.v1 import projects, agents, messages, artifacts, auth
from app.utils.logger import configure_logging
from app.utils.middleware import PrometheusMiddleware, RateLimitMiddleware
from app.services.dynamodb import DynamoDBService


# Configure structured logging
configure_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AgentDev Platform API", version=settings.app_version)
    
    # Initialize services
    try:
        # Test DynamoDB connection
        dynamodb_service = DynamoDBService()
        await dynamodb_service.health_check()
        logger.info("DynamoDB connection established")
    except Exception as e:
        logger.error("Failed to connect to DynamoDB", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AgentDev Platform API")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-agent system development platform with Amazon Bedrock",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add custom middleware
if settings.enable_metrics:
    app.add_middleware(PrometheusMiddleware)

app.add_middleware(RateLimitMiddleware, calls=settings.rate_limit_per_minute, period=60)

# Include API routers
app.include_router(
    auth.router,
    prefix=f"{settings.api_v1_prefix}/auth",
    tags=["authentication"]
)

app.include_router(
    projects.router,
    prefix=f"{settings.api_v1_prefix}/projects",
    tags=["projects"]
)

app.include_router(
    agents.router,
    prefix=f"{settings.api_v1_prefix}/agents",
    tags=["agents"]
)

app.include_router(
    messages.router,
    prefix=f"{settings.api_v1_prefix}/messages",
    tags=["messages"]
)

app.include_router(
    artifacts.router,
    prefix=f"{settings.api_v1_prefix}/artifacts",
    tags=["artifacts"]
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check DynamoDB connection
        dynamodb_service = DynamoDBService()
        await dynamodb_service.health_check()
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {
                "dynamodb": "healthy",
                "api": "healthy"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_config=None  # Use our custom logging configuration
    )