# Azure Foundry Backend API

API REST para gestión de agentes de IA con Azure Foundry, construida con FastAPI y Python.

## 🚀 Características

- **Gestión de Agentes IA**: Crear, listar, obtener, actualizar y eliminar agentes
- **Sistema de Chat**: Threads de conversación con mensajes y ejecución de agentes
- **Gestión de Archivos**: Subida de archivos con vectorización automática y asociación RAG
- **Base de Datos**: Almacenamiento local de agentes con MySQL
- **API REST**: Endpoints completos con documentación automática
- **Autenticación Azure**: Integración con Azure Foundry usando Azure CLI

## 📋 Prerrequisitos

### 1. Azure Foundry CLI (este proyecto usa la version 2.77.0)
```bash
# Instalar Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# o en terminal linux
sudo apt-get update
sudo apt-get install ca-certificates curl apt-transport-https lsb-release gnupg
curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null
AZ_REPO=$(lsb_release -cs)
echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | sudo tee /etc/apt/sources.list.d/azure-cli.list
sudo apt-get update
sudo apt-get install azure-cli

# usando Homebrew (macOS)
brew install azure-cli

# en windows usando PowerShell
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows | Invoke-Expression

# Verificar instalación
az --version
```

### 2. Python 3.8+
```bash
# Verificar versión de Python
python3 --version
```

### 3. MySQL
```bash
# Instalar MySQL
# Ubuntu/Debian
sudo apt-get install mysql-server

# macOS
brew install mysql

# Iniciar servicio
sudo systemctl start mysql  # Linux
brew services start mysql   # macOS
```

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd azure-foundry-backend
```

### 2. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Azure Foundry
```bash
# Login en Azure
az login

# Configurar variables de entorno
cp .env.example .env
```

### 5. Configurar variables de entorno

### 6. Inicializar base de datos
```bash
python scripts/init_db.py
```

## 🚀 Uso

### Iniciar el servidor
```bash
# Opción 1: Usando el script run.py
python run.py

# Opción 2: Usando uvicorn directamente
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Acceder a la documentación
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 🔧 Ejemplos de Uso

### 1. Crear un agente
```bash
curl -X POST "http://127.0.0.1:8000/agents/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mi Asistente IA",
    "model": "gpt-4o",
    "instructions": "Eres un asistente útil que responde preguntas sobre Azure Foundry"
  }'
```

### 2. Crear un thread
```bash
curl -X POST "http://127.0.0.1:8000/threads/"
```

### 3. Enviar un mensaje
```bash
curl -X POST "http://127.0.0.1:8000/chats/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "thread_abc123",
    "role": "user",
    "content": "Hola, ¿cómo estás?"
  }'
```

### 4. Subir archivo con RAG
```bash
curl -X POST "http://127.0.0.1:8000/files/upload" \
  -F "file=@documento.pdf" \
  -F "agent_id=asst_xyz789"
```

## 🏗️ Estructura del Proyecto

```
azure-foundry-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # Aplicación principal FastAPI
│   ├── config.py              # Configuración y variables de entorno
│   ├── database.py            # Configuración de base de datos
│   ├── dependencies.py        # Dependencias compartidas (Azure client)
│   ├── models.py              # Modelos de base de datos
│   └── api/
│       ├── __init__.py
│       ├── health.py          # Endpoints de health check
│       ├── agents.py          # Gestión de agentes IA
│       ├── threads.py         # Gestión de conversaciones
│       ├── files.py           # Gestión de archivos con RAG
│       └── chats.py           # Chat y mensajes
├── scripts/
│   └── init_db.py            # Script de inicialización de BD
├── venv/                     # Entorno virtual Python
├── run.py                    # Script de inicio
├── requirements.txt          # Dependencias Python
├── .env.example              # Variables de entorno de ejemplo
├── .gitignore                # Archivos ignorados por Git
└── README.md                 # Este archivo
```

## 🔐 Configuración de Azure Foundry

### 1. Crear proyecto en Azure Foundry
1. Ir a [Azure Foundry Portal](https://ai.azure.com/)
2. Crear un nuevo proyecto
3. Obtener el endpoint y las credenciales

### 2. Configurar autenticación
```bash
# Login en Azure
az login

# Configurar credenciales (opcional)
az account set --subscription "tu-subscription-id"
```

## 🐛 Solución de Problemas

### Error de autenticación Azure
```bash
# Verificar login
az account show

# Re-login si es necesario
az login
```


## 📝 Desarrollo

### Agregar nuevos endpoints
1. Crear archivo en `app/api/`
2. Importar en `app/main.py`
3. Agregar router con `app.include_router()`

### Agregar nuevos modelos de BD
1. Definir modelo en `app/models.py`
2. Ejecutar migración: `python scripts/init_db.py`

### Testing
```bash
# =( pendiente....
pytest

# Coverage
pytest --cov=app
```

- **Email**: juan_jose_flores@hotmail.com
- **Linkedin**: https://www.linkedin.com/in/juan-jose-flores/

---

**Desarrollado con ❤️ usando FastAPI y Azure Foundry**
