from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_azure_client
from app.database import get_db, create_tables
from app.models import Agent
from azure.ai.projects import AIProjectClient
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

router = APIRouter(prefix="/agents", tags=["agents"])

class AgentCreateRequest(BaseModel):
    """Modelo para crear un agente"""
    name: str
    model: str = "gpt-4o"
    instructions: str

def serialize_agent_for_response(agent):
    """Convierte un agente de la BD a diccionario para respuesta JSON"""
    return {
        "id": agent.id,
        "object": agent.object_type,
        "created_at": agent.created_at.isoformat() if agent.created_at else "",
        "name": agent.name,
        "description": agent.description,
        "model": agent.model,
        "instructions": agent.instructions,
        "tools": agent.tools,
        "top_p": agent.top_p,
        "temperature": agent.temperature,
        "tool_resources": agent.tool_resources,
        "metadata": agent.agent_metadata,
        "response_format": agent.response_format,
        "updated_at": agent.updated_at.isoformat() if agent.updated_at else ""
    }

@router.get("/")
async def list_agents(azure_client: AIProjectClient = Depends(get_azure_client)):
    """Listar todos los agentes desde Azure Foundry"""
    try:
        # Obtener lista de agentes desde Azure Foundry
        agents = azure_client.agents.list_agents()
        
        # Convertir a lista para serialización
        agents_list = []
        for agent in agents:
            agents_list.append(agent)
        
        return {
            "success": True,
            "count": len(agents_list),
            "agents": agents_list
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar agentes: {str(e)}"
        )

@router.get("/from-db")
async def list_agents_from_db(db: Session = Depends(get_db)):
    """Listar todos los agentes desde la base de datos"""
    try:
        # Obtener agentes de la base de datos
        agents = db.query(Agent).all()
        
        # Convertir a lista para serialización
        agents_list = []
        for agent in agents:
            agents_list.append(serialize_agent_for_response(agent))
        
        return {
            "success": True,
            "count": len(agents_list),
            "agents": agents_list
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar agentes desde BD: {str(e)}"
        )

@router.post("/")
async def create_agent(
    request: AgentCreateRequest,
    azure_client: AIProjectClient = Depends(get_azure_client),
    db: Session = Depends(get_db)
):
    """Crear nuevo agente"""
    try:
        # Crear agente en Azure Foundry
        agent = azure_client.agents.create_agent(
            model=request.model,
            name=request.name,
            instructions=request.instructions,
        )
        
        # Guardar en base de datos
        db_agent = Agent(
            id=agent.id,
            object_type=agent.object,
            created_at=datetime.now(timezone.utc),
            name=agent.name,
            description=agent.description,
            model=agent.model,
            instructions=agent.instructions,
            tools=agent.tools,
            top_p=agent.top_p,
            temperature=agent.temperature,
            tool_resources={},
            agent_metadata=agent.metadata,
            response_format=agent.response_format,
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        
        # Preparar respuesta usando la función helper
        response = {
            "success": True,
            "message": "Agente creado exitosamente",
            "agent": serialize_agent_for_response(db_agent)
        }
        
        return response
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error al crear agente: {str(e)}"
        )

@router.get("/{agent_id}")
async def get_agent(
    agent_id: str, 
    azure_client: AIProjectClient = Depends(get_azure_client),
    db: Session = Depends(get_db)
):
    """Obtener agente por ID desde Azure Foundry y base de datos"""
    try:
        # Obtener agente desde Azure Foundry
        azure_agent = azure_client.agents.get_agent(agent_id=agent_id)
        
        # Obtener agente desde base de datos
        db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
        
        # Preparar respuesta con datos de Azure
        response = {
            "success": True,
            "agent": {
                "id": azure_agent.id,
                "object": azure_agent.object,
                "created_at": azure_agent.created_at,
                "name": azure_agent.name,
                "description": azure_agent.description,
                "model": azure_agent.model,
                "instructions": azure_agent.instructions,
                "tools": azure_agent.tools,
                "top_p": azure_agent.top_p,
                "temperature": azure_agent.temperature,
                "tool_resources": azure_agent.tool_resources,
                "metadata": azure_agent.metadata,
                "response_format": azure_agent.response_format
            },
            "from_database": db_agent is not None,
            "database_agent": serialize_agent_for_response(db_agent) if db_agent else None
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Agente con ID {agent_id} no encontrado: {str(e)}"
        )

@router.put("/{agent_id}")
async def update_agent(agent_id: str, azure_client: AIProjectClient = Depends(get_azure_client)):
    """Actualizar agente"""
    # TODO: Implementar actualización de agente
    return {"message": f"Actualizar agente {agent_id} - Pendiente de implementar"}

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str, 
    azure_client: AIProjectClient = Depends(get_azure_client),
    db: Session = Depends(get_db)
):
    """Eliminar agente por ID desde Azure Foundry y base de datos"""
    try:
        # Verificar si el agente existe en Azure Foundry
        try:
            azure_agent = azure_client.agents.get_agent(agent_id=agent_id)
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Agente con ID {agent_id} no encontrado en Azure Foundry: {str(e)}"
            )
        
        # Eliminar de Azure Foundry
        azure_client.agents.delete_agent(agent_id=agent_id)
        
        # Eliminar de base de datos (si existe)
        db_agent = db.query(Agent).filter(Agent.id == agent_id).first()
        deleted_from_db = False
        
        if db_agent:
            db.delete(db_agent)
            db.commit()
            deleted_from_db = True
        
        # Preparar respuesta
        response = {
            "success": True,
            "message": f"Agente {agent_id} eliminado exitosamente",
            "deleted_from_azure": True,
            "deleted_from_database": deleted_from_db,
            "agent_info": {
                "id": agent_id,
                "name": azure_agent.name,
                "model": azure_agent.model
            }
        }
        
        return response
        
    except HTTPException:
        # Re-lanzar HTTPException para mantener el código de error
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar agente {agent_id}: {str(e)}"
        )
