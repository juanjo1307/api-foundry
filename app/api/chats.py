from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.dependencies import get_azure_client
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder
import time

router = APIRouter(prefix="/chats", tags=["chats"])

class MessageCreateRequest(BaseModel):
    """Modelo para crear un mensaje"""
    thread_id: str
    agent_id: str
    role: str = "user"  # "user" o "assistant"
    content: str

class RunCreateRequest(BaseModel):
    """Modelo para crear un run"""
    thread_id: str
    agent_id: str

@router.post("/messages")
async def create_message(
    request: MessageCreateRequest,
    azure_client: AIProjectClient = Depends(get_azure_client)
):
    """Crear mensaje en un thread"""
    try:
        # Validar rol del mensaje
        if request.role not in ["user", "assistant"]:
            raise HTTPException(
                status_code=400,
                detail="El rol debe ser 'user' o 'assistant'"
            )
        
        # Crear mensaje en Azure Foundry
        message = azure_client.agents.messages.create(
            thread_id=request.thread_id,
            role=request.role,
            content=request.content
        )

        # Crear run y procesar
        run = azure_client.agents.runs.create_and_process(
            thread_id=request.thread_id,
            agent_id=request.agent_id
        )
        
        messages_list = []
        if run.status == "failed":
            print(f"Run failed: {run.last_error}")
        else:
            messages = azure_client.agents.messages.list(thread_id=request.thread_id, order=ListSortOrder.ASCENDING)
            for message in messages:
                messages_list.append({
                    "id": message.id,
                    "thread_id": request.thread_id,
                    "role": message.role,
                    "content": message.content,
                    "created_at": message.created_at
                })



        return {
            "success": True,
            "message": "Mensaje creado exitosamente",
            "data": {
                "id": message.id,
                "thread_id": request.thread_id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at
            },
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al crear mensaje: {str(e)}"
        )

@router.get("/threads/{thread_id}/messages")
async def get_messages(
    thread_id: str, 
    azure_client: AIProjectClient = Depends(get_azure_client)
):
    """Obtener mensajes de un thread"""
    try:
        # Obtener mensajes desde Azure Foundry
        messages = azure_client.agents.messages.list(
            thread_id=thread_id,
            order=ListSortOrder.ASCENDING
        )
        
        # Convertir a lista para serialización
        messages_list = []
        for message in messages:
            # Extraer contenido del mensaje
            content = ""
            if hasattr(message, 'text_messages') and message.text_messages:
                content = message.text_messages[-1].text.value
            elif hasattr(message, 'content') and message.content:
                content = message.content
            
            messages_list.append({
                "id": message.id,
                "thread_id": thread_id,
                "role": message.role,
                "content": content,
                "created_at": message.created_at
            })
        
        return {
            "success": True,
            "count": len(messages_list),
            "thread_id": thread_id,
            "messages": messages_list
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener mensajes del thread {thread_id}: {str(e)}"
        )