import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import create_tables
from app.config import settings

if __name__ == "__main__":
    print("Creando tablas de base de datos...")
    print(f"Base de datos: {settings.DATABASE_URL}")
    create_tables()
    print("¡Tablas creadas exitosamente!")
