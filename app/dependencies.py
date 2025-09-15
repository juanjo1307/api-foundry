from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from app.config import settings
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Cliente de Azure AI (singleton)
_azure_client = None

def get_azure_client() -> AIProjectClient:
    global _azure_client
    
    if _azure_client is None:
        try:
            # Verificar configuración
            if not settings.AZURE_AI_ENDPOINT:
                raise ValueError("AZURE_AI_ENDPOINT no está configurado")
           
           # Crear cliente
            _azure_client = AIProjectClient(
                endpoint=settings.AZURE_AI_ENDPOINT,
                credential=DefaultAzureCredential()
            )
            
            logger.info("Cliente de Azure AI inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error al inicializar cliente de Azure AI: {e}")
            raise
    
    return _azure_client

