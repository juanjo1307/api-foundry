"""
Script de inicio para el servidor FastAPI
Uso: python run.py
"""
import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

if __name__ == "__main__":
    # Configuración del servidor
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Auto-reload en desarrollo
        log_level="info",
        access_log=True
    )
