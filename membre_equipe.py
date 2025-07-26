"""
Modèle de membre d'équipe pour gérer les données des membres d'équipe
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

class MembreEquipe:
    def __init__(self, nom: str, email: str = "", role: str = ""):
        self.id: Optional[int] = None  # Sera défini par la base de données
        self.nom = nom
        self.email = email
        self.role = role
        self.competences: List[str] = []  # Liste des compétences
        self.disponibilite = 100  # Pourcentage de disponibilité (0-100)
        self.taches_actuelles: List[int] = []  # Liste des IDs de tâches actuellement assignées
        self.charge_travail_heures = 0  # Charge de travail actuelle en heures
        self.heures_max_par_semaine = 40  # Heures maximum par semaine
        self.cree_le = datetime.now().isoformat()
        self.mis_a_jour_le = datetime.now().isoformat()
        
    def vers_dict(self) -> Dict[str, Any]:
        """Convertir le membre d'équipe en dictionnaire pour la sérialisation JSON"""
        return {
            'id': self.id,
            'nom': self.nom,
            'email': self.email,
            'role': self.role,
            'competences': self.competences,
            'disponibilite': self.disponibilite,
            'taches_actuelles': self.taches_actuelles,
            'charge_travail_heures': self.charge_travail_heures,
            'heures_max_par_semaine': self.heures_max_par_semaine,
            'cree_le': self.cree_le,
            'mis_a_jour_le': self.mis_a_jour_le
        }
    
    @classmethod
    def depuis_dict(cls, donnees: Dict[str, Any]) -> 'MembreEquipe':
        """Créer une instance de membre d'équipe depuis un dictionnaire (compatibilité JSON)"""
        membre = cls(
            nom=donnees['nom'],
            email=donnees.get('email', ''),
            role=donnees.get('role', '')
        )
        membre.id = donnees.get('id')
        membre.competences = donnees.get('competences', [])
        membre.disponibilite = donnees.get('disponibilite', 100)
        membre.taches_actuelles = donnees.get('taches_actuelles', [])
        membre.charge_travail_heures = donnees.get('charge_travail_heures', 0)
        membre.heures_max_par_semaine = donnees.get('heures_max_par_semaine', 40)
        membre.cree_le = donnees.get('cree_le', datetime.now().isoformat())
        membre.mis_a_jour_le = donnees.get('mis_a_jour_le', datetime.now().isoformat())
        return membre
    
    @classmethod
    def depuis_ligne_db(cls, ligne: Dict[str, Any]) -> 'MembreEquipe':
        """Créer une instance de membre d'équipe depuis une ligne de base de données"""
        membre = cls(
            nom=ligne['nom'],
            email=ligne.get('email', ''),
            role=ligne.get('role', '')
        )
        membre.id = ligne['id']
        membre.disponibilite = ligne.get('disponibilite', 100)
        membre.charge_travail_heures = ligne.get('charge_travail_heures', 0)
        membre.heures_max_par_semaine = ligne.get('heures_max_par_semaine', 40)
        membre.cree_le = ligne.get('cree_le', datetime.now().isoformat())
        membre.mis_a_jour_le = ligne.get('mis_a_jour_le', datetime.now().isoformat())
        return membre
    
    def ajouter_competence(self, competence: str):
        """Ajouter une compétence au membre d'équipe"""
        if competence and competence not in self.competences:
            self.competences.append(competence)
            self.mis_a_jour_le = datetime.now().isoformat()
    
    def supprimer_competence(self, competence: str):
        """Supprimer une compétence du membre d'équipe"""
        if competence in self.competences:
            self.competences.remove(competence)
            self.mis_a_jour_le = datetime.now().isoformat()
    
    def assigner_tache(self, id_tache: int, heures_estimees: int = 0):
        """Assigner une tâche à ce membre d'équipe"""
        if id_tache not in self.taches_actuelles:
            self.taches_actuelles.append(id_tache)
            self.charge_travail_heures += heures_estimees
            self.mis_a_jour_le = datetime.now().isoformat()
    
    def desassigner_tache(self, id_tache: int, heures_estimees: int = 0):
        """Désassigner une tâche de ce membre d'équipe"""
        if id_tache in self.taches_actuelles:
            self.taches_actuelles.remove(id_tache)
            self.charge_travail_heures = max(0, self.charge_travail_heures - heures_estimees)
            self.mis_a_jour_le = datetime.now().isoformat()
    
    def obtenir_score_disponibilite(self) -> float:
        """Calculer le score de disponibilité basé sur la charge de travail actuelle"""
        if self.heures_max_par_semaine == 0:
            return 0.0
        
        utilisation = self.charge_travail_heures / self.heures_max_par_semaine
        facteur_disponibilite = self.disponibilite / 100.0
        
        # Le score diminue quand l'utilisation augmente
        score = facteur_disponibilite * (1.0 - min(utilisation, 1.0))
        return max(0.0, score)
    
    def a_competences_requises(self, competences_requises: List[str]) -> bool:
        """Vérifier si le membre d'équipe a toutes les compétences requises"""
        if not competences_requises:
            return True
        return all(competence in self.competences for competence in competences_requises)
    
    def __str__(self):
        return f"MembreEquipe({self.nom} - {self.role})"