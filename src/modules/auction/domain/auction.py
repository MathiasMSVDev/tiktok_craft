"""
Entidad de dominio: Auction (Subasta)
Representa una subasta en el sistema
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import uuid


class AuctionStatus(Enum):
    """Estados posibles de una subasta"""
    PENDING = "pending"      # Creada pero no iniciada
    ACTIVE = "active"        # En curso
    PAUSED = "paused"        # Pausada manualmente
    COMPLETED = "completed"  # Finalizada por tiempo
    STOPPED = "stopped"      # Detenida manualmente


class Auction:
    """
    Entidad de subasta que encapsula toda la lógica de negocio
    """
    
    def __init__(
        self,
        id: str,
        name_streamer: str,
        titulo_subasta: str,
        timer_minutes: int,
        created_at: Optional[datetime] = None,
        status: AuctionStatus = AuctionStatus.PENDING
    ):
        self.id = id
        self.name_streamer = name_streamer
        self.titulo_subasta = titulo_subasta
        self.timer_minutes = timer_minutes
        self.created_at = created_at or datetime.now()
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        self.status = status
        self.remaining_seconds: Optional[int] = None
        
    def start(self) -> None:
        """Inicia la subasta"""
        if self.status != AuctionStatus.PENDING:
            raise ValueError(f"No se puede iniciar una subasta en estado {self.status.value}")
        
        self.status = AuctionStatus.ACTIVE
        self.started_at = datetime.now()
        self.remaining_seconds = self.timer_minutes * 60
        
    def pause(self) -> None:
        """Pausa la subasta"""
        if self.status != AuctionStatus.ACTIVE:
            raise ValueError(f"No se puede pausar una subasta en estado {self.status.value}")
        
        self.status = AuctionStatus.PAUSED
        
    def resume(self) -> None:
        """Reanuda la subasta"""
        if self.status != AuctionStatus.PAUSED:
            raise ValueError(f"No se puede reanudar una subasta en estado {self.status.value}")
        
        self.status = AuctionStatus.ACTIVE
        
    def stop(self) -> None:
        """Detiene manualmente la subasta"""
        if self.status not in [AuctionStatus.ACTIVE, AuctionStatus.PAUSED]:
            raise ValueError(f"No se puede detener una subasta en estado {self.status.value}")
        
        self.status = AuctionStatus.STOPPED
        self.ended_at = datetime.now()
        
    def complete(self) -> None:
        """Marca la subasta como completada por tiempo"""
        self.status = AuctionStatus.COMPLETED
        self.ended_at = datetime.now()
        self.remaining_seconds = 0
        
    def add_time(self, seconds: int) -> None:
        """Añade tiempo a la subasta"""
        if self.status not in [AuctionStatus.ACTIVE, AuctionStatus.PAUSED]:
            raise ValueError(f"No se puede añadir tiempo en estado {self.status.value}")
        
        if self.remaining_seconds is None:
            self.remaining_seconds = 0
            
        self.remaining_seconds += seconds
        
    def subtract_time(self, seconds: int) -> None:
        """Resta tiempo a la subasta"""
        if self.status not in [AuctionStatus.ACTIVE, AuctionStatus.PAUSED]:
            raise ValueError(f"No se puede restar tiempo en estado {self.status.value}")
        
        if self.remaining_seconds is None:
            self.remaining_seconds = 0
            
        self.remaining_seconds = max(0, self.remaining_seconds - seconds)
        
        # Si el tiempo llega a 0, completar la subasta
        if self.remaining_seconds == 0 and self.status == AuctionStatus.ACTIVE:
            self.complete()
            
    def update_remaining_time(self, seconds: int) -> None:
        """Actualiza el tiempo restante"""
        if self.status not in [AuctionStatus.ACTIVE, AuctionStatus.PAUSED]:
            return
            
        self.remaining_seconds = max(0, seconds)
        
        if self.remaining_seconds == 0 and self.status == AuctionStatus.ACTIVE:
            self.complete()
            
    def get_overlay_url(self, base_url: str) -> str:
        """Genera la URL del overlay para esta subasta"""
        return f"{base_url}/overlay/auction/{self.id}"
        
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        return {
            "id": self.id,
            "nameStreamer": self.name_streamer,
            "tituloSubasta": self.titulo_subasta,
            "timerMinutes": self.timer_minutes,
            "status": self.status.value,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "startedAt": self.started_at.isoformat() if self.started_at else None,
            "endedAt": self.ended_at.isoformat() if self.ended_at else None,
            "remainingSeconds": self.remaining_seconds
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'Auction':
        """Crea una instancia desde un diccionario"""
        auction = cls(
            id=data["id"],
            name_streamer=data["nameStreamer"],
            titulo_subasta=data["tituloSubasta"],
            timer_minutes=data["timerMinutes"],
            created_at=datetime.fromisoformat(data["createdAt"]) if data.get("createdAt") else None,
            status=AuctionStatus(data.get("status", "pending"))
        )
        
        if data.get("startedAt"):
            auction.started_at = datetime.fromisoformat(data["startedAt"])
        if data.get("endedAt"):
            auction.ended_at = datetime.fromisoformat(data["endedAt"])
        if data.get("remainingSeconds") is not None:
            auction.remaining_seconds = data["remainingSeconds"]
            
        return auction
