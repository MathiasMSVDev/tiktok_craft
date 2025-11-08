"""
Data Transfer Objects para el módulo de subastas
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class CreateAuctionDTO(BaseModel):
    """DTO para crear una subasta (estado DRAFT)"""
    tituloSubasta: str = Field(..., min_length=1, max_length=200, description="Título de la subasta")
    nameStreamer: str = Field(..., min_length=1, max_length=100, description="Nombre del streamer de TikTok")
    timer: int = Field(..., gt=0, le=1440, description="Duración de la subasta en minutos (máximo 24 horas)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tituloSubasta": "Subasta de productos exclusivos",
                "nameStreamer": "santiago",
                "timer": 30
            }
        }


class UpdateAuctionDTO(BaseModel):
    """DTO para actualizar una subasta en estado DRAFT"""
    tituloSubasta: Optional[str] = Field(None, min_length=1, max_length=200, description="Nuevo título de la subasta")
    nameStreamer: Optional[str] = Field(None, min_length=1, max_length=100, description="Nuevo nombre del streamer")
    timer: Optional[int] = Field(None, gt=0, le=1440, description="Nueva duración en minutos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tituloSubasta": "Subasta actualizada",
                "timer": 45
            }
        }


class AuctionResponseDTO(BaseModel):
    """DTO de respuesta con información de la subasta"""
    id: str
    nameStreamer: str
    tituloSubasta: str
    timerMinutes: int
    status: str  # draft, active, paused, completed, stopped
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
                "tituloSubasta": "Subasta de productos exclusivos",
                "timerMinutes": 30,
                "status": "draft",
                "overlayUrl": "http://localhost:8000/overlay/auction/550e8400-e29b-41d4-a716-446655440000",
                "createdAt": "2025-11-07T10:30:00",
                "startedAt": None,
                "remainingSeconds": None
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


class StartAuctionResponseDTO(BaseModel):
    """DTO de respuesta al iniciar una subasta"""
    id: str
    status: str
    message: str
    startedAt: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "active",
                "message": "Subasta iniciada y conectada a TikTok Live",
                "startedAt": "2025-11-07T10:35:00"
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


class DonationDTO(BaseModel):
    """DTO para una donación individual"""
    username: str = Field(..., description="Nombre del usuario que donó")
    amount: float = Field(..., gt=0, description="Cantidad donada (en coins de TikTok)")
    timestamp: str = Field(..., description="Momento de la donación")
    giftName: Optional[str] = Field(None, description="Nombre del regalo enviado")
    profilePicture: Optional[str] = Field(None, description="URL de la foto de perfil del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "usuario123",
                "amount": 500.0,
                "timestamp": "2025-11-07T10:35:00",
                "giftName": "Rose",
                "profilePicture": "https://..."
            }
        }


class DonorStatsDTO(BaseModel):
    """DTO para estadísticas de un donador"""
    username: str = Field(..., description="Nombre del usuario")
    profilePicture: Optional[str] = Field(None, description="URL de la foto de perfil del usuario")
    totalAmount: float = Field(..., description="Cantidad total acumulada")
    donationCount: int = Field(..., description="Número de donaciones realizadas")
    lastDonation: str = Field(..., description="Fecha de la última donación")
    rank: int = Field(..., description="Posición en el ranking (1-5)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "usuario123",
                "profilePicture": "https://...",
                "totalAmount": 2500.0,
                "donationCount": 5,
                "lastDonation": "2025-11-07T10:35:00",
                "rank": 1
            }
        }


class TopDonorsResponseDTO(BaseModel):
    """DTO de respuesta para el top de donadores"""
    auctionId: str = Field(..., description="ID de la subasta")
    topDonors: List[DonorStatsDTO] = Field(..., description="Lista de top donadores")
    totalDonations: float = Field(..., description="Total de donaciones acumuladas")
    totalDonors: int = Field(..., description="Número total de donadores únicos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "auctionId": "auction-001",
                "topDonors": [
                    {
                        "username": "usuario1",
                        "totalAmount": 5000.0,
                        "donationCount": 10,
                        "lastDonation": "2025-11-07T10:35:00",
                        "rank": 1
                    }
                ],
                "totalDonations": 15000.0,
                "totalDonors": 25
            }
        }

