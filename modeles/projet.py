"""
Modèle de projet pour gérer les données de projet
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

class Projet:
    # Constantes de statut
    STATUT_ACTIF = "Actif"
    STATUT_TERMINE = "Terminé"
    STATUT_EN_ATTENTE = "En Attente"
    
    def __init__(self, nom: str, description: str = "", date_debut: str = "", date_fin: str = "",cree_par: str = ""):
        self.id: Optional[int] = None  # Sera défini par la base de données
        self.nom = nom
        self.description = description
        self.statut = self.STATUT_ACTIF
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.cree_par = cree_par
        self.cree_le = datetime.now().isoformat()
        self.mis_a_jour_le = datetime.now().isoformat()
        
    def vers_dict(self) -> Dict[str, Any]:
        """Convertir le projet en dictionnaire pour la sérialisation JSON"""
        return {
            'id': self.id,
            'nom': self.nom,
            'description': self.description,
            'statut': self.statut,
            'date_debut': self.date_debut,
            'date_fin': self.date_fin,
            'cree_le': self.cree_le,
            'mis_a_jour_le': self.mis_a_jour_le
        }
    
    @classmethod
    def depuis_dict(cls, donnees: Dict[str, Any]) -> 'Projet':
        """Créer une instance de projet depuis un dictionnaire (compatibilité JSON)"""
        projet = cls(
            nom=donnees['nom'],
            description=donnees.get('description', ''),
            date_debut=donnees.get('date_debut', ''),
            date_fin=donnees.get('date_fin', '')
        )
        projet.id = donnees.get('id')
        projet.cree_le = donnees.get('cree_le', datetime.now().isoformat())
        projet.mis_a_jour_le = donnees.get('mis_a_jour_le', datetime.now().isoformat())
        projet.statut = donnees.get('statut', cls.STATUT_ACTIF)
        return projet
    
    @classmethod
    def depuis_ligne_db(cls, ligne: Dict[str, Any]) -> 'Projet':
        """Créer une instance de projet depuis une ligne de base de données"""
        projet = cls(
            nom=ligne['nom'],
            description=ligne.get('description', ''),
            date_debut=ligne.get('date_debut', ''),
            date_fin=ligne.get('date_fin', '')
        )
        projet.id = ligne['id']
        projet.statut = ligne.get('statut', cls.STATUT_ACTIF)
        projet.cree_le = ligne.get('cree_le', datetime.now().isoformat())
        projet.mis_a_jour_le = ligne.get('mis_a_jour_le', datetime.now().isoformat())
        return projet
    
    def __str__(self):
        return f"Projet({self.nom})"
