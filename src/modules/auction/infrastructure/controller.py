"""
Controlador REST para el módulo de subastas
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from ..application.dtos import (
    CreateAuctionDTO, 
    AuctionResponseDTO, 
    UpdateTimeDTO, 
    AuctionStatusDTO
)
from ..application.service import AuctionService
from ....shared.websocket_manager import websocket_manager


class AuctionController:
    """Controlador REST para gestionar subastas"""
    
    def __init__(self, service: AuctionService):
        self.service = service
        self.router = APIRouter(prefix="/api/auctions", tags=["Auctions"])
        self._register_routes()
        
    def _register_routes(self):
        """Registra todas las rutas del controlador"""
        
        @self.router.post("", response_model=AuctionResponseDTO, status_code=status.HTTP_201_CREATED)
        async def create_auction(dto: CreateAuctionDTO):
            """
            Crea una nueva subasta y devuelve el enlace del overlay
            
            - **nameStreamer**: Nombre del streamer
            - **timer**: Duración en minutos (1-120)
            - **tituloSubasta**: Título de la subasta
            - **id**: ID opcional (se genera automáticamente si no se proporciona)
            """
            try:
                result = self.service.create_auction(dto)
                # Notificar a todos los clientes conectados
                await websocket_manager.broadcast_status_change(result.id, result.status)
                return result
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
                
        @self.router.get("", response_model=List[AuctionResponseDTO])
        async def get_all_auctions():
            """Obtiene todas las subastas"""
            return self.service.get_all_auctions()
            
        @self.router.get("/{auction_id}", response_model=AuctionResponseDTO)
        async def get_auction(auction_id: str):
            """Obtiene una subasta específica por ID"""
            auction = self.service.get_auction(auction_id)
            if not auction:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subasta no encontrada")
            return auction
            
        @self.router.post("/{auction_id}/control", response_model=AuctionResponseDTO)
        async def control_auction(auction_id: str, dto: AuctionStatusDTO):
            """
            Controla el estado de una subasta
            
            - **action**: start | pause | resume | stop
            """
            try:
                if dto.action == "start":
                    result = self.service.start_auction(auction_id)
                elif dto.action == "pause":
                    result = self.service.pause_auction(auction_id)
                elif dto.action == "resume":
                    result = self.service.resume_auction(auction_id)
                elif dto.action == "stop":
                    result = self.service.stop_auction(auction_id)
                else:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Acción inválida")
                    
                # Notificar cambio de estado
                await websocket_manager.broadcast_status_change(result.id, result.status)
                return result
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
                
        @self.router.patch("/{auction_id}/time", response_model=AuctionResponseDTO)
        async def update_time(auction_id: str, dto: UpdateTimeDTO):
            """
            Modifica el tiempo de una subasta
            
            - **seconds**: Segundos a añadir (positivo) o restar (negativo)
            """
            try:
                result = self.service.update_time(auction_id, dto.seconds)
                # Notificar actualización de tiempo
                if result.remainingSeconds is not None:
                    await websocket_manager.broadcast_time_update(result.id, result.remainingSeconds)
                return result
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
                
        @self.router.delete("/{auction_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_auction(auction_id: str):
            """Elimina una subasta"""
            if not self.service.delete_auction(auction_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subasta no encontrada")
