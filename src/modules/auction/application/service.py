"""
Servicio de aplicación para gestionar subastas
Orquesta la lógica de negocio
"""
import uuid
from typing import Optional, List
from ..domain.auction import Auction, AuctionStatus
from ..domain.donation import DonationTracker
from ..infrastructure.repository import AuctionRepository
from ....shared.tiktok_connector import TikTokLiveConnector
from ..application.dtos import (
    CreateAuctionDTO, 
    UpdateAuctionDTO,
    AuctionResponseDTO, 
    TopDonorsResponseDTO,
    StartAuctionResponseDTO,
    UpdateTimeDTO
)


class AuctionService:
    """Servicio para gestionar operaciones de subastas"""
    
    def __init__(
        self, 
        repository: AuctionRepository, 
        tiktok_connector: TikTokLiveConnector,
        base_url: str = "http://localhost:8000"
    ):
        self.repository = repository
        self.tiktok_connector = tiktok_connector
        self.base_url = base_url
        self.donation_trackers: dict[str, DonationTracker] = {}
        self.websocket_manager = None  # Se inyectará desde el controller
        
    def set_websocket_manager(self, manager):
        """Inyecta el WebSocket manager"""
        self.websocket_manager = manager
        
    def create_auction(self, dto: CreateAuctionDTO) -> AuctionResponseDTO:
        """Crea una nueva subasta en estado DRAFT"""
        # Generar ID automáticamente
        auction_id = str(uuid.uuid4())
        
        # Crear entidad en estado DRAFT
        auction = Auction(
            id=auction_id,
            name_streamer=dto.nameStreamer,
            titulo_subasta=dto.tituloSubasta,
            timer_minutes=dto.timer,
            status=AuctionStatus.DRAFT
        )
        
        # Guardar
        self.repository.save(auction)
        
        # Retornar DTO de respuesta
        return self._to_response_dto(auction)
    
    def update_auction(self, auction_id: str, dto: UpdateAuctionDTO) -> AuctionResponseDTO:
        """Actualiza una subasta en estado DRAFT"""
        auction = self._get_auction_or_raise(auction_id)
        
        # Llamar al método de dominio que valida el estado
        auction.update(
            titulo_subasta=dto.tituloSubasta,
            name_streamer=dto.nameStreamer,
            timer_minutes=dto.timer
        )
        
        # Guardar
        self.repository.save(auction)
        
        return self._to_response_dto(auction)
    
    def start_auction(self, auction_id: str) -> StartAuctionResponseDTO:
        """Inicia una subasta (cambia de DRAFT a ACTIVE y conecta TikTok Live)"""
        auction = self._get_auction_or_raise(auction_id)
        
        # Iniciar la subasta (validación de estado en el dominio)
        auction.start()
        
        # Guardar estado
        self.repository.save(auction)
        
        # Crear tracker de donaciones
        self.donation_trackers[auction_id] = DonationTracker(auction_id)
        
        # Conectar a TikTok Live de forma asíncrona
        import asyncio
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            connection_task = asyncio.create_task(
                self.tiktok_connector.connect(
                    auction.name_streamer,
                    auction_id,
                    lambda username, amount, gift, profile_pic: self._on_donation_received(
                        auction_id, username, amount, gift, profile_pic
                    )
                )
            )
            logger.info(f"🔄 Conexión TikTok Live iniciada para @{auction.name_streamer}")
        except Exception as e:
            logger.warning(f"⚠️ Error al iniciar conexión TikTok Live: {e}")
            logger.warning(f"   La subasta continuará pero sin capturar donaciones automáticamente")
        
        # Retornar respuesta específica
        return StartAuctionResponseDTO(
            id=auction_id,
            status=auction.status.value,
            message="Subasta iniciada. Conectando con TikTok Live...",
            startedAt=auction.started_at.isoformat()
        )
        
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
        """Detiene una subasta manualmente y desconecta de TikTok Live"""
        auction = self._get_auction_or_raise(auction_id)
        auction.stop()
        self.repository.save(auction)
        
        # Desconectar de TikTok Live
        import asyncio
        try:
            asyncio.create_task(self.tiktok_connector.disconnect(auction_id))
        except Exception as e:
            print(f"Error desconectando de TikTok Live: {e}")
        
        return self._to_response_dto(auction)
        
    def update_time(self, auction_id: str, dto: UpdateTimeDTO) -> AuctionResponseDTO:
        """Modifica el tiempo de una subasta"""
        auction = self._get_auction_or_raise(auction_id)
        
        if dto.seconds > 0:
            auction.add_time(dto.seconds)
        else:
            auction.subtract_time(abs(dto.seconds))
            
        self.repository.save(auction)
        return self._to_response_dto(auction)
        
    def update_remaining_time(self, auction_id: str, remaining_seconds: int) -> None:
        """Actualiza el tiempo restante de una subasta (usado por el timer)"""
        auction = self._get_auction_or_raise(auction_id)
        auction.update_remaining_time(remaining_seconds)
        self.repository.save(auction)
        
    def delete_auction(self, auction_id: str) -> bool:
        """Elimina una subasta"""
        # Desconectar de TikTok Live
        import asyncio
        try:
            asyncio.create_task(self.tiktok_connector.disconnect(auction_id))
        except Exception:
            pass
        
        # Eliminar tracker de donaciones
        if auction_id in self.donation_trackers:
            del self.donation_trackers[auction_id]
        
        return self.repository.delete(auction_id)
    
    def get_top_donors(self, auction_id: str) -> TopDonorsResponseDTO:
        """Obtiene el top 5 de donadores de una subasta"""
        if auction_id not in self.donation_trackers:
            raise ValueError(f"No se encontró el tracker de donaciones para la subasta {auction_id}")
        
        tracker = self.donation_trackers[auction_id]
        data = tracker.to_dict()
        
        return TopDonorsResponseDTO(**data)
    
    def _on_donation_received(self, auction_id: str, username: str, amount: float, gift_name: str, profile_picture: str):
        """Callback cuando se recibe una donación de TikTok Live"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Verificar que la subasta existe y está en estado ACTIVE
            auction = self.repository.find_by_id(auction_id)
            if not auction:
                logger.warning(f"⚠️ Donación ignorada: subasta {auction_id} no encontrada")
                return
            
            if auction.status != AuctionStatus.ACTIVE:
                logger.warning(f"⚠️ Donación ignorada: subasta en estado {auction.status.value} (solo se aceptan en ACTIVE)")
                logger.info(f"   Usuario: {username} intentó donar {amount} coins ({gift_name})")
                return
            
            # Registrar donación en el tracker
            if auction_id in self.donation_trackers:
                tracker = self.donation_trackers[auction_id]
                donation = tracker.add_donation(username, amount, gift_name, profile_picture)
                
                # Obtener stats del donador para logging
                donor_stats = tracker.get_donor_stats(username)
                
                logger.info(f"✅ DONACIÓN REGISTRADA:")
                logger.info(f"   Usuario: {username}")
                logger.info(f"   Monto esta donación: {amount} coins")
                logger.info(f"   Total acumulado: {donor_stats.total_amount} coins")
                logger.info(f"   Número de donaciones: {donor_stats.donation_count}")
                
                # Enviar actualización por WebSocket
                if self.websocket_manager:
                    import asyncio
                    tracker_data = tracker.to_dict()
                    
                    logger.info(f"📡 Enviando actualización WebSocket:")
                    logger.info(f"   Top 5 actual: {[f'{d['username']}({d['totalAmount']})' for d in tracker_data['topDonors'][:5]]}")
                    
                    asyncio.create_task(
                        self.websocket_manager.broadcast_donation_update(
                            auction_id,
                            tracker_data
                        )
                    )
            else:
                logger.warning(f"⚠️ No existe tracker de donaciones para la subasta {auction_id}")
        except Exception as e:
            logger.error(f"❌ Error procesando donación: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
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
