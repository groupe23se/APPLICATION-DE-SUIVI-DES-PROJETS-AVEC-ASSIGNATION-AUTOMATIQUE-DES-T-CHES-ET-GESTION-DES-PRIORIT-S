"""
Fenêtre de gestion des membres d'équipe
"""

import tkinter as tk
from tkinter import ttk, messagebox
from modeles.gestionnaire_donnees import GestionnaireDonnees
from modeles.membre_equipe import MembreEquipe
from utilitaires.validateurs import Validateurs

class FenetreEquipe:
    def __init__(self, parent, gestionnaire_donnees: GestionnaireDonnees):
        self.parent = parent
        self.gestionnaire_donnees = gestionnaire_donnees
        
        self.creer_widgets()
        self.actualiser()
    
    def creer_widgets(self):
        """Créer les widgets de gestion de l'équipe"""
        # Conteneur principal
        self.cadre_principal = ttk.Frame(self.parent)
        self.cadre_principal.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.cadre_principal.grid_rowconfigure(2, weight=1)
        self.cadre_principal.grid_columnconfigure(0, weight=1)
        
        # Titre
        etiquette_titre = ttk.Label(self.cadre_principal, text="Gestion de l'Équipe", 
                                   font=("Arial", 16, "bold"))
        etiquette_titre.grid(row=0, column=0, pady=(0, 20))
        
        # Barre d'outils
        cadre_barre_outils = ttk.Frame(self.cadre_principal)
        cadre_barre_outils.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Boutons
        ttk.Button(cadre_barre_outils, text="Ajouter Membre", 
                  command=self.nouveau_membre).pack(side="left", padx=(0, 10))
        ttk.Button(cadre_barre_outils, text="Modifier Membre", 
                  command=self.modifier_membre).pack(side="left", padx=(0, 10))
        ttk.Button(cadre_barre_outils, text="Supprimer Membre", 
                  command=self.supprimer_membre).pack(side="left", padx=(0, 10))
        ttk.Button(cadre_barre_outils, text="Voir Tâches", 
                  command=self.voir_taches_membre).pack(side="left", padx=(0, 10))
        ttk.Button(cadre_barre_outils, text="Actualiser", 
                  command=self.actualiser).pack(side="right")
        
        # Cadre de recherche
        cadre_recherche = ttk.Frame(self.cadre_principal)
        cadre_recherche.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Label(cadre_recherche, text="Rechercher :").pack(side="left", padx=(0, 5))
        self.var_recherche = tk.StringVar()
        self.var_recherche.trace("w", self.filtrer_membres)
        entree_recherche = ttk.Entry(cadre_recherche, textvariable=self.var_recherche, width=30)
        entree_recherche.pack(side="left", padx=(0, 10))
        
        # Arbre des membres d'équipe
        self.creer_arbre_membres()
    
    def creer_arbre_membres(self):
        """Créer l'arbre des membres d'équipe"""
        cadre_arbre = ttk.Frame(self.cadre_principal)
        cadre_arbre.grid(row=3, column=0, sticky="nsew")
        cadre_arbre.grid_rowconfigure(0, weight=1)
        cadre_arbre.grid_columnconfigure(0, weight=1)
        
        # Colonnes
        colonnes = ("Nom", "Email", "Rôle", "Compétences", "Disponibilité", "Tâches Actuelles", "Charge de Travail")
        self.arbre_membres = ttk.Treeview(cadre_arbre, columns=colonnes, show="headings")
        
        # Configurer les colonnes
        self.arbre_membres.heading("Nom", text="Nom")
        self.arbre_membres.heading("Email", text="Email")
        self.arbre_membres.heading("Rôle", text="Rôle")
        self.arbre_membres.heading("Compétences", text="Compétences")
        self.arbre_membres.heading("Disponibilité", text="Disponibilité %")
        self.arbre_membres.heading("Tâches Actuelles", text="Tâches Actuelles")
        self.arbre_membres.heading("Charge de Travail", text="Charge de Travail (h)")
        
        self.arbre_membres.column("Nom", width=150)
        self.arbre_membres.column("Email", width=200)
        self.arbre_membres.column("Rôle", width=120)
        self.arbre_membres.column("Compétences", width=200)
        self.arbre_membres.column("Disponibilité", width=100)
        self.arbre_membres.column("Tâches Actuelles", width=100)
        self.arbre_membres.column("Charge de Travail", width=100)
        
        # Barres de défilement
        defilement_v = ttk.Scrollbar(cadre_arbre, orient="vertical", command=self.arbre_membres.yview)
        defilement_h = ttk.Scrollbar(cadre_arbre, orient="horizontal", command=self.arbre_membres.xview)
        self.arbre_membres.configure(yscrollcommand=defilement_v.set, xscrollcommand=defilement_h.set)
        
        # Disposition en grille
        self.arbre_membres.grid(row=0, column=0, sticky="nsew")
        defilement_v.grid(row=0, column=1, sticky="ns")
        defilement_h.grid(row=1, column=0, sticky="ew")
        
        # Liaison double-clic
        self.arbre_membres.bind("<Double-1>", lambda e: self.modifier_membre())
    
    def actualiser(self):
        """Actualiser l'affichage des membres d'équipe"""
        self.membres = self.gestionnaire_donnees.charger_membres_equipe()
        self.toutes_taches = self.gestionnaire_donnees.charger_taches()
        self.filtrer_membres()
    
    def filtrer_membres(self, *args):
        """Filtrer les membres selon la recherche"""
        # Effacer les éléments existants
        for element in self.arbre_membres.get_children():
            self.arbre_membres.delete(element)
        
        texte_recherche = self.var_recherche.get().lower()
        
        for membre in self.membres:
            # Appliquer le filtre de recherche
            if texte_recherche and (texte_recherche not in membre.nom.lower() and 
                                   texte_recherche not in membre.email.lower() and
                                   texte_recherche not in membre.role.lower()):
                continue
            
            # Obtenir les tâches actuelles du membre
            taches_membre = [t for t in self.toutes_taches if t.assigne_a == membre.id and t.statut != "Terminé"]
            
            # Formater les compétences
            texte_competences = ", ".join(membre.competences[:3])  # Afficher les 3 premières compétences
            if len(membre.competences) > 3:
                texte_competences += f" (+{len(membre.competences) - 3} autres)"
            
            # Déterminer la couleur de ligne selon la disponibilité
            balises = []
            if membre.obtenir_score_disponibilite() < 0.3:
                balises = ["faible_disponibilite"]
            elif membre.obtenir_score_disponibilite() > 0.7:
                balises = ["haute_disponibilite"]
            
            self.arbre_membres.insert("", "end", values=(
                membre.nom,
                membre.email,
                membre.role,
                texte_competences,
                f"{membre.disponibilite}%",
                str(len(taches_membre)),
                f"{membre.charge_travail_heures}/{membre.heures_max_par_semaine}"
            ), tags=[membre.id] + balises)
        
        # Configurer les balises pour les couleurs
        self.arbre_membres.tag_configure("faible_disponibilite", background="#ffcdd2")
        self.arbre_membres.tag_configure("haute_disponibilite", background="#c8e6c9")
    
    def obtenir_membre_selectionne(self):
        """Obtenir le membre d'équipe actuellement sélectionné"""
        selection = self.arbre_membres.selection()
        if not selection:
            messagebox.showwarning("Aucune Sélection", "Veuillez sélectionner un membre d'équipe.")
            return None
        
        # Obtenir l'ID du membre depuis les balises
        element = selection[0]
        balises = self.arbre_membres.item(element, "tags")
        if not balises:
            return None
        
        id_membre = int(balises[0])  # Première balise est l'ID du membre
        return self.gestionnaire_donnees.obtenir_membre_equipe(id_membre)
    
    def nouveau_membre(self):
        """Ajouter un nouveau membre d'équipe"""
        self.afficher_dialogue_membre_equipe(self.cadre_principal, self.gestionnaire_donnees)
        self.actualiser()
    
    def modifier_membre(self):
        """Modifier le membre d'équipe sélectionné"""
        membre = self.obtenir_membre_selectionne()
        if membre:
            self.afficher_dialogue_membre_equipe(self.cadre_principal, self.gestionnaire_donnees, membre)
            self.actualiser()
    
    def supprimer_membre(self):
        """Supprimer le membre d'équipe sélectionné"""
        membre = self.obtenir_membre_selectionne()
        if not membre:
            return
        
        # Vérifier si le membre a des tâches assignées
        taches_assignees = [t for t in self.toutes_taches if t.assigne_a == membre.id and t.statut != "Terminé"]
        
        message_avertissement = f"Êtes-vous sûr de vouloir supprimer le membre d'équipe '{membre.nom}' ?"
        if taches_assignees:
            message_avertissement += f"\n\nCe membre a {len(taches_assignees)} tâches assignées qui seront désassignées."
        
        resultat = messagebox.askyesno("Confirmer la Suppression", message_avertissement)
        
        if resultat:
            try:
                self.gestionnaire_donnees.supprimer_membre_equipe(membre.id)
                messagebox.showinfo("Succès", "Membre d'équipe supprimé avec succès.")
                self.actualiser()
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de la suppression du membre d'équipe : {str(e)}")
    
    def voir_taches_membre(self):
        """Voir les tâches assignées au membre sélectionné"""
        membre = self.obtenir_membre_selectionne()
        if not membre:
            return
        
        # Créer la fenêtre d'affichage des tâches
        fenetre_taches = tk.Toplevel(self.cadre_principal)
        fenetre_taches.title(f"Tâches - {membre.nom}")
        fenetre_taches.geometry("800x500")
        
        # Tâches pour ce membre
        taches_membre = [t for t in self.toutes_taches if t.assigne_a == membre.id]
        
        # Créer l'arbre
        cadre = ttk.Frame(fenetre_taches, padding=20)
        cadre.pack(fill="both", expand=True)
        
        ttk.Label(cadre, text=f"Tâches assignées à {membre.nom}", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Arbre des tâches
        colonnes = ("Titre", "Projet", "Priorité", "Statut", "Échéance")
        arbre = ttk.Treeview(cadre, columns=colonnes, show="headings", height=15)
        
        for col in colonnes:
            arbre.heading(col, text=col)
            arbre.column(col, width=150)
        
        # Ajouter les tâches
        projets = {p.id: p for p in self.gestionnaire_donnees.charger_projets()}
        for tache in taches_membre:
            nom_projet = projets.get(tache.id_projet, type('obj', (object,), {'nom': 'Aucun Projet'})).nom
            
            arbre.insert("", "end", values=(
                tache.titre,
                nom_projet,
                tache.priorite,
                tache.statut,
                tache.echeance or "Pas d'échéance"
            ))
        
        # Barre de défilement
        barre_defilement = ttk.Scrollbar(cadre, orient="vertical", command=arbre.yview)
        arbre.configure(yscrollcommand=barre_defilement.set)
        
        arbre.pack(side="left", fill="both", expand=True)
        barre_defilement.pack(side="right", fill="y")
        
        if not taches_membre:
            ttk.Label(cadre, text="Aucune tâche assignée à ce membre.", 
                     font=("Arial", 12)).pack(pady=50)
    
    @staticmethod
    def afficher_dialogue_membre_equipe(parent, gestionnaire_donnees: GestionnaireDonnees, membre: MembreEquipe = None):
        """Afficher la boîte de dialogue de création/modification de membre d'équipe"""
        dialogue = tk.Toplevel(parent)
        dialogue.title("Modifier le Membre d'Équipe" if membre else "Nouveau Membre d'Équipe")
        dialogue.geometry("500x600")
        dialogue.resizable(False, False)
        dialogue.transient(parent)
        dialogue.grab_set()
        
        # Centrer la boîte de dialogue
        dialogue.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Variables
        var_nom = tk.StringVar(value=membre.nom if membre else "")
        var_email = tk.StringVar(value=membre.email if membre else "")
        var_role = tk.StringVar(value=membre.role if membre else "")
        var_disponibilite = tk.StringVar(value=str(membre.disponibilite) if membre else "100")
        var_heures_max = tk.StringVar(value=str(membre.heures_max_par_semaine) if membre else "40")
        
        # Créer le formulaire
        cadre_principal = ttk.Frame(dialogue, padding=20)
        cadre_principal.pack(fill="both", expand=True)
        
        ligne = 0
        
        # Nom
        ttk.Label(cadre_principal, text="Nom :*").grid(row=ligne, column=0, sticky="w", pady=(0, 5))
        ligne += 1
        entree_nom = ttk.Entry(cadre_principal, textvariable=var_nom, width=50)
        entree_nom.grid(row=ligne, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        entree_nom.focus()
        ligne += 1
        
        # Email
        ttk.Label(cadre_principal, text="Email :").grid(row=ligne, column=0, sticky="w", pady=(0, 5))
        ligne += 1
        entree_email = ttk.Entry(cadre_principal, textvariable=var_email, width=50)
        entree_email.grid(row=ligne, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        ligne += 1
        
        # Rôle
        ttk.Label(cadre_principal, text="Rôle :").grid(row=ligne, column=0, sticky="w", pady=(0, 5))
        ligne += 1
        entree_role = ttk.Entry(cadre_principal, textvariable=var_role, width=50)
        entree_role.grid(row=ligne, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        ligne += 1
        
        # Disponibilité et Heures Max
        cadre_details = ttk.Frame(cadre_principal)
        cadre_details.grid(row=ligne, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        cadre_details.grid_columnconfigure(1, weight=1)
        ligne += 1
        
        ttk.Label(cadre_details, text="Disponibilité (%) :").grid(row=0, column=0, sticky="w", padx=(0, 10))
        entree_disponibilite = ttk.Entry(cadre_details, textvariable=var_disponibilite, width=10)
        entree_disponibilite.grid(row=0, column=1, sticky="w", padx=(0, 20))
        
        ttk.Label(cadre_details, text="Heures Max/Semaine :").grid(row=0, column=2, sticky="w", padx=(0, 10))
        entree_heures = ttk.Entry(cadre_details, textvariable=var_heures_max, width=10)
        entree_heures.grid(row=0, column=3, sticky="w")
        
        # Compétences
        ttk.Label(cadre_principal, text="Compétences (une par ligne) :").grid(row=ligne, column=0, sticky="w", pady=(0, 5))
        ligne += 1
        texte_competences = tk.Text(cadre_principal, width=50, height=8)
        texte_competences.grid(row=ligne, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        if membre and membre.competences:
            texte_competences.insert("1.0", "\n".join(membre.competences))
        ligne += 1
        
        # Boutons
        cadre_boutons = ttk.Frame(cadre_principal)
        cadre_boutons.grid(row=ligne, column=0, columnspan=2, sticky="ew")
        
        def sauvegarder_membre():
            # Valider l'entrée
            nom = var_nom.get().strip()
            if not nom:
                messagebox.showerror("Erreur de Validation", "Le nom est requis.")
                return
            
            if not Validateurs.valider_longueur_texte(nom, longueur_max=100):
                messagebox.showerror("Erreur de Validation", "Le nom doit faire 100 caractères ou moins.")
                return
            
            email = var_email.get().strip()
            if email and not Validateurs.valider_email(email):
                messagebox.showerror("Erreur de Validation", "Format d'email invalide.")
                return
            
            # Valider la disponibilité
            try:
                disponibilite = int(var_disponibilite.get())
                if not (0 <= disponibilite <= 100):
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Erreur de Validation", "La disponibilité doit être un nombre entre 0 et 100.")
                return
            
            # Valider les heures max
            try:
                heures_max = int(var_heures_max.get())
                if heures_max < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Erreur de Validation", "Les heures max doivent être un entier non négatif.")
                return
            
            # Analyser les compétences
            competences = [c.strip() for c in texte_competences.get("1.0", "end-1c").split("\n") if c.strip()]
            
            try:
                if membre:
                    # Mettre à jour le membre existant
                    membre.nom = nom
                    membre.email = email
                    membre.role = var_role.get().strip()
                    membre.disponibilite = disponibilite
                    membre.heures_max_par_semaine = heures_max
                    membre.competences = competences
                    gestionnaire_donnees.mettre_a_jour_membre_equipe(membre)
                    messagebox.showinfo("Succès", "Membre d'équipe mis à jour avec succès.")
                else:
                    # Créer un nouveau membre
                    nouveau_membre = MembreEquipe(
                        nom=nom,
                        email=email,
                        role=var_role.get().strip()
                    )
                    nouveau_membre.disponibilite = disponibilite
                    nouveau_membre.heures_max_par_semaine = heures_max
                    nouveau_membre.competences = competences
                    gestionnaire_donnees.ajouter_membre_equipe(nouveau_membre)
                    messagebox.showinfo("Succès", "Membre d'équipe créé avec succès.")
                
                dialogue.destroy()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de la sauvegarde du membre d'équipe : {str(e)}")
        
        def annuler():
            dialogue.destroy()
        
        ttk.Button(cadre_boutons, text="Sauvegarder", command=sauvegarder_membre).pack(side="right", padx=(10, 0))
        ttk.Button(cadre_boutons, text="Annuler", command=annuler).pack(side="right")
        
        # Configurer les poids de la grille
        cadre_principal.grid_columnconfigure(0, weight=1)
        dialogue.grid_columnconfigure(0, weight=1)
        
        # Lier les touches
        dialogue.bind("<Return>", lambda e: sauvegarder_membre())
        dialogue.bind("<Escape>", lambda e: annuler())
