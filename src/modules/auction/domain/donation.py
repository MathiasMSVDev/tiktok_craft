"""
Entidad de dominio: Donation (Donación)
Representa una donación de un usuario en TikTok Live
"""
from datetime import datetime
from typing import Dict, List, Optional


class Donation:
    """
    Entidad que representa una donación individual
    """
    
    def __init__(
        self,
        username: str,
        amount: float,
        gift_name: Optional[str] = None,
        profile_picture: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self.username = username
        self.amount = amount
        self.gift_name = gift_name
        self.profile_picture = profile_picture
        self.timestamp = timestamp or datetime.now()
        
    def to_dict(self) -> dict:
        """Convierte la donación a diccionario"""
        return {
            "username": self.username,
            "amount": self.amount,
            "giftName": self.gift_name,
            "profilePicture": self.profile_picture,
            "timestamp": self.timestamp.isoformat()
        }


class DonorStats:
    """
    Estadísticas acumuladas de un donador
    """
    
    def __init__(self, username: str, profile_picture: Optional[str] = None):
        self.username = username
        self.profile_picture = profile_picture
        self.total_amount: float = 0.0
        self.donation_count: int = 0
        self.last_donation: Optional[datetime] = None
        self.donations: List[Donation] = []
        
    def add_donation(self, donation: Donation) -> None:
        """Agrega una nueva donación"""
        self.total_amount += donation.amount
        self.donation_count += 1
        self.last_donation = donation.timestamp
        self.donations.append(donation)
        # Actualizar foto de perfil si viene en la donación
        if donation.profile_picture:
            self.profile_picture = donation.profile_picture
        
    def to_dict(self, rank: int = 0) -> dict:
        """Convierte las estadísticas a diccionario"""
        return {
            "username": self.username,
            "profilePicture": self.profile_picture,
            "totalAmount": self.total_amount,
            "donationCount": self.donation_count,
            "lastDonation": self.last_donation.isoformat() if self.last_donation else None,
            "rank": rank
        }


class DonationTracker:
    """
    Gestor de donaciones para una subasta
    Mantiene el tracking de donadores y sus estadísticas
    """
    
    def __init__(self, auction_id: str):
        self.auction_id = auction_id
        self.donors: Dict[str, DonorStats] = {}
        self.all_donations: List[Donation] = []
        
    def add_donation(self, username: str, amount: float, gift_name: Optional[str] = None, profile_picture: Optional[str] = None) -> Donation:
        """
        Registra una nueva donación
        """
        donation = Donation(username, amount, gift_name, profile_picture)
        
        # Crear o actualizar estadísticas del donador
        if username not in self.donors:
            self.donors[username] = DonorStats(username, profile_picture)
            
        self.donors[username].add_donation(donation)
        self.all_donations.append(donation)
        
        return donation
        
    def get_top_donors(self, limit: int = 5) -> List[DonorStats]:
        """
        Obtiene el top N de donadores ordenados por monto total
        """
        sorted_donors = sorted(
            self.donors.values(),
            key=lambda d: d.total_amount,
            reverse=True
        )
        return sorted_donors[:limit]
        
    def get_total_donations(self) -> float:
        """Retorna el total de donaciones acumuladas"""
        return sum(donor.total_amount for donor in self.donors.values())
        
    def get_total_donors(self) -> int:
        """Retorna el número de donadores únicos"""
        return len(self.donors)
        
    def get_donor_stats(self, username: str) -> Optional[DonorStats]:
        """Obtiene las estadísticas de un donador específico"""
        return self.donors.get(username)
        
    def reset(self) -> None:
        """Limpia todas las donaciones y estadísticas"""
        self.donors.clear()
        self.all_donations.clear()
        
    def to_dict(self) -> dict:
        """Convierte el tracker a diccionario"""
        top_donors = self.get_top_donors(5)
        
        return {
            "auctionId": self.auction_id,
            "topDonors": [
                donor.to_dict(rank=idx + 1) 
                for idx, donor in enumerate(top_donors)
            ],
            "totalDonations": self.get_total_donations(),
            "totalDonors": self.get_total_donors()
        }
