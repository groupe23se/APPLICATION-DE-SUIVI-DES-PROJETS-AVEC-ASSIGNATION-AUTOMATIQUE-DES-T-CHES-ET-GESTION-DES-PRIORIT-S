"""
Moteur d'assignation automatique des tâches
"""

from typing import List, Optional
from modeles.gestionnaire_donnees import GestionnaireDonnees
from modeles.tache import Tache
from modeles.membre_equipe import MembreEquipe

class MoteurAssignation:
    def __init__(self, gestionnaire_donnees: GestionnaireDonnees):
        self.gestionnaire_donnees = gestionnaire_donnees
    
    def trouver_meilleur_assignataire(self, tache: Tache) -> Optional[MembreEquipe]:
        """
        Trouver le meilleur membre d'équipe pour assigner une tâche basé sur :
        - Correspondance des compétences requises
        - Charge de travail actuelle/disponibilité
        - Priorité de la tâche
        """
        membres_equipe = self.gestionnaire_donnees.charger_membres_equipe()
        
        if not membres_equipe:
            return None
        
        # Filtrer les membres qui ont les compétences requises
        membres_eligibles = []
        for membre in membres_equipe:
            if membre.a_competences_requises(tache.competences_requises):
                membres_eligibles.append(membre)
        
        # Si personne n'a les compétences requises, considérer tous les membres
        if not membres_eligibles:
            membres_eligibles = membres_equipe
        
        # Calculer les scores d'assignation pour chaque membre éligible
        membres_scores = []
        for membre in membres_eligibles:
            score = self._calculer_score_assignation(membre, tache)
            if score > 0:  # Considérer seulement les membres avec des scores positifs
                membres_scores.append((membre, score))
        
        if not membres_scores:
            return None
        
        # Trier par score (le plus élevé en premier) et retourner la meilleure correspondance
        membres_scores.sort(key=lambda x: x[1], reverse=True)
        return membres_scores[0][0]
    
    def _calculer_score_assignation(self, membre: MembreEquipe, tache: Tache) -> float:
        """
        Calculer le score d'assignation pour un membre d'équipe et une tâche.
        Un score plus élevé signifie une meilleure correspondance.
        """
        score = 0.0
        
        # Score de disponibilité de base (0.0 à 1.0)
        score_disponibilite = membre.obtenir_score_disponibilite()
        score += score_disponibilite * 40  # Poids : 40%
        
        # Score de correspondance des compétences
        score_competences = self._calculer_score_competences(membre, tache)
        score += score_competences * 35  # Poids : 35%
        
        # Bonus de priorité (les tâches de haute priorité obtiennent la préférence pour les membres disponibles)
        bonus_priorite = self._calculer_bonus_priorite(tache, score_disponibilite)
        score += bonus_priorite * 15  # Poids : 15%
        
        # Score d'équilibre de charge de travail (préférer les membres avec une charge plus légère)
        score_charge_travail = self._calculer_score_charge_travail(membre)
        score += score_charge_travail * 10  # Poids : 10%
        
        return score
    
    def _calculer_score_competences(self, membre: MembreEquipe, tache: Tache) -> float:
        """Calculer à quel point les compétences du membre correspondent aux exigences de la tâche"""
        if not tache.competences_requises:
            return 0.5  # Score neutre si aucune compétence spécifique requise
        
        if not membre.competences:
            return 0.0  # Aucune compétence signifie aucune correspondance
        
        # Calculer le pourcentage de compétences requises que le membre possède
        competences_correspondantes = 0
        for competence in tache.competences_requises:
            if competence.lower() in [c.lower() for c in membre.competences]:
                competences_correspondantes += 1
        
        ratio_correspondance_competences = competences_correspondantes / len(tache.competences_requises)
        
        # Bonus pour avoir des compétences supplémentaires pertinentes
        bonus_competences_supplementaires = min(len(membre.competences) / 10.0, 0.2)
        
        return min(ratio_correspondance_competences + bonus_competences_supplementaires, 1.0)
    
    def _calculer_bonus_priorite(self, tache: Tache, score_disponibilite: float) -> float:
        """Calculer le bonus de priorité basé sur la priorité de la tâche et la disponibilité du membre"""
        poids_priorites = {
            Tache.PRIORITE_HAUTE: 1.0,
            Tache.PRIORITE_MOYENNE: 0.6,
            Tache.PRIORITE_BASSE: 0.3
        }
        
        poids_priorite = poids_priorites.get(tache.priorite, 0.6)
        
        # Les tâches de haute priorité obtiennent un plus gros bonus pour les membres très disponibles
        return poids_priorite * score_disponibilite
    
    def _calculer_score_charge_travail(self, membre: MembreEquipe) -> float:
        """Calculer le score d'équilibre de charge de travail (préférer les membres moins chargés)"""
        if membre.heures_max_par_semaine == 0:
            return 0.0
        
        utilisation = membre.charge_travail_heures / membre.heures_max_par_semaine
        
        # Le score diminue quand l'utilisation augmente
        # Score parfait (1.0) pour 0% d'utilisation, score 0 pour 100%+ d'utilisation
        return max(0.0, 1.0 - utilisation)
    
    def auto_assigner_toutes_taches_non_assignees(self) -> dict:
        """
        Assigner automatiquement toutes les tâches non assignées.
        Retourne un dictionnaire avec les résultats d'assignation.
        """
        taches = self.gestionnaire_donnees.charger_taches()
        taches_non_assignees = [t for t in taches if not t.assigne_a and t.statut == Tache.STATUT_A_FAIRE]
        
        resultats = {
            'assignees': [],
            'non_assignees': [],
            'total_traitees': len(taches_non_assignees)
        }
        
        # Trier les tâches par priorité (haute priorité en premier)
        taches_non_assignees.sort(key=lambda t: t.obtenir_poids_priorite(), reverse=True)
        
        for tache in taches_non_assignees:
            meilleur_membre = self.trouver_meilleur_assignataire(tache)
            
            if meilleur_membre:
                # Assigner la tâche
                tache.assigner_a(meilleur_membre.id)
                meilleur_membre.assigner_tache(tache.id, tache.heures_estimees)
                
                # Sauvegarder les changements
                self.gestionnaire_donnees.mettre_a_jour_tache(tache)
                self.gestionnaire_donnees.mettre_a_jour_membre_equipe(meilleur_membre)
                
                resultats['assignees'].append({
                    'tache': tache,
                    'assignataire': meilleur_membre
                })
            else:
                resultats['non_assignees'].append(tache)
        
        return resultats
    
    def suggerer_reassignations(self) -> List[dict]:
        """
        Suggérer des réassignations de tâches pour un meilleur équilibre de charge de travail.
        Retourne une liste de suggestions de réassignation.
        """
        taches = self.gestionnaire_donnees.charger_taches()
        membres_equipe = self.gestionnaire_donnees.charger_membres_equipe()
        
        suggestions = []
        
        # Trouver les membres surchargés
        membres_surcharges = [m for m in membres_equipe if m.obtenir_score_disponibilite() < 0.2]
        
        for membre in membres_surcharges:
            taches_membre = [t for t in taches if t.assigne_a == membre.id and t.statut != Tache.STATUT_TERMINE]
            
            # Trier par priorité (essayer de réassigner les tâches de priorité plus basse en premier)
            taches_membre.sort(key=lambda t: t.obtenir_poids_priorite())
            
            for tache in taches_membre[:3]:  # Considérer jusqu'à 3 tâches pour réassignation
                meilleur_assignataire = self.trouver_meilleur_assignataire(tache)
                
                if meilleur_assignataire and meilleur_assignataire.id != membre.id:
                    score_actuel = self._calculer_score_assignation(membre, tache)
                    nouveau_score = self._calculer_score_assignation(meilleur_assignataire, tache)
                    
                    if nouveau_score > score_actuel * 1.2:  # Seuil d'amélioration de 20% 
                        suggestions.append({
                            'tache': tache,
                            'assignataire_actuel': membre,
                            'assignataire_suggere': meilleur_assignataire,
                            'score_amelioration': nouveau_score - score_actuel
                        })
        
        # Trier par score d'amélioration
        suggestions.sort(key=lambda s: s['score_amelioration'], reverse=True)
        
        return suggestions[:10]  # Retourner les 10 meilleures suggestions
