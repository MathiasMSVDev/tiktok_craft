"""
Data Transfer Objects para el módulo de subastas
"""
from pydantic import BaseModel, Field
from typing import Optional


class CreateAuctionDTO(BaseModel):
    """DTO para crear una subasta"""
    nameStreamer: str = Field(..., min_length=1, max_length=100, description="Nombre del streamer")
    timer: int = Field(..., gt=0, le=120, description="Duración de la subasta en minutos")
    tituloSubasta: str = Field(..., min_length=1, max_length=200, description="Título de la subasta")
    id: Optional[str] = Field(None, description="ID personalizado (opcional, se genera automáticamente si no se proporciona)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nameStreamer": "santiago",
                "timer": 5,
                "tituloSubasta": "Subasta online",
                "id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class AuctionResponseDTO(BaseModel):
    """DTO de respuesta con información de la subasta"""
    id: str
    nameStreamer: str
    tituloSubasta: str
    timerMinutes: int
    status: str
    overlayUrl: str
    createdAt: str
    startedAt: Optional[str] = None
    endedAt: Optional[str] = None
    remainingSeconds: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "nameStreamer": "santiago",
                "tituloSubasta": "Subasta online",
                "timerMinutes": 5,
                "status": "active",
                "overlayUrl": "http://localhost:8000/overlay/auction/550e8400-e29b-41d4-a716-446655440000",
                "createdAt": "2025-11-07T10:30:00",
                "startedAt": "2025-11-07T10:31:00",
                "remainingSeconds": 240
            }
        }


class UpdateTimeDTO(BaseModel):
    """DTO para modificar el tiempo de una subasta"""
    seconds: int = Field(..., description="Segundos a añadir (positivo) o restar (negativo)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "seconds": 60  # Añadir 1 minuto
            }
        }


class AuctionStatusDTO(BaseModel):
    """DTO para cambiar el estado de una subasta"""
    action: str = Field(..., pattern="^(start|pause|resume|stop)$", description="Acción a realizar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action": "start"
            }
        }


class WebSocketMessage(BaseModel):
    """DTO para mensajes WebSocket"""
    type: str = Field(..., description="Tipo de mensaje")
    auctionId: str = Field(..., description="ID de la subasta")
    data: Optional[dict] = Field(None, description="Datos adicionales")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "time_update",
                "auctionId": "550e8400-e29b-41d4-a716-446655440000",
                "data": {
                    "remainingSeconds": 240
                }
            }
        }
