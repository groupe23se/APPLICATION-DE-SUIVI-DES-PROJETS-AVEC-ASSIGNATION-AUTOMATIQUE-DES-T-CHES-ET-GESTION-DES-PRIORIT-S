"""
Fenêtre principale pour l'application de Suivi des Projets
"""

import tkinter as tk
from tkinter import ttk, messagebox
from gui.tableau_bord import TableauBord
from gui.fenetre_projet import FenetreProjet
from gui.fenetre_tache import FenetreTache
from gui.fenetre_equipe import FenetreEquipe
from modeles.gestionnaire_donnees import GestionnaireDonnees

class FenetrePrincipale:
    def __init__(self, racine):
        self.racine = racine
        self.gestionnaire_donnees = GestionnaireDonnees()
        
        self.configurer_fenetre()
        self.creer_menu()
        self.creer_cadre_principal()
        
        # Initialiser avec le tableau de bord
        self.afficher_tableau_bord()
    
    def configurer_fenetre(self):
        """Configurer les propriétés de la fenêtre principale"""
        self.racine.title("Suivi des Projets - Système de Gestion des Tâches")
        self.racine.geometry("1200x800")
        self.racine.minsize(800, 600)
        
        # Configurer le poids de la grille
        self.racine.grid_rowconfigure(0, weight=1)
        self.racine.grid_columnconfigure(0, weight=1)
    
    def creer_menu(self):
        """Créer la barre de menu"""
        barre_menu = tk.Menu(self.racine)
        self.racine.config(menu=barre_menu)
        
        # Menu Fichier
        menu_fichier = tk.Menu(barre_menu, tearoff=0)
        barre_menu.add_cascade(label="Fichier", menu=menu_fichier)
        menu_fichier.add_command(label="Tableau de bord", command=self.afficher_tableau_bord)
        menu_fichier.add_separator()
        menu_fichier.add_command(label="Quitter", command=self.racine.quit)
        
        # Menu Projets
        menu_projets = tk.Menu(barre_menu, tearoff=0)
        barre_menu.add_cascade(label="Projets", menu=menu_projets)
        menu_projets.add_command(label="Gérer les Projets", command=self.afficher_projets)
        menu_projets.add_command(label="Nouveau Projet", command=self.nouveau_projet)
        
        # Menu Tâches
        menu_taches = tk.Menu(barre_menu, tearoff=0)
        barre_menu.add_cascade(label="Tâches", menu=menu_taches)
        menu_taches.add_command(label="Gérer les Tâches", command=self.afficher_taches)
        menu_taches.add_command(label="Nouvelle Tâche", command=self.nouvelle_tache)
        
        # Menu Équipe
        menu_equipe = tk.Menu(barre_menu, tearoff=0)
        barre_menu.add_cascade(label="Équipe", menu=menu_equipe)
        menu_equipe.add_command(label="Gérer l'Équipe", command=self.afficher_equipe)
        menu_equipe.add_command(label="Ajouter un Membre", command=self.nouveau_membre_equipe)
        
        # Menu Aide
        menu_aide = tk.Menu(barre_menu, tearoff=0)
        barre_menu.add_cascade(label="Aide", menu=menu_aide)
        menu_aide.add_command(label="À propos", command=self.afficher_a_propos)
    
    def creer_cadre_principal(self):
        """Créer le cadre de contenu principal"""
        self.cadre_principal = ttk.Frame(self.racine)
        self.cadre_principal.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.cadre_principal.grid_rowconfigure(0, weight=1)
        self.cadre_principal.grid_columnconfigure(0, weight=1)
        
        # Référence de la vue actuelle
        self.vue_actuelle = None
    
    def vider_cadre_principal(self):
        """Vider le cadre principal"""
        for widget in self.cadre_principal.winfo_children():
            widget.destroy()
        self.vue_actuelle = None
    
    def afficher_tableau_bord(self):
        """Afficher la vue du tableau de bord"""
        self.vider_cadre_principal()
        self.vue_actuelle = TableauBord(self.cadre_principal, self.gestionnaire_donnees)
    
    def afficher_projets(self):
        """Afficher la vue de gestion des projets"""
        self.vider_cadre_principal()
        self.vue_actuelle = FenetreProjet(self.cadre_principal, self.gestionnaire_donnees)
    
    def afficher_taches(self):
        """Afficher la vue de gestion des tâches"""
        self.vider_cadre_principal()
        self.vue_actuelle = FenetreTache(self.cadre_principal, self.gestionnaire_donnees)
    
    def afficher_equipe(self):
        """Afficher la vue de gestion de l'équipe"""
        self.vider_cadre_principal()
        self.vue_actuelle = FenetreEquipe(self.cadre_principal, self.gestionnaire_donnees)
    
    def nouveau_projet(self):
        """Ouvrir la boîte de dialogue nouveau projet"""
        FenetreProjet.afficher_dialogue_projet(self.racine, self.gestionnaire_donnees)
        # Actualiser la vue actuelle si c'est le tableau de bord ou les projets
        if isinstance(self.vue_actuelle, (TableauBord, FenetreProjet)):
            self.vue_actuelle.actualiser()
    
    def nouvelle_tache(self):
        """Ouvrir la boîte de dialogue nouvelle tâche"""
        FenetreTache.afficher_dialogue_tache(self.racine, self.gestionnaire_donnees)
        # Actualiser la vue actuelle si c'est le tableau de bord ou les tâches
        if isinstance(self.vue_actuelle, (TableauBord, FenetreTache)):
            self.vue_actuelle.actualiser()
    
    def nouveau_membre_equipe(self):
        """Ouvrir la boîte de dialogue nouveau membre d'équipe"""
        FenetreEquipe.afficher_dialogue_membre_equipe(self.racine, self.gestionnaire_donnees)
        # Actualiser la vue actuelle si c'est le tableau de bord ou l'équipe
        if isinstance(self.vue_actuelle, (TableauBord, FenetreEquipe)):
            self.vue_actuelle.actualiser()
    
    def afficher_a_propos(self):
        """Afficher la boîte de dialogue à propos"""
        texte_a_propos = """Suivi des Projets v1.0

Une application complète de gestion de projets pour suivre les projets, tâches et membres d'équipe.

Fonctionnalités :
• Gestion des projets
• Suivi des tâches avec assignation automatique
• Gestion des membres d'équipe
• Gestion des priorités et statuts
• Tableau de bord avec statistiques
• Fonctionnalités de recherche et filtrage

Développé avec Python et Tkinter"""
        
        messagebox.showinfo("À propos du Suivi des Projets", texte_a_propos)