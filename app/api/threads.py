from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_azure_client
from azure.ai.projects import AIProjectClient

router = APIRouter(prefix="/threads", tags=["threads"])

@router.get("/")
async def list_threads(azure_client: AIProjectClient = Depends(get_azure_client)):
    """Listar todos los threads"""
    try:
        # Obtener lista de threads desde Azure Foundry
        threads = azure_client.agents.threads.list()
        
        # Convertir a lista para serialización
        threads_list = []
        for thread in threads:
            threads_list.append({
                "id": thread.id,
                "object": thread.object,
                "created_at": thread.created_at,
                "metadata": thread.metadata
            })
        
        return {
            "success": True,
            "count": len(threads_list),
            "threads": threads_list
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar threads: {str(e)}"
        )

@router.post("/")
async def create_thread(azure_client: AIProjectClient = Depends(get_azure_client)):
    """Crear nuevo thread"""
    try:
        # Crear thread en Azure Foundry
        thread = azure_client.agents.threads.create()
        
        return {
            "success": True,
            "message": "Thread creado exitosamente",
            "thread": {
                "id": thread.id,
                "object": thread.object,
                "created_at": thread.created_at,
                "metadata": thread.metadata
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al crear thread: {str(e)}"
        )

@router.get("/{thread_id}")
async def get_thread(thread_id: str, azure_client: AIProjectClient = Depends(get_azure_client)):
    """Obtener thread por ID"""
    try:
        # Obtener thread desde Azure Foundry
        thread = azure_client.agents.threads.get(thread_id=thread_id)
        
        return {
            "success": True,
            "thread": {
                "id": thread.id,
                "object": thread.object,
                "created_at": thread.created_at,
                "metadata": thread.metadata
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Thread con ID {thread_id} no encontrado: {str(e)}"
        )

@router.delete("/{thread_id}")
async def delete_thread(thread_id: str, azure_client: AIProjectClient = Depends(get_azure_client)):
    """Eliminar thread"""
    try:
        # Verificar que el thread existe antes de eliminar
        try:
            thread = azure_client.agents.threads.get(thread_id=thread_id)
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Thread con ID {thread_id} no encontrado: {str(e)}"
            )
        
        # Eliminar thread
        azure_client.agents.threads.delete(thread_id=thread_id)
        
        return {
            "success": True,
            "message": f"Thread {thread_id} eliminado exitosamente",
            "thread_info": {
                "id": thread_id,
                "created_at": thread.created_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar thread {thread_id}: {str(e)}"
        )
