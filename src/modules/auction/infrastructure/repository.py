"""
Repositorio en memoria para gestionar subastas
En producción, esto podría ser una base de datos
"""
from typing import Dict, Optional, List
from ..domain.auction import Auction


class AuctionRepository:
    """Repositorio para persistir y recuperar subastas"""
    
    def __init__(self):
        self._auctions: Dict[str, Auction] = {}
        
    def save(self, auction: Auction) -> None:
        """Guarda o actualiza una subasta"""
        self._auctions[auction.id] = auction
        
    def find_by_id(self, auction_id: str) -> Optional[Auction]:
        """Busca una subasta por ID"""
        return self._auctions.get(auction_id)
        
    def find_all(self) -> List[Auction]:
        """Obtiene todas las subastas"""
        return list(self._auctions.values())
        
    def delete(self, auction_id: str) -> bool:
        """Elimina una subasta"""
        if auction_id in self._auctions:
            del self._auctions[auction_id]
            return True
        return False
        
    def exists(self, auction_id: str) -> bool:
        """Verifica si existe una subasta"""
        return auction_id in self._auctions
