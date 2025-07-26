"""
Gestionnaire de données pour l'application de suivi des projets
Gère la persistance des données en utilisant SQLite
"""

from typing import List, Optional
from modeles.base_donnees import BaseDonnees
from modeles.projet import Projet
from modeles.tache import Tache
from modeles.membre_equipe import MembreEquipe

class GestionnaireDonnees:
    def __init__(self, chemin_db='donnees/suivi_projets.db'):
        """Initialiser le gestionnaire de données avec SQLite"""
        self.db = BaseDonnees(chemin_db)
    
    # Méthodes pour les projets
    def charger_projets(self) -> List[Projet]:
        """Charger tous les projets"""
        lignes = self.db.executer_requete('''
            SELECT id, nom, description, statut, date_debut, date_fin, cree_le, mis_a_jour_le
            FROM projets ORDER BY cree_le DESC
        ''')
        return [Projet.depuis_ligne_db(dict(ligne)) for ligne in lignes]
    
    def ajouter_projet(self, projet: Projet):
        """Ajouter un nouveau projet"""
        maintenant = self.db.maintenant()
        id_nouveau = self.db.executer_modification('''
            INSERT INTO projets (nom, description, statut, date_debut, date_fin, cree_le, mis_a_jour_le)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (projet.nom, projet.description, projet.statut, projet.date_debut, 
              projet.date_fin, maintenant, maintenant))
        projet.id = id_nouveau
        projet.cree_le = maintenant
        projet.mis_a_jour_le = maintenant
    
    def mettre_a_jour_projet(self, projet: Projet):
        """Mettre à jour un projet existant"""
        maintenant = self.db.maintenant()
        self.db.executer_modification('''
            UPDATE projets 
            SET nom=?, description=?, statut=?, date_debut=?, date_fin=?, mis_a_jour_le=?
            WHERE id=?
        ''', (projet.nom, projet.description, projet.statut, projet.date_debut,
              projet.date_fin, maintenant, projet.id))
        projet.mis_a_jour_le = maintenant
    
    def supprimer_projet(self, id_projet: int):
        """Supprimer un projet"""
        self.db.executer_modification('DELETE FROM projets WHERE id=?', (id_projet,))
    
    def obtenir_projet(self, id_projet: int) -> Optional[Projet]:
        """Obtenir un projet par son ID"""
        lignes = self.db.executer_requete('''
            SELECT id, nom, description, statut, date_debut, date_fin, cree_le, mis_a_jour_le
            FROM projets WHERE id=?
        ''', (id_projet,))
        if lignes:
            return Projet.depuis_ligne_db(dict(lignes[0]))
        return None
    
    # Méthodes pour les tâches
    def charger_taches(self) -> List[Tache]:
        """Charger toutes les tâches avec leurs compétences"""
        lignes = self.db.executer_requete('''
            SELECT t.id, t.titre, t.description, t.id_projet, t.priorite, t.statut,
                   t.assigne_a, t.echeance, t.heures_estimees, t.cree_le, t.mis_a_jour_le
            FROM taches t ORDER BY t.cree_le DESC
        ''')
        
        taches = []
        for ligne in lignes:
            tache = Tache.depuis_ligne_db(dict(ligne))
            # Charger les compétences requises
            competences = self.db.executer_requete('''
                SELECT competence FROM competences_taches WHERE tache_id=?
            ''', (tache.id,))
            tache.competences_requises = [comp[0] for comp in competences]
            taches.append(tache)
        
        return taches
    
    def ajouter_tache(self, tache: Tache):
        """Ajouter une nouvelle tâche"""
        maintenant = self.db.maintenant()
        id_nouveau = self.db.executer_modification('''
            INSERT INTO taches (titre, description, id_projet, priorite, statut, assigne_a, 
                               echeance, heures_estimees, cree_le, mis_a_jour_le)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tache.titre, tache.description, tache.id_projet, tache.priorite,
              tache.statut, tache.assigne_a, tache.echeance, tache.heures_estimees,
              maintenant, maintenant))
        
        tache.id = id_nouveau
        tache.cree_le = maintenant
        tache.mis_a_jour_le = maintenant
        
        # Ajouter les compétences requises
        if tache.competences_requises:
            for competence in tache.competences_requises:
                self.db.executer_modification('''
                    INSERT INTO competences_taches (tache_id, competence) VALUES (?, ?)
                ''', (id_nouveau, competence))
    
    def mettre_a_jour_tache(self, tache: Tache):
        """Mettre à jour une tâche existante"""
        maintenant = self.db.maintenant()
        self.db.executer_modification('''
            UPDATE taches 
            SET titre=?, description=?, id_projet=?, priorite=?, statut=?, assigne_a=?,
                echeance=?, heures_estimees=?, mis_a_jour_le=?
            WHERE id=?
        ''', (tache.titre, tache.description, tache.id_projet, tache.priorite,
              tache.statut, tache.assigne_a, tache.echeance, tache.heures_estimees,
              maintenant, tache.id))
        
        # Mettre à jour les compétences
        self.db.executer_modification('DELETE FROM competences_taches WHERE tache_id=?', (tache.id,))
        if tache.competences_requises:
            for competence in tache.competences_requises:
                self.db.executer_modification('''
                    INSERT INTO competences_taches (tache_id, competence) VALUES (?, ?)
                ''', (tache.id, competence))
        
        tache.mis_a_jour_le = maintenant
    
    def supprimer_tache(self, id_tache: int):
        """Supprimer une tâche"""
        self.db.executer_modification('DELETE FROM taches WHERE id=?', (id_tache,))
    
    def obtenir_tache(self, id_tache: int) -> Optional[Tache]:
        """Obtenir une tâche par son ID"""
        lignes = self.db.executer_requete('''
            SELECT id, titre, description, id_projet, priorite, statut, assigne_a,
                   echeance, heures_estimees, cree_le, mis_a_jour_le
            FROM taches WHERE id=?
        ''', (id_tache,))
        
        if lignes:
            tache = Tache.depuis_ligne_db(dict(lignes[0]))
            # Charger les compétences requises
            competences = self.db.executer_requete('''
                SELECT competence FROM competences_taches WHERE tache_id=?
            ''', (id_tache,))
            tache.competences_requises = [comp[0] for comp in competences]
            return tache
        return None
    
    # Méthodes pour les membres d'équipe
    def charger_membres_equipe(self) -> List[MembreEquipe]:
        """Charger tous les membres d'équipe avec leurs compétences"""
        lignes = self.db.executer_requete('''
            SELECT id, nom, email, role, disponibilite, heures_max_par_semaine,
                   charge_travail_heures, cree_le, mis_a_jour_le
            FROM membres_equipe ORDER BY nom
        ''')
        
        membres = []
        for ligne in lignes:
            membre = MembreEquipe.depuis_ligne_db(dict(ligne))
            # Charger les compétences
            competences = self.db.executer_requete('''
                SELECT competence FROM competences_membres WHERE membre_id=?
            ''', (membre.id,))
            membre.competences = [comp[0] for comp in competences]
            membres.append(membre)
        
        return membres
    
    def ajouter_membre_equipe(self, membre: MembreEquipe):
        """Ajouter un nouveau membre d'équipe"""
        maintenant = self.db.maintenant()
        id_nouveau = self.db.executer_modification('''
            INSERT INTO membres_equipe (nom, email, role, disponibilite, heures_max_par_semaine,
                                       charge_travail_heures, cree_le, mis_a_jour_le)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (membre.nom, membre.email, membre.role, membre.disponibilite,
              membre.heures_max_par_semaine, membre.charge_travail_heures,
              maintenant, maintenant))
        
        membre.id = id_nouveau
        membre.cree_le = maintenant
        membre.mis_a_jour_le = maintenant
        
        # Ajouter les compétences
        if membre.competences:
            for competence in membre.competences:
                self.db.executer_modification('''
                    INSERT INTO competences_membres (membre_id, competence) VALUES (?, ?)
                ''', (id_nouveau, competence))
    
    def mettre_a_jour_membre_equipe(self, membre: MembreEquipe):
        """Mettre à jour un membre d'équipe existant"""
        maintenant = self.db.maintenant()
        self.db.executer_modification('''
            UPDATE membres_equipe 
            SET nom=?, email=?, role=?, disponibilite=?, heures_max_par_semaine=?,
                charge_travail_heures=?, mis_a_jour_le=?
            WHERE id=?
        ''', (membre.nom, membre.email, membre.role, membre.disponibilite,
              membre.heures_max_par_semaine, membre.charge_travail_heures,
              maintenant, membre.id))
        
        # Mettre à jour les compétences
        self.db.executer_modification('DELETE FROM competences_membres WHERE membre_id=?', (membre.id,))
        if membre.competences:
            for competence in membre.competences:
                self.db.executer_modification('''
                    INSERT INTO competences_membres (membre_id, competence) VALUES (?, ?)
                ''', (membre.id, competence))
        
        membre.mis_a_jour_le = maintenant
    
    def supprimer_membre_equipe(self, id_membre: int):
        """Supprimer un membre d'équipe"""
        self.db.executer_modification('DELETE FROM membres_equipe WHERE id=?', (id_membre,))
    
    def obtenir_membre_equipe(self, id_membre: int) -> Optional[MembreEquipe]:
        """Obtenir un membre d'équipe par son ID"""
        lignes = self.db.executer_requete('''
            SELECT id, nom, email, role, disponibilite, heures_max_par_semaine,
                   charge_travail_heures, cree_le, mis_a_jour_le
            FROM membres_equipe WHERE id=?
        ''', (id_membre,))
        
        if lignes:
            membre = MembreEquipe.depuis_ligne_db(dict(lignes[0]))
            # Charger les compétences
            competences = self.db.executer_requete('''
                SELECT competence FROM competences_membres WHERE membre_id=?
            ''', (id_membre,))
            membre.competences = [comp[0] for comp in competences]
            return membre
        return None
    
    # Méthodes utilitaires
    def obtenir_statistiques(self) -> dict:
        """Obtenir les statistiques générales"""
        projets = self.charger_projets()
        taches = self.charger_taches()
        membres = self.charger_membres_equipe()
        
        # Statistiques des projets
        projets_actifs = len([p for p in projets if p.statut == Projet.STATUT_ACTIF])
        projets_termines = len([p for p in projets if p.statut == Projet.STATUT_TERMINE])
        
        # Statistiques des tâches
        taches_a_faire = len([t for t in taches if t.statut == Tache.STATUT_A_FAIRE])
        taches_en_cours = len([t for t in taches if t.statut == Tache.STATUT_EN_COURS])
        taches_terminees = len([t for t in taches if t.statut == Tache.STATUT_TERMINE])
        
        # Tâches haute priorité
        taches_haute_priorite = len([t for t in taches if t.priorite == Tache.PRIORITE_HAUTE])
        
        # Membres disponibles
        membres_disponibles = len([m for m in membres if m.obtenir_score_disponibilite() > 0.5])
        
        return {
            'total_projets': len(projets),
            'projets_actifs': projets_actifs,
            'projets_termines': projets_termines,
            'total_taches': len(taches),
            'taches_a_faire': taches_a_faire,
            'taches_en_cours': taches_en_cours,
            'taches_terminees': taches_terminees,
            'taches_haute_priorite': taches_haute_priorite,
            'total_membres': len(membres),
            'membres_disponibles': membres_disponibles
        }
    
    # Méthodes de compatibilité (pour maintenir l'interface existante)
    def sauvegarder_projets(self, projets: List[Projet]):
        """Compatibilité - ne fait rien car SQLite sauvegarde automatiquement"""
        pass
    
    def sauvegarder_taches(self, taches: List[Tache]):
        """Compatibilité - ne fait rien car SQLite sauvegarde automatiquement"""
        pass
    
    def sauvegarder_membres_equipe(self, membres: List[MembreEquipe]):
        """Compatibilité - ne fait rien car SQLite sauvegarde automatiquement"""
        pass