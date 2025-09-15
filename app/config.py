import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Configuración de la aplicación"""
    
    # Información de la aplicación
    APP_NAME: str = "Azure Foundry Backend API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API REST para gestión de agentes de IA con Azure Foundry"
    
    # Configuración del servidor
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Configuración de Azure AI
    AZURE_AI_ENDPOINT: str = os.getenv("AZURE_AI_ENDPOINT", "")
    
    # Configuración de base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Configuración de CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Configuración de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

# Instancia global de configuración
settings = Settings()
