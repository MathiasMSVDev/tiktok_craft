"""
Adaptador para conectar con TikTok Live
Captura eventos de donaciones en tiempo real
"""
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, GiftEvent, DisconnectEvent
from typing import Callable, Optional, Dict
import asyncio
import logging

logger = logging.getLogger(__name__)


class TikTokLiveConnector:
    """
    Conector para TikTok Live que captura eventos de donaciones
    """
    
    def __init__(self):
        self.clients: Dict[str, TikTokLiveClient] = {}
        self.donation_callbacks: Dict[str, Callable] = {}
        
    async def connect(
        self,
        username: str,
        auction_id: str,
        on_donation: Callable[[str, float, str], None]
    ) -> bool:
        """
        Conecta al stream de TikTok Live de un usuario
        
        Args:
            username: Nombre del streamer en TikTok
            auction_id: ID de la subasta asociada
            on_donation: Callback que se ejecuta cuando hay una donación
                        Recibe (username, amount, gift_name)
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            # Crear cliente de TikTok Live
            client = TikTokLiveClient(unique_id=f"@{username}")
            
            # Registrar callback de donación
            self.donation_callbacks[auction_id] = on_donation
            
            # Handler para eventos de regalo (donaciones)
            @client.on(GiftEvent)
            async def on_gift(event: GiftEvent):
                try:
                    # Solo procesar regalos completados (no repetidos durante el envío)
                    if event.gift.streakable and not event.gift.streaking:
                        # Calcular el valor total (cantidad * valor del regalo)
                        total_value = event.gift.count * event.gift.diamond_count
                        
                        logger.info(
                            f"Donación recibida: {event.user.nickname} envió {event.gift.count}x "
                            f"{event.gift.name} (Total: {total_value} coins)"
                        )
                        
                        # Ejecutar callback
                        if auction_id in self.donation_callbacks:
                            self.donation_callbacks[auction_id](
                                event.user.nickname,
                                float(total_value),
                                event.gift.name
                            )
                    elif not event.gift.streakable:
                        # Regalos no streakable se procesan inmediatamente
                        total_value = event.gift.count * event.gift.diamond_count
                        
                        logger.info(
                            f"Donación recibida: {event.user.nickname} envió {event.gift.name} "
                            f"(Total: {total_value} coins)"
                        )
                        
                        if auction_id in self.donation_callbacks:
                            self.donation_callbacks[auction_id](
                                event.user.nickname,
                                float(total_value),
                                event.gift.name
                            )
                            
                except Exception as e:
                    logger.error(f"Error procesando donación: {e}")
            
            # Handler para conexión exitosa
            @client.on(ConnectEvent)
            async def on_connect(event: ConnectEvent):
                logger.info(f"Conectado al stream de @{username}")
            
            # Handler para desconexión
            @client.on(DisconnectEvent)
            async def on_disconnect(event: DisconnectEvent):
                logger.info(f"Desconectado del stream de @{username}")
            
            # Guardar cliente
            self.clients[auction_id] = client
            
            # Iniciar conexión (no bloqueante)
            asyncio.create_task(client.start())
            
            logger.info(f"Iniciando conexión con TikTok Live: @{username}")
            return True
            
        except Exception as e:
            logger.error(f"Error conectando a TikTok Live: {e}")
            return False
    
    async def disconnect(self, auction_id: str) -> None:
        """
        Desconecta del stream de TikTok Live
        
        Args:
            auction_id: ID de la subasta asociada
        """
        try:
            if auction_id in self.clients:
                client = self.clients[auction_id]
                await client.stop()
                del self.clients[auction_id]
                
            if auction_id in self.donation_callbacks:
                del self.donation_callbacks[auction_id]
                
            logger.info(f"Desconectado de TikTok Live para subasta {auction_id}")
            
        except Exception as e:
            logger.error(f"Error desconectando de TikTok Live: {e}")
    
    async def disconnect_all(self) -> None:
        """Desconecta todos los streams activos"""
        auction_ids = list(self.clients.keys())
        for auction_id in auction_ids:
            await self.disconnect(auction_id)
    
    def is_connected(self, auction_id: str) -> bool:
        """Verifica si hay una conexión activa para una subasta"""
        return auction_id in self.clients
    
    def get_active_connections(self) -> int:
        """Retorna el número de conexiones activas"""
        return len(self.clients)
