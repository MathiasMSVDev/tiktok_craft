"""
Manager de WebSocket para comunicación en tiempo real
"""
from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio


class ConnectionManager:
    """Gestiona las conexiones WebSocket activas"""
    
    def __init__(self):
        # Diccionario: auction_id -> lista de WebSockets conectados
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, auction_id: str):
        """Conecta un cliente WebSocket a una subasta específica"""
        await websocket.accept()
        if auction_id not in self.active_connections:
            self.active_connections[auction_id] = []
        self.active_connections[auction_id].append(websocket)
        
    def disconnect(self, websocket: WebSocket, auction_id: str):
        """Desconecta un cliente WebSocket"""
        if auction_id in self.active_connections:
            if websocket in self.active_connections[auction_id]:
                self.active_connections[auction_id].remove(websocket)
            # Limpiar si no quedan conexiones
            if not self.active_connections[auction_id]:
                del self.active_connections[auction_id]
                
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Envía un mensaje a un cliente específico"""
        await websocket.send_json(message)
        
    async def broadcast(self, message: dict, auction_id: str):
        """Envía un mensaje a todos los clientes conectados a una subasta"""
        if auction_id in self.active_connections:
            # Crear una copia de la lista para evitar problemas si se desconecta durante el broadcast
            connections = self.active_connections[auction_id].copy()
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    # Si falla el envío, desconectar el cliente
                    print(f"Error enviando mensaje: {e}")
                    self.disconnect(connection, auction_id)
                    
    async def broadcast_time_update(self, auction_id: str, remaining_seconds: int):
        """Envía actualización de tiempo a todos los clientes"""
        message = {
            "type": "time_update",
            "auctionId": auction_id,
            "data": {
                "remainingSeconds": remaining_seconds
            }
        }
        await self.broadcast(message, auction_id)
        
    async def broadcast_status_change(self, auction_id: str, status: str):
        """Envía cambio de estado a todos los clientes"""
        message = {
            "type": "status_change",
            "auctionId": auction_id,
            "data": {
                "status": status
            }
        }
        await self.broadcast(message, auction_id)
    
    async def broadcast_donation_update(self, auction_id: str, donation_data: dict):
        """Envía actualización de donaciones a todos los clientes"""
        message = {
            "type": "donation_update",
            "auctionId": auction_id,
            "data": donation_data
        }
        await self.broadcast(message, auction_id)
        
    def get_connections_count(self, auction_id: str) -> int:
        """Obtiene el número de conexiones activas para una subasta"""
        return len(self.active_connections.get(auction_id, []))


# Instancia global del manager
websocket_manager = ConnectionManager()
