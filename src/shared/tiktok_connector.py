"""
Adaptador compartido para conectar con TikTok Live
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
    Conector compartido para TikTok Live que captura eventos de donaciones
    Puede ser utilizado por múltiples módulos del sistema
    """
    
    def __init__(self):
        self.clients: Dict[str, TikTokLiveClient] = {}
        self.donation_callbacks: Dict[str, Callable] = {}
        
    async def connect(
        self,
        username: str,
        session_id: str,
        on_donation: Callable[[str, float, str, str], None]
    ) -> bool:
        """
        Conecta al stream de TikTok Live de un usuario
        
        Args:
            username: Nombre del streamer en TikTok (sin @)
            session_id: ID único de la sesión (ej: auction_id, event_id, etc.)
            on_donation: Callback que se ejecuta cuando hay una donación
                        Recibe (username, amount, gift_name, profile_picture_url)
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            # Limpiar el username (quitar @ si está presente)
            clean_username = username.lstrip('@')
            
            # Crear cliente de TikTok Live
            client = TikTokLiveClient(unique_id=f"@{clean_username}")
            
            # Registrar callback de donación
            self.donation_callbacks[session_id] = on_donation
            
            # Handler para eventos de regalo (donaciones)
            @client.on(GiftEvent)
            async def on_gift(event: GiftEvent):
                try:
                    # Obtener información del regalo y usuario
                    gift = event.gift
                    user = event.user
                    
                    # Obtener atributos del regalo de forma segura
                    gift_name = getattr(gift, 'name', 'Regalo desconocido')
                    gift_id = getattr(gift, 'id', 0)
                    
                    # Obtener el valor del regalo (diamond_count puede estar en diferentes lugares)
                    diamond_count = getattr(gift, 'diamond_count', 0)
                    if diamond_count == 0:
                        diamond_count = getattr(gift, 'diamonds', 0)
                    if diamond_count == 0:
                        diamond_count = getattr(gift, 'value', 1)
                    
                    # Obtener la cantidad de regalos enviados
                    count = getattr(event, 'count', 1)
                    if count == 0:
                        count = getattr(gift, 'count', 1)
                    
                    # Calcular el valor total en coins
                    total_value = count * diamond_count
                    
                    # Log detallado del cálculo
                    logger.info(f"💎 DONACIÓN RECIBIDA:")
                    logger.info(f"   Regalo: {gift_name} (ID: {gift_id})")
                    logger.info(f"   Valor unitario: {diamond_count} diamonds")
                    logger.info(f"   Cantidad: {count}")
                    logger.info(f"   Total calculado: {total_value} coins ({count} × {diamond_count})")
                    
                    # Obtener nickname del usuario
                    username = getattr(user, 'nickname', 'Usuario desconocido')
                    unique_id = getattr(user, 'unique_id', '')
                    if not username or username == 'Usuario desconocido':
                        username = unique_id if unique_id else 'Usuario desconocido'
                    
                    # Obtener foto de perfil del usuario
                    # En TikTokLive Python, los objetos ImageModel usan m_urls (no url_list como en TypeScript)
                    profile_picture = ''
                    
                    # Intentar extraer desde avatar_thumb (prioridad 1)
                    try:
                        if hasattr(user, 'avatar_thumb') and user.avatar_thumb:
                            avatar = user.avatar_thumb
                            
                            # ImageModel usa m_urls en lugar de url_list
                            if hasattr(avatar, 'm_urls') and avatar.m_urls:
                                urls = avatar.m_urls
                                if urls and len(urls) > 0:
                                    profile_picture = str(urls[0])
                                    logger.info(f"✅ Avatar extraído de avatar_thumb: {profile_picture[:80]}...")
                    except Exception as e:
                        logger.error(f"❌ Error extrayendo avatar_thumb: {e}")
                    
                    # Intentar extraer desde avatar_medium (prioridad 2)
                    if not profile_picture:
                        try:
                            if hasattr(user, 'avatar_medium') and user.avatar_medium:
                                avatar = user.avatar_medium
                                if hasattr(avatar, 'm_urls') and avatar.m_urls:
                                    profile_picture = str(avatar.m_urls[0])
                                    logger.info(f"✅ Avatar extraído de avatar_medium: {profile_picture[:80]}...")
                        except Exception as e:
                            logger.error(f"❌ Error extrayendo avatar_medium: {e}")
                    
                    # Intentar extraer desde avatar_large (prioridad 3)
                    if not profile_picture:
                        try:
                            if hasattr(user, 'avatar_large') and user.avatar_large:
                                avatar = user.avatar_large
                                if hasattr(avatar, 'm_urls') and avatar.m_urls:
                                    profile_picture = str(avatar.m_urls[0])
                                    logger.info(f"✅ Avatar extraído de avatar_large: {profile_picture[:80]}...")
                        except Exception as e:
                            logger.error(f"❌ Error extrayendo avatar_large: {e}")
                    
                    # Log de warning si no se pudo extraer
                    if not profile_picture:
                        logger.warning(f"⚠️ No se pudo extraer avatar para {username}")
                        logger.warning(f"⚠️ Usando avatar generado automáticamente")
                    
                    logger.info(f"👤 Usuario: {username} (@{unique_id})")
                    if profile_picture:
                        logger.info(f"🖼️  Avatar: {profile_picture[:80]}...")
                    
                    # Ejecutar callback si hay valor
                    if session_id in self.donation_callbacks and total_value > 0:
                        logger.info(f"✅ Registrando {total_value} coins para {username}")
                        self.donation_callbacks[session_id](
                            username,
                            float(total_value),
                            gift_name,
                            profile_picture
                        )
                    else:
                        if total_value == 0:
                            logger.warning(f"⚠️ Donación con valor 0 ignorada")
                        if session_id not in self.donation_callbacks:
                            logger.warning(f"⚠️ No hay callback registrado para sesión {session_id}")
                            
                except Exception as e:
                    logger.error(f"Error procesando donación: {e}")
                    # Imprimir más detalles para debugging
                    try:
                        logger.error(f"Tipo de evento: {type(event)}")
                        logger.error(f"Atributos del evento: {dir(event)}")
                        if hasattr(event, 'gift'):
                            logger.error(f"Tipo de regalo: {type(event.gift)}")
                            logger.error(f"Atributos del regalo: {dir(event.gift)}")
                        if hasattr(event, 'user'):
                            logger.error(f"Tipo de usuario: {type(event.user)}")
                            logger.error(f"Atributos del usuario: {dir(event.user)}")
                            # Intentar serializar el usuario completo
                            if hasattr(event.user, '__dict__'):
                                logger.error(f"Dict del usuario: {event.user.__dict__}")
                    except Exception as debug_error:
                        logger.error(f"Error en debugging: {debug_error}")
            
            # Handler para conexión exitosa
            @client.on(ConnectEvent)
            async def on_connect(event: ConnectEvent):
                logger.info(f"✅ Conectado exitosamente al stream de @{clean_username}")
            
            # Handler para desconexión
            @client.on(DisconnectEvent)
            async def on_disconnect(event: DisconnectEvent):
                logger.info(f"⚠️ Desconectado del stream de @{clean_username}")
            
            # Guardar cliente
            self.clients[session_id] = client
            
            # Iniciar conexión en segundo plano (no bloqueante)
            async def start_client():
                try:
                    logger.info(f"🔄 Intentando conectar con TikTok Live: @{clean_username}")
                    await client.start()
                except Exception as e:
                    logger.error(f"❌ Error en la conexión con TikTok Live (@{clean_username}): {e}")
                    logger.error(f"   Razones posibles:")
                    logger.error(f"   - El usuario no está en transmisión en vivo")
                    logger.error(f"   - El nombre de usuario es incorrecto")
                    logger.error(f"   - Problemas de red o timeout")
                    logger.error(f"   - Restricciones de privacidad del streamer")
                    # Limpiar cliente fallido
                    if session_id in self.clients:
                        del self.clients[session_id]
                    if session_id in self.donation_callbacks:
                        del self.donation_callbacks[session_id]
            
            asyncio.create_task(start_client())
            
            logger.info(f"📡 Conexión iniciada con @{clean_username} (sesión: {session_id[:8]}...)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al inicializar conexión con TikTok Live: {e}")
            return False
    
    async def disconnect(self, session_id: str) -> None:
        """
        Desconecta del stream de TikTok Live
        
        Args:
            session_id: ID de la sesión asociada
        """
        try:
            if session_id in self.clients:
                client = self.clients[session_id]
                await client.stop()
                del self.clients[session_id]
                
            if session_id in self.donation_callbacks:
                del self.donation_callbacks[session_id]
                
            logger.info(f"Desconectado de TikTok Live para sesión {session_id}")
            
        except Exception as e:
            logger.error(f"Error desconectando de TikTok Live: {e}")
    
    async def disconnect_all(self) -> None:
        """Desconecta todos los streams activos"""
        session_ids = list(self.clients.keys())
        for session_id in session_ids:
            await self.disconnect(session_id)
    
    def is_connected(self, session_id: str) -> bool:
        """Verifica si hay una conexión activa para una sesión"""
        return session_id in self.clients
    
    def get_active_connections(self) -> int:
        """Retorna el número de conexiones activas"""
        return len(self.clients)
    
    def get_connected_sessions(self) -> list[str]:
        """Retorna la lista de sesiones conectadas"""
        return list(self.clients.keys())


# Instancia global compartida del conector
tiktok_connector = TikTokLiveConnector()
