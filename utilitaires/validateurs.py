"""
Utilitaires de validation des entrées
"""

import re
from datetime import datetime
from typing import Optional

class Validateurs:
    @staticmethod
    def valider_email(email: str) -> bool:
        """Valider le format d'email"""
        if not email:
            return True  # Email vide est autorisé
        
        motif = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(motif, email) is not None
    
    @staticmethod
    def valider_longueur_texte(texte: str, longueur_min: int = 0, longueur_max: int = 1000) -> bool:
        """Valider la longueur du texte"""
        if not isinstance(texte, str):
            return False
        
        longueur = len(texte.strip())
        return longueur_min <= longueur <= longueur_max
    
    @staticmethod
    def valider_date(chaine_date: str) -> bool:
        """Valider le format de date (YYYY-MM-DD)"""
        if not chaine_date:
            return True  # Date vide est autorisée
        
        try:
            datetime.strptime(chaine_date, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    @staticmethod
    def valider_entier(valeur: str, valeur_min: int = None, valeur_max: int = None) -> bool:
        """Valider la valeur entière"""
        try:
            valeur_entiere = int(valeur)
            
            if valeur_min is not None and valeur_entiere < valeur_min:
                return False
            
            if valeur_max is not None and valeur_entiere > valeur_max:
                return False
            
            return True
        except ValueError:
            return False
    
    @staticmethod
    def valider_pourcentage(valeur: str) -> bool:
        """Valider la valeur de pourcentage (0-100)"""
        return Validateurs.valider_entier(valeur, 0, 100)
    
    @staticmethod
    def valider_champ_requis(valeur: str) -> bool:
        """Valider qu'un champ requis n'est pas vide"""
        return bool(valeur and valeur.strip())
    
    @staticmethod
    def nettoyer_texte(texte: str) -> str:
        """Nettoyer l'entrée de texte en supprimant/échappant les caractères potentiellement dangereux"""
        if not isinstance(texte, str):
            return ""
        
        # Supprimer les caractères de contrôle sauf tabulation, nouvelle ligne et retour chariot
        nettoye = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', texte)
        
        # Limiter les sauts de ligne
        nettoye = re.sub(r'\n{3,}', '\n\n', nettoye)
        
        return nettoye.strip()
    
    @staticmethod
    def valider_nom_competence(competence: str) -> bool:
        """Valider le format du nom de compétence"""
        if not competence or not competence.strip():
            return False
        
        # La compétence doit être alphanumérique avec espaces, tirets et signes plus
        motif = r'^[a-zA-Z0-9\s\-\+\.#]+$'
        return re.match(motif, competence.strip()) is not None and len(competence.strip()) <= 50
    
    @staticmethod
    def valider_nom_projet(nom: str) -> bool:
        """Valider le nom de projet"""
        return (Validateurs.valider_champ_requis(nom) and 
                Validateurs.valider_longueur_texte(nom, 1, 100))
    
    @staticmethod
    def valider_titre_tache(titre: str) -> bool:
        """Valider le titre de tâche"""
        return (Validateurs.valider_champ_requis(titre) and 
                Validateurs.valider_longueur_texte(titre, 1, 200))
    
    @staticmethod
    def valider_nom_membre(nom: str) -> bool:
        """Valider le nom du membre d'équipe"""
        return (Validateurs.valider_champ_requis(nom) and 
                Validateurs.valider_longueur_texte(nom, 1, 100))
