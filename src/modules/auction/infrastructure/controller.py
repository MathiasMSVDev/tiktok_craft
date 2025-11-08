"""
Controlador REST para el módulo de subastas
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from ..application.dtos import (
    CreateAuctionDTO,
    UpdateAuctionDTO,
    AuctionResponseDTO, 
    UpdateTimeDTO,
    TopDonorsResponseDTO,
    StartAuctionResponseDTO
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
            Crea una nueva subasta en estado DRAFT
            
            - **tituloSubasta**: Título de la subasta
            - **nameStreamer**: Nombre del streamer de TikTok
            - **timer**: Duración en minutos (1-1440)
            
            La subasta se crea con un GUID automático y en estado DRAFT.
            Para iniciarla, usar POST /api/auctions/{id}/start
            """
            try:
                result = self.service.create_auction(dto)
                return result
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        @self.router.put("/{auction_id}", response_model=AuctionResponseDTO)
        async def update_auction(auction_id: str, dto: UpdateAuctionDTO):
            """
            Actualiza una subasta en estado DRAFT
            
            - **tituloSubasta**: Nuevo título (opcional)
            - **nameStreamer**: Nuevo nombre del streamer (opcional)
            - **timer**: Nueva duración en minutos (opcional)
            
            Solo se pueden actualizar subastas en estado DRAFT.
            """
            try:
                result = self.service.update_auction(auction_id, dto)
                return result
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        @self.router.post("/{auction_id}/start", response_model=StartAuctionResponseDTO, status_code=status.HTTP_200_OK)
        async def start_auction(auction_id: str):
            """
            Inicia una subasta (DRAFT -> ACTIVE)
            
            Cambia el estado de DRAFT a ACTIVE, conecta con TikTok Live
            y comienza el conteo del timer.
            """
            try:
                result = self.service.start_auction(auction_id)
                # Notificar cambio de estado por WebSocket
                await websocket_manager.broadcast_status_change(auction_id, result.status)
                return result
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        @self.router.post("/{auction_id}/stop", response_model=AuctionResponseDTO)
        async def stop_auction(auction_id: str):
            """
            Detiene una subasta manualmente
            
            Cambia el estado a STOPPED y desconecta de TikTok Live.
            """
            try:
                result = self.service.stop_auction(auction_id)
                await websocket_manager.broadcast_status_change(auction_id, result.status)
                return result
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        @self.router.post("/{auction_id}/pause", response_model=AuctionResponseDTO)
        async def pause_auction(auction_id: str):
            """Pausa una subasta activa"""
            try:
                result = self.service.pause_auction(auction_id)
                await websocket_manager.broadcast_status_change(auction_id, result.status)
                return result
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        @self.router.post("/{auction_id}/resume", response_model=AuctionResponseDTO)
        async def resume_auction(auction_id: str):
            """Reanuda una subasta pausada"""
            try:
                result = self.service.resume_auction(auction_id)
                await websocket_manager.broadcast_status_change(auction_id, result.status)
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
        
        @self.router.patch("/{auction_id}/time", response_model=AuctionResponseDTO)
        async def update_time(auction_id: str, dto: UpdateTimeDTO):
            """
            Actualiza el tiempo restante de una subasta activa
            
            - **seconds**: Segundos a añadir (positivo) o restar (negativo)
            """
            try:
                result = self.service.update_time(auction_id, dto)
                if result.remainingSeconds is not None:
                    await websocket_manager.broadcast_time_update(auction_id, result.remainingSeconds)
                return result
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        @self.router.delete("/{auction_id}", status_code=status.HTTP_204_NO_CONTENT)
        async def delete_auction(auction_id: str):
            """Elimina una subasta"""
            deleted = self.service.delete_auction(auction_id)
            if not deleted:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subasta no encontrada")
        
        @self.router.get("/{auction_id}/top-donors", response_model=TopDonorsResponseDTO)
        async def get_top_donors(auction_id: str):
            """Obtiene el top 5 de donadores de la subasta"""
            try:
                return self.service.get_top_donors(auction_id)
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
                
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
        
        @self.router.get("/{auction_id}/top-donors", response_model=TopDonorsResponseDTO)
        async def get_top_donors(auction_id: str):
            """
            Obtiene el top 5 de donadores de una subasta
            
            Retorna la lista de los 5 usuarios que más han donado durante la subasta,
            ordenados por cantidad total donada.
            """
            try:
                return self.service.get_top_donors(auction_id)
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
