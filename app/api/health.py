from fastapi import APIRouter
from app.config import settings
import platform
import sys
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """Health check detallado con información del sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "azure-foundry-backend",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "python_version": sys.version,
        "platform": platform.platform(),
        "azure_endpoint_configured": bool(settings.AZURE_AI_ENDPOINT),
    }
