from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.dependencies import get_azure_client
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FileSearchToolDefinition, ToolResources, FileSearchToolResource
import time
import io

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/")
async def list_files(azure_client: AIProjectClient = Depends(get_azure_client)):
    """Listar todos los archivos"""
    try:
        # Obtener lista de archivos desde Azure Foundry
        files = azure_client.agents.files.list()
        
        # Convertir a lista para serialización
        files_list = []
        for file in files.data:
            files_list.append({
                "id": file.id,
                "object": file.object,
                "created_at": file.created_at,
                "filename": file.filename,
                "purpose": file.purpose,
                "bytes": file.bytes
            })
        
        return {
            "success": True,
            "count": len(files_list),
            "files": files_list
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar archivos: {str(e)}"
        )

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    agent_id: str = Form(...),
    azure_client: AIProjectClient = Depends(get_azure_client)
):
    """Subir archivo y asociarlo a un agente con vector store"""
    try:
        # Paso 1: Subir archivo
        file_id = await upload_file_to_project(file, azure_client)
        
        # Paso 2: Crear vector store
        vector_store_id = await create_vector_store_with_file(file_id, azure_client)
        
        if not vector_store_id:
            raise HTTPException(
                status_code=500,
                detail="Error al crear vector store"
            )
        
        # Paso 3: Asociar al agente
        association_success = await associate_vector_store_to_agent(
            agent_id, vector_store_id, azure_client
        )
        
        if not association_success:
            raise HTTPException(
                status_code=500,
                detail="Error al asociar vector store al agente"
            )
        
        return {
            "success": True,
            "message": "Archivo subido y asociado exitosamente",
            "file_id": file_id,
            "vector_store_id": vector_store_id,
            "agent_id": agent_id,
            "filename": file.filename,
            "bytes": file.size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al subir archivo: {str(e)}"
        )

async def upload_file_to_project(file: UploadFile, azure_client: AIProjectClient):
    """Subir archivo a Azure Foundry"""
    try:
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Crear un objeto file-like que Azure pueda entender
        # Necesitamos que tenga un nombre de archivo
        file_obj = io.BytesIO(file_content)
        file_obj.name = file.filename  # Establecer el nombre del archivo
        
        # Subir archivo usando el método correcto
        uploaded_file = azure_client.agents.files.upload(
            file=file_obj,
            purpose="assistants"
        )
        
        return uploaded_file.id
        
    except Exception as e:
        # Log más detallado para debugging
        print(f"Error detallado en upload_file_to_project: {str(e)}")
        print(f"Tipo de archivo: {type(file)}")
        print(f"Nombre del archivo: {file.filename}")
        print(f"Tamaño del archivo: {file.size}")
        raise Exception(f"Error al subir archivo: {str(e)}")

async def create_vector_store_with_file(file_id: str, azure_client: AIProjectClient):
    """Crear vector store con el archivo"""
    try:
        vector_store = azure_client.agents.vector_stores.create(
            name=f"VectorStore_ChatData_{int(time.time())}",
            file_ids=[file_id],
            expires_after={
                "anchor": "last_active_at",
                "days": 7
            }
        )
        
        # Esperar procesamiento
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            vs_status = azure_client.agents.vector_stores.get(vector_store.id)
            
            if vs_status.status == "completed":
                print("Vectorización completada!")
                return vector_store.id
            elif vs_status.status == "failed":
                print("Vectorización falló")
                return None
                
            time.sleep(2)
            attempt += 1
        
        return vector_store.id
        
    except Exception as e:
        raise Exception(f"Error al crear vector store: {str(e)}")

async def associate_vector_store_to_agent(
    agent_id: str, 
    vector_store_id: str, 
    azure_client: AIProjectClient
):
    """Asociar vector store al agente"""
    try:
        # Crear FileSearchToolDefinition
        file_search_tool = FileSearchToolDefinition()
        
        # Crear FileSearchToolResource
        file_search_resource = FileSearchToolResource(
            vector_store_ids=[vector_store_id]
        )
        
        tool_resources = ToolResources(
            file_search=file_search_resource
        )
        
        # Actualizar agente
        updated_agent = azure_client.agents.update_agent(
            agent_id=agent_id,
            tools=[file_search_tool],
            tool_resources=tool_resources
        )
        
        return True
        
    except Exception as e:
        raise Exception(f"Error al asociar vector store: {str(e)}")

@router.get("/{file_id}")
async def get_file(file_id: str, azure_client: AIProjectClient = Depends(get_azure_client)):
    """Obtener archivo por ID"""
    try:
        file = azure_client.agents.files.get(file_id=file_id)
        
        return {
            "success": True,
            "file": {
                "id": file.id,
                "object": file.object,
                "created_at": file.created_at,
                "filename": file.filename,
                "purpose": file.purpose,
                "bytes": file.bytes
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Archivo con ID {file_id} no encontrado: {str(e)}"
        )

@router.delete("/{file_id}")
async def delete_file(file_id: str, azure_client: AIProjectClient = Depends(get_azure_client)):
    """Eliminar archivo"""
    try:
        azure_client.agents.files.delete(file_id=file_id)
        
        return {
            "success": True,
            "message": f"Archivo {file_id} eliminado exitosamente"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Error al eliminar archivo {file_id}: {str(e)}"
        )
