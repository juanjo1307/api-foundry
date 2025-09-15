from sqlalchemy import Column, String, Text, Float, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Agent(Base):
    """Modelo para almacenar agentes en la base de datos"""
    __tablename__ = "agents"
    
    id = Column(String(255), primary_key=True)  # asst_xxx
    object_type = Column(String(50), default="assistant")
    created_at = Column(DateTime, default=func.now())
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    model = Column(String(100), nullable=False)
    instructions = Column(Text, nullable=False)
    tools = Column(JSON, default=list)  # Lista de herramientas
    top_p = Column(Float, default=0.9)
    temperature = Column(Float, default=0.7)
    tool_resources = Column(JSON, default=dict)  # Recursos de herramientas
    agent_metadata = Column(JSON, default=dict)  # Metadatos adicionales (renombrado)
    response_format = Column(String(50), default="auto")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
