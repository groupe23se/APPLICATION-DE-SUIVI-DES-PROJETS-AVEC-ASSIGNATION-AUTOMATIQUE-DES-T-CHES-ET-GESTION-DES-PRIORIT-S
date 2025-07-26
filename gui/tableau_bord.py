"""
Vue du tableau de bord montrant l'aperçu du projet et les statistiques
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, date
from modeles.gestionnaire_donnees import GestionnaireDonnees
from modeles.tache import Tache
from modeles.projet import Projet

class TableauBord:
    def __init__(self, parent, gestionnaire_donnees: GestionnaireDonnees):
        self.parent = parent
        self.gestionnaire_donnees = gestionnaire_donnees
        
        self.creer_widgets()
        self.actualiser()
    
    def creer_widgets(self):
        """Créer les widgets du tableau de bord"""
        # Conteneur principal
        self.cadre_principal = ttk.Frame(self.parent)
        self.cadre_principal.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.cadre_principal.grid_rowconfigure(1, weight=1)
        self.cadre_principal.grid_columnconfigure(0, weight=1)
        
        # Titre
        etiquette_titre = ttk.Label(self.cadre_principal, text="Tableau de Bord des Projets", 
                                   font=("Arial", 16, "bold"))
        etiquette_titre.grid(row=0, column=0, pady=(0, 20))
        
        # Cadre des statistiques
        cadre_stats = ttk.LabelFrame(self.cadre_principal, text="Statistiques Générales", padding=10)
        cadre_stats.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        cadre_stats.grid_columnconfigure(0, weight=1)
        cadre_stats.grid_columnconfigure(1, weight=1)
        cadre_stats.grid_columnconfigure(2, weight=1)
        cadre_stats.grid_columnconfigure(3, weight=1)
        
        # Étiquettes de statistiques
        self.etiquettes_stats = {}
        elements_stats = [
            ("Total Projets", "total_projets"),
            ("Projets Actifs", "projets_actifs"),
            ("Total Tâches", "total_taches"),
            ("Tâches Terminées", "taches_terminees"),
            ("Tâches Haute Priorité", "taches_haute_priorite"),
            ("Tâches en Retard", "taches_retard"),
            ("Membres d'Équipe", "membres_equipe"),
            ("Membres Disponibles", "membres_disponibles")
        ]
        
        ligne = 0
        colonne = 0
        for texte_etiquette, cle in elements_stats:
            cadre = ttk.Frame(cadre_stats)
            cadre.grid(row=ligne, column=colonne, padx=10, pady=5, sticky="ew")
            
            ttk.Label(cadre, text=texte_etiquette + " :", font=("Arial", 10, "bold")).pack()
            self.etiquettes_stats[cle] = ttk.Label(cadre, text="0", font=("Arial", 12))
            self.etiquettes_stats[cle].pack()
            
            colonne += 1
            if colonne > 3:
                colonne = 0
                ligne += 1
        
        # Cahier d'onglets de contenu
        self.cahier_onglets = ttk.Notebook(self.cadre_principal)
        self.cahier_onglets.grid(row=2, column=0, sticky="nsew")
        self.cadre_principal.grid_rowconfigure(2, weight=1)
        
        # Onglet tâches récentes
        self.creer_onglet_taches_recentes()
        
        # Onglet tâches prioritaires
        self.creer_onglet_taches_prioritaires()
        
        # Onglet aperçu projets
        self.creer_onglet_apercu_projets()
    
    def creer_onglet_taches_recentes(self):
        """Créer l'onglet des tâches récentes"""
        cadre_onglet = ttk.Frame(self.cahier_onglets)
        self.cahier_onglets.add(cadre_onglet, text="Tâches Récentes")
        
        # Créer l'arbre pour les tâches récentes
        colonnes = ("Titre", "Projet", "Priorité", "Statut", "Assigné à", "Échéance")
        self.arbre_taches_recentes = ttk.Treeview(cadre_onglet, columns=colonnes, show="headings", height=10)
        
        # Configurer les colonnes
        for col in colonnes:
            self.arbre_taches_recentes.heading(col, text=col)
            self.arbre_taches_recentes.column(col, width=120)
        
        # Barres de défilement
        defilement_v = ttk.Scrollbar(cadre_onglet, orient="vertical", command=self.arbre_taches_recentes.yview)
        defilement_h = ttk.Scrollbar(cadre_onglet, orient="horizontal", command=self.arbre_taches_recentes.xview)
        self.arbre_taches_recentes.configure(yscrollcommand=defilement_v.set, xscrollcommand=defilement_h.set)
        
        # Disposition en grille
        self.arbre_taches_recentes.grid(row=0, column=0, sticky="nsew")
        defilement_v.grid(row=0, column=1, sticky="ns")
        defilement_h.grid(row=1, column=0, sticky="ew")
        
        cadre_onglet.grid_rowconfigure(0, weight=1)
        cadre_onglet.grid_columnconfigure(0, weight=1)
    
    def creer_onglet_taches_prioritaires(self):
        """Créer l'onglet des tâches haute priorité"""
        cadre_onglet = ttk.Frame(self.cahier_onglets)
        self.cahier_onglets.add(cadre_onglet, text="Tâches Haute Priorité")
        
        # Créer l'arbre pour les tâches prioritaires
        colonnes = ("Titre", "Projet", "Statut", "Assigné à", "Échéance")
        self.arbre_taches_prioritaires = ttk.Treeview(cadre_onglet, columns=colonnes, show="headings", height=10)
        
        # Configurer les colonnes
        for col in colonnes:
            self.arbre_taches_prioritaires.heading(col, text=col)
            self.arbre_taches_prioritaires.column(col, width=140)
        
        # Barres de défilement
        defilement_v = ttk.Scrollbar(cadre_onglet, orient="vertical", command=self.arbre_taches_prioritaires.yview)
        defilement_h = ttk.Scrollbar(cadre_onglet, orient="horizontal", command=self.arbre_taches_prioritaires.xview)
        self.arbre_taches_prioritaires.configure(yscrollcommand=defilement_v.set, xscrollcommand=defilement_h.set)
        
        # Disposition en grille
        self.arbre_taches_prioritaires.grid(row=0, column=0, sticky="nsew")
        defilement_v.grid(row=0, column=1, sticky="ns")
        defilement_h.grid(row=1, column=0, sticky="ew")
        
        cadre_onglet.grid_rowconfigure(0, weight=1)
        cadre_onglet.grid_columnconfigure(0, weight=1)
    
    def creer_onglet_apercu_projets(self):
        """Créer l'onglet aperçu des projets"""
        cadre_onglet = ttk.Frame(self.cahier_onglets)
        self.cahier_onglets.add(cadre_onglet, text="Aperçu des Projets")
        
        # Créer l'arbre pour les projets
        colonnes = ("Nom", "Statut", "Tâches", "Terminées", "Progrès")
        self.arbre_projets = ttk.Treeview(cadre_onglet, columns=colonnes, show="headings", height=10)
        
        # Configurer les colonnes
        for col in colonnes:
            self.arbre_projets.heading(col, text=col)
            self.arbre_projets.column(col, width=140)
        
        # Barres de défilement
        defilement_v = ttk.Scrollbar(cadre_onglet, orient="vertical", command=self.arbre_projets.yview)
        defilement_h = ttk.Scrollbar(cadre_onglet, orient="horizontal", command=self.arbre_projets.xview)
        self.arbre_projets.configure(yscrollcommand=defilement_v.set, xscrollcommand=defilement_h.set)
        
        # Disposition en grille
        self.arbre_projets.grid(row=0, column=0, sticky="nsew")
        defilement_v.grid(row=0, column=1, sticky="ns")
        defilement_h.grid(row=1, column=0, sticky="ew")
        
        cadre_onglet.grid_rowconfigure(0, weight=1)
        cadre_onglet.grid_columnconfigure(0, weight=1)
    
    def actualiser(self):
        """Actualiser les données du tableau de bord"""
        self.mettre_a_jour_statistiques()
        self.mettre_a_jour_taches_recentes()
        self.mettre_a_jour_taches_prioritaires()
        self.mettre_a_jour_apercu_projets()
    
    def mettre_a_jour_statistiques(self):
        """Mettre à jour l'affichage des statistiques"""
        projets = self.gestionnaire_donnees.charger_projets()
        taches = self.gestionnaire_donnees.charger_taches()
        membres_equipe = self.gestionnaire_donnees.charger_membres_equipe()
        
        # Calculer les statistiques
        total_projets = len(projets)
        projets_actifs = len([p for p in projets if p.statut == "Actif"])
        total_taches = len(taches)
        taches_terminees = len([t for t in taches if t.statut == Tache.STATUT_TERMINE])
        taches_haute_priorite = len([t for t in taches if t.priorite == Tache.PRIORITE_HAUTE])
        
        # Calculer les tâches en retard
        aujourd_hui = date.today()
        taches_retard = 0
        for tache in taches:
            if tache.echeance and tache.statut != Tache.STATUT_TERMINE:
                try:
                    date_echeance = datetime.strptime(tache.echeance, "%Y-%m-%d").date()
                    if date_echeance < aujourd_hui:
                        taches_retard += 1
                except ValueError:
                    pass
        
        total_membres = len(membres_equipe)
        membres_disponibles = len([m for m in membres_equipe if m.obtenir_score_disponibilite() > 0.5])
        
        # Mettre à jour les étiquettes
        self.etiquettes_stats["total_projets"].config(text=str(total_projets))
        self.etiquettes_stats["projets_actifs"].config(text=str(projets_actifs))
        self.etiquettes_stats["total_taches"].config(text=str(total_taches))
        self.etiquettes_stats["taches_terminees"].config(text=str(taches_terminees))
        self.etiquettes_stats["taches_haute_priorite"].config(text=str(taches_haute_priorite))
        self.etiquettes_stats["taches_retard"].config(text=str(taches_retard))
        self.etiquettes_stats["membres_equipe"].config(text=str(total_membres))
        self.etiquettes_stats["membres_disponibles"].config(text=str(membres_disponibles))
    
    def mettre_a_jour_taches_recentes(self):
        """Mettre à jour l'affichage des tâches récentes"""
        # Effacer les éléments existants
        for element in self.arbre_taches_recentes.get_children():
            self.arbre_taches_recentes.delete(element)
        
        taches = self.gestionnaire_donnees.charger_taches()
        projets = {p.id: p for p in self.gestionnaire_donnees.charger_projets()}
        membres_equipe = {m.id: m for m in self.gestionnaire_donnees.charger_membres_equipe()}
        
        # Trier les tâches par date de création (plus récentes en premier)
        taches.sort(key=lambda t: t.cree_le, reverse=True)
        
        # Afficher les 20 dernières tâches
        for tache in taches[:20]:
            nom_projet = projets.get(tache.id_projet, type('obj', (object,), {'nom': 'Aucun Projet'})).nom if tache.id_projet else "Aucun Projet"
            nom_assigne = membres_equipe.get(tache.assigne_a, type('obj', (object,), {'nom': 'Non assigné'})).nom if tache.assigne_a else "Non assigné"
            
            # Codage couleur par priorité
            balises = []
            if tache.priorite == Tache.PRIORITE_HAUTE:
                balises = ["haute_priorite"]
            elif tache.priorite == Tache.PRIORITE_MOYENNE:
                balises = ["priorite_moyenne"]
            else:
                balises = ["basse_priorite"]
            
            self.arbre_taches_recentes.insert("", "end", values=(
                tache.titre,
                nom_projet,
                tache.priorite,
                tache.statut,
                nom_assigne,
                tache.echeance or "Pas d'échéance"
            ), tags=balises)
        
        # Configurer les balises pour les couleurs
        self.arbre_taches_recentes.tag_configure("haute_priorite", background="#ffebee")
        self.arbre_taches_recentes.tag_configure("priorite_moyenne", background="#fff3e0")
        self.arbre_taches_recentes.tag_configure("basse_priorite", background="#e8f5e8")
    
    def mettre_a_jour_taches_prioritaires(self):
        """Mettre à jour l'affichage des tâches haute priorité"""
        # Effacer les éléments existants
        for element in self.arbre_taches_prioritaires.get_children():
            self.arbre_taches_prioritaires.delete(element)
        
        taches = self.gestionnaire_donnees.charger_taches()
        projets = {p.id: p for p in self.gestionnaire_donnees.charger_projets()}
        membres_equipe = {m.id: m for m in self.gestionnaire_donnees.charger_membres_equipe()}
        
        # Filtrer les tâches haute priorité
        taches_haute_priorite = [t for t in taches if t.priorite == Tache.PRIORITE_HAUTE]
        taches_haute_priorite.sort(key=lambda t: t.echeance or "9999-12-31")
        
        for tache in taches_haute_priorite:
            nom_projet = projets.get(tache.id_projet, type('obj', (object,), {'nom': 'Aucun Projet'})).nom if tache.id_projet else "Aucun Projet"
            nom_assigne = membres_equipe.get(tache.assigne_a, type('obj', (object,), {'nom': 'Non assigné'})).nom if tache.assigne_a else "Non assigné"
            
            # Vérifier si en retard
            balises = []
            if tache.echeance and tache.statut != Tache.STATUT_TERMINE:
                try:
                    date_echeance = datetime.strptime(tache.echeance, "%Y-%m-%d").date()
                    if date_echeance < date.today():
                        balises = ["en_retard"]
                except ValueError:
                    pass
            
            self.arbre_taches_prioritaires.insert("", "end", values=(
                tache.titre,
                nom_projet,
                tache.statut,
                nom_assigne,
                tache.echeance or "Pas d'échéance"
            ), tags=balises)
        
        # Configurer la balise en retard
        self.arbre_taches_prioritaires.tag_configure("en_retard", background="#ffcdd2")
    
    def mettre_a_jour_apercu_projets(self):
        """Mettre à jour l'affichage de l'aperçu des projets"""
        # Effacer les éléments existants
        for element in self.arbre_projets.get_children():
            self.arbre_projets.delete(element)
        
        projets = self.gestionnaire_donnees.charger_projets()
        toutes_taches = self.gestionnaire_donnees.charger_taches()
        
        for projet in projets:
            taches_projet = [t for t in toutes_taches if t.id_projet == projet.id]
            total_taches = len(taches_projet)
            taches_terminees = len([t for t in taches_projet if t.statut == Tache.STATUT_TERMINE])
            
            progres = 0
            if total_taches > 0:
                progres = int((taches_terminees / total_taches) * 100)
            
            self.arbre_projets.insert("", "end", values=(
                projet.nom,
                projet.statut,
                str(total_taches),
                str(taches_terminees),
                f"{progres}%"
            ))
