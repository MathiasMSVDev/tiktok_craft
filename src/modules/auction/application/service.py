"""
Servicio de aplicación para gestionar subastas
Orquesta la lógica de negocio
"""
import uuid
from typing import Optional, List
from ..domain.auction import Auction, AuctionStatus
from ..infrastructure.repository import AuctionRepository
from ..application.dtos import CreateAuctionDTO, AuctionResponseDTO


class AuctionService:
    """Servicio para gestionar operaciones de subastas"""
    
    def __init__(self, repository: AuctionRepository, base_url: str = "http://localhost:8000"):
        self.repository = repository
        self.base_url = base_url
        
    def create_auction(self, dto: CreateAuctionDTO) -> AuctionResponseDTO:
        """Crea una nueva subasta"""
        # Generar ID si no se proporciona
        auction_id = dto.id or str(uuid.uuid4())
        
        # Verificar que no existe
        if self.repository.exists(auction_id):
            raise ValueError(f"Ya existe una subasta con el ID {auction_id}")
        
        # Crear entidad
        auction = Auction(
            id=auction_id,
            name_streamer=dto.nameStreamer,
            titulo_subasta=dto.tituloSubasta,
            timer_minutes=dto.timer
        )
        
        # Iniciar automáticamente la subasta
        auction.start()
        
        # Guardar
        self.repository.save(auction)
        
        # Retornar DTO de respuesta
        return self._to_response_dto(auction)
        
    def get_auction(self, auction_id: str) -> Optional[AuctionResponseDTO]:
        """Obtiene una subasta por ID"""
        auction = self.repository.find_by_id(auction_id)
        if not auction:
            return None
        return self._to_response_dto(auction)
        
    def get_all_auctions(self) -> List[AuctionResponseDTO]:
        """Obtiene todas las subastas"""
        auctions = self.repository.find_all()
        return [self._to_response_dto(a) for a in auctions]
        
    def start_auction(self, auction_id: str) -> AuctionResponseDTO:
        """Inicia una subasta"""
        auction = self._get_auction_or_raise(auction_id)
        auction.start()
        self.repository.save(auction)
        return self._to_response_dto(auction)
        
    def pause_auction(self, auction_id: str) -> AuctionResponseDTO:
        """Pausa una subasta"""
        auction = self._get_auction_or_raise(auction_id)
        auction.pause()
        self.repository.save(auction)
        return self._to_response_dto(auction)
        
    def resume_auction(self, auction_id: str) -> AuctionResponseDTO:
        """Reanuda una subasta"""
        auction = self._get_auction_or_raise(auction_id)
        auction.resume()
        self.repository.save(auction)
        return self._to_response_dto(auction)
        
    def stop_auction(self, auction_id: str) -> AuctionResponseDTO:
        """Detiene una subasta manualmente"""
        auction = self._get_auction_or_raise(auction_id)
        auction.stop()
        self.repository.save(auction)
        return self._to_response_dto(auction)
        
    def update_time(self, auction_id: str, seconds: int) -> AuctionResponseDTO:
        """Modifica el tiempo de una subasta"""
        auction = self._get_auction_or_raise(auction_id)
        
        if seconds > 0:
            auction.add_time(seconds)
        else:
            auction.subtract_time(abs(seconds))
            
        self.repository.save(auction)
        return self._to_response_dto(auction)
        
    def update_remaining_time(self, auction_id: str, remaining_seconds: int) -> None:
        """Actualiza el tiempo restante de una subasta (usado por el timer)"""
        auction = self._get_auction_or_raise(auction_id)
        auction.update_remaining_time(remaining_seconds)
        self.repository.save(auction)
        
    def delete_auction(self, auction_id: str) -> bool:
        """Elimina una subasta"""
        return self.repository.delete(auction_id)
        
    def _get_auction_or_raise(self, auction_id: str) -> Auction:
        """Obtiene una subasta o lanza excepción"""
        auction = self.repository.find_by_id(auction_id)
        if not auction:
            raise ValueError(f"No se encontró la subasta con ID {auction_id}")
        return auction
        
    def _to_response_dto(self, auction: Auction) -> AuctionResponseDTO:
        """Convierte una entidad a DTO de respuesta"""
        data = auction.to_dict()
        return AuctionResponseDTO(
            id=data["id"],
            nameStreamer=data["nameStreamer"],
            tituloSubasta=data["tituloSubasta"],
            timerMinutes=data["timerMinutes"],
            status=data["status"],
            overlayUrl=auction.get_overlay_url(self.base_url),
            createdAt=data["createdAt"],
            startedAt=data["startedAt"],
            endedAt=data["endedAt"],
            remainingSeconds=data["remainingSeconds"]
        )
