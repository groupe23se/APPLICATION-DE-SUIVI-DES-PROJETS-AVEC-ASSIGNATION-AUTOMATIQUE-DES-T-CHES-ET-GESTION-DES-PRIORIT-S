"""
Fenêtre de gestion des projets
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from modeles.gestionnaire_donnees import GestionnaireDonnees
from modeles.projet import Projet
from utilitaires.validateurs import Validateurs

class FenetreProjet:
    def __init__(self, parent, gestionnaire_donnees: GestionnaireDonnees):
        self.parent = parent
        self.gestionnaire_donnees = gestionnaire_donnees
        
        self.creer_widgets()
        self.actualiser()
    
    def creer_widgets(self):
        """Créer les widgets de gestion des projets"""
        # Conteneur principal
        self.cadre_principal = ttk.Frame(self.parent)
        self.cadre_principal.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.cadre_principal.grid_rowconfigure(2, weight=1)
        self.cadre_principal.grid_columnconfigure(0, weight=1)
        
        # Titre
        etiquette_titre = ttk.Label(self.cadre_principal, text="Gestion des Projets", 
                                   font=("Arial", 16, "bold"))
        etiquette_titre.grid(row=0, column=0, pady=(0, 20))
        
        # Barre d'outils
        cadre_barre_outils = ttk.Frame(self.cadre_principal)
        cadre_barre_outils.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Boutons
        ttk.Button(cadre_barre_outils, text="Nouveau Projet", 
                  command=self.nouveau_projet).pack(side="left", padx=(0, 10))
        ttk.Button(cadre_barre_outils, text="Modifier Projet", 
                  command=self.modifier_projet).pack(side="left", padx=(0, 10))
        ttk.Button(cadre_barre_outils, text="Supprimer Projet", 
                  command=self.supprimer_projet).pack(side="left", padx=(0, 10))
        ttk.Button(cadre_barre_outils, text="Voir Tâches", 
                  command=self.voir_taches).pack(side="left", padx=(0, 10))
        ttk.Button(cadre_barre_outils, text="Actualiser", 
                  command=self.actualiser).pack(side="right")
        
        # Cadre de recherche
        cadre_recherche = ttk.Frame(self.cadre_principal)
        cadre_recherche.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Label(cadre_recherche, text="Rechercher :").pack(side="left", padx=(0, 5))
        self.var_recherche = tk.StringVar()
        self.var_recherche.trace("w", self.filtrer_projets)
        entree_recherche = ttk.Entry(cadre_recherche, textvariable=self.var_recherche, width=30)
        entree_recherche.pack(side="left", padx=(0, 10))
        
        # Filtre de statut
        ttk.Label(cadre_recherche, text="Statut :").pack(side="left", padx=(10, 5))
        self.var_statut = tk.StringVar(value="Tous")
        combo_statut = ttk.Combobox(cadre_recherche, textvariable=self.var_statut, 
                                   values=["Tous", "Actif", "Terminé", "En Attente"],
                                   state="readonly", width=12)
        combo_statut.pack(side="left")
        combo_statut.bind("<<ComboboxSelected>>", lambda e: self.filtrer_projets())
        
        # Arbre des projets
        self.creer_arbre_projets()
    
    def creer_arbre_projets(self):
        """Créer l'arbre des projets"""
        cadre_arbre = ttk.Frame(self.cadre_principal)
        cadre_arbre.grid(row=3, column=0, sticky="nsew")
        cadre_arbre.grid_rowconfigure(0, weight=1)
        cadre_arbre.grid_columnconfigure(0, weight=1)
        
        # Colonnes
        colonnes = ("Nom", "Description", "Statut", "Tâches", "Créé", "Créé par")
        self.arbre_projets = ttk.Treeview(cadre_arbre, columns=colonnes, show="headings")
        
        # Configurer les colonnes
        self.arbre_projets.heading("Nom", text="Nom du Projet")
        self.arbre_projets.heading("Description", text="Description")
        self.arbre_projets.heading("Statut", text="Statut")
        self.arbre_projets.heading("Tâches", text="Tâches")
        self.arbre_projets.heading("Créé", text="Créé")
        self.arbre_projets.heading("Créé par", text="Créé par")
        
        self.arbre_projets.column("Nom", width=200)
        self.arbre_projets.column("Description", width=300)
        self.arbre_projets.column("Statut", width=100)
        self.arbre_projets.column("Tâches", width=80)
        self.arbre_projets.column("Créé", width=120)
        self.arbre_projets.column("Créé par", width=150)
        
        # Barres de défilement
        defilement_v = ttk.Scrollbar(cadre_arbre, orient="vertical", command=self.arbre_projets.yview)
        defilement_h = ttk.Scrollbar(cadre_arbre, orient="horizontal", command=self.arbre_projets.xview)
        self.arbre_projets.configure(yscrollcommand=defilement_v.set, xscrollcommand=defilement_h.set)
        
        # Disposition en grille
        self.arbre_projets.grid(row=0, column=0, sticky="nsew")
        defilement_v.grid(row=0, column=1, sticky="ns")
        defilement_h.grid(row=1, column=0, sticky="ew")
        
        # Liaison double-clic
        self.arbre_projets.bind("<Double-1>", lambda e: self.modifier_projet())
    
    def actualiser(self):
        """Actualiser l'affichage des projets"""
        self.projets = self.gestionnaire_donnees.charger_projets()
        self.toutes_taches = self.gestionnaire_donnees.charger_taches()
        self.filtrer_projets()
    
    def filtrer_projets(self, *args):
        """Filtrer les projets selon la recherche et le statut"""
        # Effacer les éléments existants
        for element in self.arbre_projets.get_children():
            self.arbre_projets.delete(element)
        
        texte_recherche = self.var_recherche.get().lower()
        filtre_statut = self.var_statut.get()
        
        for projet in self.projets:
            # Appliquer les filtres
            if texte_recherche and texte_recherche not in projet.nom.lower() and texte_recherche not in projet.description.lower():
                continue
            
            if filtre_statut != "Tous" and projet.statut != filtre_statut:
                continue
            
            # Compter les tâches pour ce projet
            taches_projet = len([t for t in self.toutes_taches if t.id_projet == projet.id])
            
            # Formater la date de création
            try:
                date_creation = projet.cree_le.split("T")[0]
            except:
                date_creation = projet.cree_le
            
            self.arbre_projets.insert("", "end", values=(
                projet.nom,
                projet.description[:50] + "..." if len(projet.description) > 50 else projet.description,
                projet.statut,
                str(taches_projet),
                date_creation,
                projet.cree_par
            ), tags=[projet.id])
    
    def obtenir_projet_selectionne(self):
        """Obtenir le projet actuellement sélectionné"""
        selection = self.arbre_projets.selection()
        if not selection:
            messagebox.showwarning("Aucune Sélection", "Veuillez sélectionner un projet.")
            return None
        
        # Obtenir l'ID du projet depuis les balises
        element = selection[0]
        balises = self.arbre_projets.item(element, "tags")
        if not balises:
            return None
        
        id_projet = balises[0]
        return self.gestionnaire_donnees.obtenir_projet(id_projet)
    
    def nouveau_projet(self):
        """Créer un nouveau projet"""
        self.afficher_dialogue_projet(self.cadre_principal, self.gestionnaire_donnees)
        self.actualiser()
    
    def modifier_projet(self):
        """Modifier le projet sélectionné"""
        projet = self.obtenir_projet_selectionne()
        if projet:
            self.afficher_dialogue_projet(self.cadre_principal, self.gestionnaire_donnees, projet)
            self.actualiser()
    
    def supprimer_projet(self):
        """Supprimer le projet sélectionné"""
        projet = self.obtenir_projet_selectionne()
        if not projet:
            return
        
        # Confirmer la suppression
        resultat = messagebox.askyesno(
            "Confirmer la Suppression",
            f"Êtes-vous sûr de vouloir supprimer le projet '{projet.nom}' ?\n\n"
            "Cela supprimera également toutes les tâches associées."
        )
        
        if resultat:
            try:
                self.gestionnaire_donnees.supprimer_projet(projet.id)
                messagebox.showinfo("Succès", "Projet supprimé avec succès.")
                self.actualiser()
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de la suppression du projet : {str(e)}")
    
    def voir_taches(self):
        """Voir les tâches du projet sélectionné"""
        projet = self.obtenir_projet_selectionne()
        if not projet:
            return
        
        # Importer ici pour éviter l'import circulaire
        from gui.fenetre_tache import FenetreTache
        
        # Créer une nouvelle fenêtre pour les tâches
        fenetre_taches = tk.Toplevel(self.cadre_principal)
        fenetre_taches.title(f"Tâches - {projet.nom}")
        fenetre_taches.geometry("1000x600")
        
        # Créer la vue des tâches avec filtre de projet
        vue_taches = FenetreTache(fenetre_taches, self.gestionnaire_donnees, filtre_projet=projet.id)
    
    @staticmethod
    def afficher_dialogue_projet(parent, gestionnaire_donnees: GestionnaireDonnees, projet: Projet = None):
        """Afficher la boîte de dialogue de création/modification de projet"""
        dialogue = tk.Toplevel(parent)
        dialogue.title("Modifier le Projet" if projet else "Nouveau Projet")
        dialogue.geometry("500x400")
        dialogue.resizable(False, False)
        dialogue.transient(parent)
        dialogue.grab_set()
        
        # Centrer la boîte de dialogue
        dialogue.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Variables
        var_nom = tk.StringVar(value=projet.nom if projet else "")
        var_description = tk.StringVar(value=projet.description if projet else "")
        var_statut = tk.StringVar(value=projet.statut if projet else "Actif")
        var_cree_par = tk.StringVar(value=projet.cree_par if projet else "")
        
        # Créer le formulaire
        cadre_principal = ttk.Frame(dialogue, padding=20)
        cadre_principal.pack(fill="both", expand=True)
        
        # Nom du projet
        ttk.Label(cadre_principal, text="Nom du Projet :*").grid(row=0, column=0, sticky="w", pady=(0, 5))
        entree_nom = ttk.Entry(cadre_principal, textvariable=var_nom, width=50)
        entree_nom.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        entree_nom.focus()
        
        # Description
        ttk.Label(cadre_principal, text="Description :").grid(row=2, column=0, sticky="w", pady=(0, 5))
        texte_desc = tk.Text(cadre_principal, width=50, height=8)
        texte_desc.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        texte_desc.insert("1.0", var_description.get())
        
        # Statut
        ttk.Label(cadre_principal, text="Statut :").grid(row=4, column=0, sticky="w", pady=(0, 5))
        combo_statut = ttk.Combobox(cadre_principal, textvariable=var_statut, 
                                   values=["Actif", "Terminé", "En Attente"],
                                   state="readonly", width=20)
        combo_statut.grid(row=5, column=0, sticky="w", pady=(0, 15))
        
        # Créé par
        ttk.Label(cadre_principal, text="Créé par :").grid(row=6, column=0, sticky="w", pady=(0, 5))
        entree_cree_par = ttk.Entry(cadre_principal, textvariable=var_cree_par, width=30)
        entree_cree_par.grid(row=7, column=0, sticky="w", pady=(0, 20))
        
        # Boutons
        cadre_boutons = ttk.Frame(cadre_principal)
        cadre_boutons.grid(row=8, column=0, columnspan=2, sticky="ew")
        
        def sauvegarder_projet():
            # Valider l'entrée
            nom = var_nom.get().strip()
            if not nom:
                messagebox.showerror("Erreur de Validation", "Le nom du projet est requis.")
                return
            
            if not Validateurs.valider_longueur_texte(nom, longueur_max=100):
                messagebox.showerror("Erreur de Validation", "Le nom du projet doit faire 100 caractères ou moins.")
                return
            
            description = texte_desc.get("1.0", "end-1c").strip()
            if not Validateurs.valider_longueur_texte(description, longueur_max=1000):
                messagebox.showerror("Erreur de Validation", "La description doit faire 1000 caractères ou moins.")
                return
            
            try:
                if projet:
                    # Mettre à jour le projet existant
                    projet.nom = nom
                    projet.description = description
                    projet.statut = var_statut.get()
                    projet.cree_par = var_cree_par.get().strip()
                    gestionnaire_donnees.mettre_a_jour_projet(projet)
                    messagebox.showinfo("Succès", "Projet mis à jour avec succès.")
                else:
                    # Créer un nouveau projet
                    nouveau_projet = Projet(
                        nom=nom,
                        description=description,
                        cree_par=var_cree_par.get().strip()
                    )
                    nouveau_projet.statut = var_statut.get()
                    gestionnaire_donnees.ajouter_projet(nouveau_projet)
                    messagebox.showinfo("Succès", "Projet créé avec succès.")
                
                dialogue.destroy()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de la sauvegarde du projet : {str(e)}")
        
        def annuler():
            dialogue.destroy()
        
        ttk.Button(cadre_boutons, text="Sauvegarder", command=sauvegarder_projet).pack(side="right", padx=(10, 0))
        ttk.Button(cadre_boutons, text="Annuler", command=annuler).pack(side="right")
        
        # Configurer les poids de la grille
        cadre_principal.grid_columnconfigure(0, weight=1)
        dialogue.grid_columnconfigure(0, weight=1)
        
        # Lier la touche Entrée à sauvegarder
        dialogue.bind("<Return>", lambda e: sauvegarder_projet())
        dialogue.bind("<Escape>", lambda e: annuler())
