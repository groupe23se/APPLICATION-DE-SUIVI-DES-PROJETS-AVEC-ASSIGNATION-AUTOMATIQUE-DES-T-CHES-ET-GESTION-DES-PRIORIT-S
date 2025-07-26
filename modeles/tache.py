"""
Modèle de tâche pour gérer les données de tâche
"""

from datetime import datetime
from typing import Dict, Any, Optional, List

class Tache:
    # Niveaux de priorité
    PRIORITE_HAUTE = "Haute"
    PRIORITE_MOYENNE = "Moyenne"
    PRIORITE_BASSE = "Basse"
    
    # Options de statut
    STATUT_A_FAIRE = "À faire"
    STATUT_EN_COURS = "En cours"
    STATUT_TERMINE = "Terminé"
    
    def __init__(self, titre: str, description: str = "", id_projet: Optional[int] = None, 
                 priorite: str = PRIORITE_MOYENNE, echeance: str = ""):
        self.id: Optional[int] = None  # Sera défini par la base de données
        self.titre = titre
        self.description = description
        self.id_projet = id_projet
        self.priorite = priorite
        self.statut = self.STATUT_A_FAIRE
        self.assigne_a: Optional[int] = None  # ID du membre d'équipe
        self.echeance = echeance
        self.heures_estimees = 0
        self.competences_requises: List[str] = []  # Liste des compétences requises pour cette tâche
        self.cree_le = datetime.now().isoformat()
        self.mis_a_jour_le = datetime.now().isoformat()
        
    def vers_dict(self) -> Dict[str, Any]:
        """Convertir la tâche en dictionnaire pour la sérialisation JSON"""
        return {
            'id': self.id,
            'titre': self.titre,
            'description': self.description,
            'id_projet': self.id_projet,
            'priorite': self.priorite,
            'statut': self.statut,
            'assigne_a': self.assigne_a,
            'echeance': self.echeance,
            'heures_estimees': self.heures_estimees,
            'competences_requises': self.competences_requises,
            'cree_le': self.cree_le,
            'mis_a_jour_le': self.mis_a_jour_le
        }
    
    @classmethod
    def depuis_dict(cls, donnees: Dict[str, Any]) -> 'Tache':
        """Créer une instance de tâche depuis un dictionnaire (compatibilité JSON)"""
        tache = cls(
            titre=donnees['titre'],
            description=donnees.get('description', ''),
            id_projet=donnees.get('id_projet'),
            priorite=donnees.get('priorite', cls.PRIORITE_MOYENNE),
            echeance=donnees.get('echeance', '')
        )
        tache.id = donnees.get('id')
        tache.statut = donnees.get('statut', cls.STATUT_A_FAIRE)
        tache.assigne_a = donnees.get('assigne_a')
        tache.heures_estimees = donnees.get('heures_estimees', 0)
        tache.competences_requises = donnees.get('competences_requises', [])
        tache.cree_le = donnees.get('cree_le', datetime.now().isoformat())
        tache.mis_a_jour_le = donnees.get('mis_a_jour_le', datetime.now().isoformat())
        return tache
    
    @classmethod
    def depuis_ligne_db(cls, ligne: Dict[str, Any]) -> 'Tache':
        """Créer une instance de tâche depuis une ligne de base de données"""
        tache = cls(
            titre=ligne['titre'],
            description=ligne.get('description', ''),
            id_projet=ligne.get('id_projet'),
            priorite=ligne.get('priorite', cls.PRIORITE_MOYENNE),
            echeance=ligne.get('echeance', '')
        )
        tache.id = ligne['id']
        tache.statut = ligne.get('statut', cls.STATUT_A_FAIRE)
        tache.assigne_a = ligne.get('assigne_a')
        tache.heures_estimees = ligne.get('heures_estimees', 0)
        tache.cree_le = ligne.get('cree_le', datetime.now().isoformat())
        tache.mis_a_jour_le = ligne.get('mis_a_jour_le', datetime.now().isoformat())
        return tache
    
    def marquer_termine(self):
        """Marquer la tâche comme terminée"""
        self.statut = self.STATUT_TERMINE
        self.mis_a_jour_le = datetime.now().isoformat()
    
    def assigner_a(self, id_membre: int):
        """Assigner la tâche à un membre d'équipe"""
        self.assigne_a = id_membre
        if self.statut == self.STATUT_A_FAIRE:
            self.statut = self.STATUT_EN_COURS
        self.mis_a_jour_le = datetime.now().isoformat()
    
    def obtenir_poids_priorite(self) -> int:
        """Obtenir le poids numérique pour la priorité (pour le tri)"""
        poids = {
            self.PRIORITE_HAUTE: 3,
            self.PRIORITE_MOYENNE: 2,
            self.PRIORITE_BASSE: 1
        }
        return poids.get(self.priorite, 2)
    
    def __str__(self):
        return f"Tache({self.titre} - {self.priorite})"
