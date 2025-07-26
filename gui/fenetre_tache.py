"""
Fenêtre de gestion des tâches avec assignation automatique
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from modeles.gestionnaire_donnees import GestionnaireDonnees
from modeles.tache import Tache
from utilitaires.moteur_assignation import MoteurAssignation
from utilitaires.validateurs import Validateurs

class FenetreTache:
    def __init__(self, parent, gestionnaire_donnees: GestionnaireDonnees, filtre_projet: str = None):
        self.parent = parent
        self.gestionnaire_donnees = gestionnaire_donnees
        self.filtre_projet = filtre_projet
        self.moteur_assignation = MoteurAssignation(gestionnaire_donnees)
        
        self.creer_widgets()
        self.actualiser()
    
    def creer_widgets(self):
        """Créer les widgets de gestion des tâches"""
        # Conteneur principal
        self.cadre_principal = ttk.Frame(self.parent)
        self.cadre_principal.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.cadre_principal.grid_rowconfigure(3, weight=1)
        self.cadre_principal.grid_columnconfigure(0, weight=1)
        
        # Titre
        texte_titre = "Gestion des Tâches"
        if self.filtre_projet:
            projet = self.gestionnaire_donnees.obtenir_projet(self.filtre_projet)
            if projet:
                texte_titre += f" - {projet.nom}"
        
        etiquette_titre = ttk.Label(self.cadre_principal, text=texte_titre, 
                                   font=("Arial", 16, "bold"))
        etiquette_titre.grid(row=0, column=0, pady=(0, 20))
        
        # Barre d'outils
        cadre_barre_outils = ttk.Frame(self.cadre_principal)
        cadre_barre_outils.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Boutons
        ttk.Button(cadre_barre_outils, text="Nouvelle Tâche", 
                  command=self.nouvelle_tache).pack(side="left", padx=(0, 10))
        ttk.Button(cadre_barre_outils, text="Modifier Tâche", 
                  command=self.modifier_tache).pack(side="left", padx=(0, 10))
        ttk.Button(cadre_barre_outils, text="Supprimer Tâche", 
                  command=self.supprimer_tache).pack(side="left", padx=(0, 10))
        ttk.Button(cadre_barre_outils, text="Assignation Auto", 
                  command=self.assignation_auto_tache).pack(side="left", padx=(0, 10))
        ttk.Button(cadre_barre_outils, text="Marquer Terminé", 
                  command=self.marquer_termine).pack(side="left", padx=(0, 10))
        ttk.Button(cadre_barre_outils, text="Actualiser", 
                  command=self.actualiser).pack(side="right")
        
        # Cadre des filtres
        cadre_filtres = ttk.Frame(self.cadre_principal)
        cadre_filtres.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        # Recherche
        ttk.Label(cadre_filtres, text="Rechercher :").pack(side="left", padx=(0, 5))
        self.var_recherche = tk.StringVar()
        self.var_recherche.trace("w", self.filtrer_taches)
        entree_recherche = ttk.Entry(cadre_filtres, textvariable=self.var_recherche, width=20)
        entree_recherche.pack(side="left", padx=(0, 10))
        
        # Filtre de projet (si pas déjà filtré)
        if not self.filtre_projet:
            ttk.Label(cadre_filtres, text="Projet :").pack(side="left", padx=(10, 5))
            self.var_projet = tk.StringVar(value="Tous")
            self.combo_projet = ttk.Combobox(cadre_filtres, textvariable=self.var_projet, 
                                            state="readonly", width=20)
            self.combo_projet.pack(side="left", padx=(0, 10))
            self.combo_projet.bind("<<ComboboxSelected>>", lambda e: self.filtrer_taches())
        
        # Filtre de statut
        ttk.Label(cadre_filtres, text="Statut :").pack(side="left", padx=(10, 5))
        self.var_statut = tk.StringVar(value="Tous")
        combo_statut = ttk.Combobox(cadre_filtres, textvariable=self.var_statut, 
                                   values=["Tous", "À faire", "En cours", "Terminé"],
                                   state="readonly", width=12)
        combo_statut.pack(side="left", padx=(0, 10))
        combo_statut.bind("<<ComboboxSelected>>", lambda e: self.filtrer_taches())
        
        # Filtre de priorité
        ttk.Label(cadre_filtres, text="Priorité :").pack(side="left", padx=(10, 5))
        self.var_priorite = tk.StringVar(value="Tous")
        combo_priorite = ttk.Combobox(cadre_filtres, textvariable=self.var_priorite, 
                                     values=["Tous", "Haute", "Moyenne", "Basse"],
                                     state="readonly", width=10)
        combo_priorite.pack(side="left")
        combo_priorite.bind("<<ComboboxSelected>>", lambda e: self.filtrer_taches())
        
        # Arbre des tâches
        self.creer_arbre_taches()
    
    def creer_arbre_taches(self):
        """Créer l'arbre des tâches"""
        cadre_arbre = ttk.Frame(self.cadre_principal)
        cadre_arbre.grid(row=3, column=0, sticky="nsew")
        cadre_arbre.grid_rowconfigure(0, weight=1)
        cadre_arbre.grid_columnconfigure(0, weight=1)
        
        # Colonnes
        colonnes = ["Titre", "Projet", "Priorité", "Statut", "Assigné à", "Échéance", "Créé"]
        if self.filtre_projet:
            colonnes.remove("Projet")
        
        self.arbre_taches = ttk.Treeview(cadre_arbre, columns=colonnes, show="headings")
        
        # Configurer les colonnes
        for col in colonnes:
            self.arbre_taches.heading(col, text=col)
        
        self.arbre_taches.column("Titre", width=200)
        if "Projet" in colonnes:
            self.arbre_taches.column("Projet", width=150)
        self.arbre_taches.column("Priorité", width=80)
        self.arbre_taches.column("Statut", width=100)
        self.arbre_taches.column("Assigné à", width=120)
        self.arbre_taches.column("Échéance", width=100)
        self.arbre_taches.column("Créé", width=100)
        
        # Barres de défilement
        defilement_v = ttk.Scrollbar(cadre_arbre, orient="vertical", command=self.arbre_taches.yview)
        defilement_h = ttk.Scrollbar(cadre_arbre, orient="horizontal", command=self.arbre_taches.xview)
        self.arbre_taches.configure(yscrollcommand=defilement_v.set, xscrollcommand=defilement_h.set)
        
        # Disposition en grille
        self.arbre_taches.grid(row=0, column=0, sticky="nsew")
        defilement_v.grid(row=0, column=1, sticky="ns")
        defilement_h.grid(row=1, column=0, sticky="ew")
        
        # Liaison double-clic
        self.arbre_taches.bind("<Double-1>", lambda e: self.modifier_tache())
    
    def actualiser(self):
        """Actualiser l'affichage des tâches"""
        self.taches = self.gestionnaire_donnees.charger_taches()
        self.projets = {p.id: p for p in self.gestionnaire_donnees.charger_projets()}
        self.membres_equipe = {m.id: m for m in self.gestionnaire_donnees.charger_membres_equipe()}
        
        # Mettre à jour le combo projet si pas filtré
        if not self.filtre_projet:
            noms_projets = ["Tous"] + [p.nom for p in self.projets.values()]
            self.combo_projet['values'] = noms_projets
        
        self.filtrer_taches()
    
    def filtrer_taches(self, *args):
        """Filtrer les tâches selon la recherche et les filtres"""
        # Effacer les éléments existants
        for element in self.arbre_taches.get_children():
            self.arbre_taches.delete(element)
        
        texte_recherche = self.var_recherche.get().lower()
        filtre_statut = self.var_statut.get()
        filtre_priorite = self.var_priorite.get()
        
        # Filtre de projet
        filtre_projet = None
        if self.filtre_projet:
            filtre_projet = self.filtre_projet
        elif hasattr(self, 'var_projet') and self.var_projet.get() != "Tous":
            # Trouver l'ID du projet par nom
            for pid, projet in self.projets.items():
                if projet.nom == self.var_projet.get():
                    filtre_projet = pid
                    break
        
        for tache in self.taches:
            # Appliquer les filtres
            if texte_recherche and texte_recherche not in tache.titre.lower() and texte_recherche not in tache.description.lower():
                continue
            
            if filtre_statut != "Tous" and tache.statut != filtre_statut:
                continue
            
            if filtre_priorite != "Tous" and tache.priorite != filtre_priorite:
                continue
            
            if filtre_projet and tache.id_projet != filtre_projet:
                continue
            
            # Obtenir les données d'affichage
            nom_projet = self.projets.get(tache.id_projet, type('obj', (object,), {'nom': 'Aucun Projet'})).nom
            nom_assigne = self.membres_equipe.get(tache.assigne_a, type('obj', (object,), {'nom': 'Non assigné'})).nom
            
            # Formater la date de création
            try:
                date_creation = tache.cree_le.split("T")[0]
            except:
                date_creation = tache.cree_le
            
            # Préparer les valeurs
            valeurs = [
                tache.titre,
                nom_projet,
                tache.priorite,
                tache.statut,
                nom_assigne,
                tache.echeance or "Pas d'échéance",
                date_creation
            ]
            
            # Supprimer la colonne projet si filtré
            if self.filtre_projet:
                valeurs.pop(1)
            
            # Déterminer les balises pour les couleurs
            balises = []
            if tache.priorite == Tache.PRIORITE_HAUTE:
                balises.append("haute_priorite")
            elif tache.priorite == Tache.PRIORITE_MOYENNE:
                balises.append("priorite_moyenne")
            else:
                balises.append("basse_priorite")
            
            if tache.statut == Tache.STATUT_TERMINE:
                balises.append("termine")
            
            # Vérifier si en retard
            if tache.echeance and tache.statut != Tache.STATUT_TERMINE:
                try:
                    date_echeance = datetime.strptime(tache.echeance, "%Y-%m-%d").date()
                    if date_echeance < date.today():
                        balises.append("en_retard")
                except ValueError:
                    pass
            
            self.arbre_taches.insert("", "end", values=valeurs, tags=[tache.id] + balises)
        
        # Configurer les balises pour les couleurs
        self.arbre_taches.tag_configure("haute_priorite", background="#ffebee")
        self.arbre_taches.tag_configure("priorite_moyenne", background="#fff3e0")
        self.arbre_taches.tag_configure("basse_priorite", background="#e8f5e8")
        self.arbre_taches.tag_configure("termine", background="#e0e0e0")
        self.arbre_taches.tag_configure("en_retard", background="#ffcdd2")
    
    def obtenir_tache_selectionnee(self):
        """Obtenir la tâche actuellement sélectionnée"""
        selection = self.arbre_taches.selection()
        if not selection:
            messagebox.showwarning("Aucune Sélection", "Veuillez sélectionner une tâche.")
            return None
        
        # Obtenir l'ID de la tâche depuis les balises
        element = selection[0]
        balises = self.arbre_taches.item(element, "tags")
        if not balises:
            return None
        
        id_tache = int(balises[0])  # Première balise est l'ID de la tâche
        return self.gestionnaire_donnees.obtenir_tache(id_tache)
    
    def nouvelle_tache(self):
        """Créer une nouvelle tâche"""
        self.afficher_dialogue_tache(self.cadre_principal, self.gestionnaire_donnees, filtre_projet=self.filtre_projet)
        self.actualiser()
    
    def modifier_tache(self):
        """Modifier la tâche sélectionnée"""
        tache = self.obtenir_tache_selectionnee()
        if tache:
            self.afficher_dialogue_tache(self.cadre_principal, self.gestionnaire_donnees, tache)
            self.actualiser()
    
    def supprimer_tache(self):
        """Supprimer la tâche sélectionnée"""
        tache = self.obtenir_tache_selectionnee()
        if not tache:
            return
        
        # Confirmer la suppression
        resultat = messagebox.askyesno(
            "Confirmer la Suppression",
            f"Êtes-vous sûr de vouloir supprimer la tâche '{tache.titre}' ?"
        )
        
        if resultat:
            try:
                self.gestionnaire_donnees.supprimer_tache(tache.id)
                messagebox.showinfo("Succès", "Tâche supprimée avec succès.")
                self.actualiser()
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de la suppression de la tâche : {str(e)}")
    
    def assignation_auto_tache(self):
        """Assigner automatiquement la tâche sélectionnée"""
        tache = self.obtenir_tache_selectionnee()
        if not tache:
            return
        
        if tache.assigne_a:
            resultat = messagebox.askyesno(
                "Tâche Déjà Assignée",
                f"La tâche est déjà assignée à {self.membres_equipe.get(tache.assigne_a, type('obj', (object,), {'nom': 'Inconnu'})).nom}.\n"
                "Voulez-vous la réassigner ?"
            )
            if not resultat:
                return
        
        # Trouver le meilleur membre d'équipe pour cette tâche
        meilleur_membre = self.moteur_assignation.trouver_meilleur_assignataire(tache)
        
        if not meilleur_membre:
            messagebox.showwarning("Aucune Assignation", "Aucun membre d'équipe approprié trouvé pour cette tâche.")
            return
        
        # Assigner la tâche
        ancien_assigne_a = tache.assigne_a
        ancien_membre = self.gestionnaire_donnees.obtenir_membre_equipe(ancien_assigne_a) if ancien_assigne_a else None
        
        # Mettre à jour l'ancien assignataire
        if ancien_membre:
            ancien_membre.desassigner_tache(tache.id, tache.heures_estimees)
            self.gestionnaire_donnees.mettre_a_jour_membre_equipe(ancien_membre)
        
        # Assigner au nouveau membre
        tache.assigner_a(meilleur_membre.id)
        meilleur_membre.assigner_tache(tache.id, tache.heures_estimees)
        
        # Sauvegarder les changements
        self.gestionnaire_donnees.mettre_a_jour_tache(tache)
        self.gestionnaire_donnees.mettre_a_jour_membre_equipe(meilleur_membre)
        
        messagebox.showinfo(
            "Tâche Assignée",
            f"La tâche '{tache.titre}' a été assignée à {meilleur_membre.nom}."
        )
        self.actualiser()
    
    def marquer_termine(self):
        """Marquer la tâche sélectionnée comme terminée"""
        tache = self.obtenir_tache_selectionnee()
        if not tache:
            return
        
        if tache.statut == Tache.STATUT_TERMINE:
            messagebox.showinfo("Déjà Terminé", "La tâche est déjà marquée comme terminée.")
            return
        
        # Marquer comme terminée
        tache.marquer_termine()
        
        # Mettre à jour la charge de travail de l'assignataire
        if tache.assigne_a:
            membre = self.gestionnaire_donnees.obtenir_membre_equipe(tache.assigne_a)
            if membre:
                membre.desassigner_tache(tache.id, tache.heures_estimees)
                self.gestionnaire_donnees.mettre_a_jour_membre_equipe(membre)
        
        # Sauvegarder les changements
        self.gestionnaire_donnees.mettre_a_jour_tache(tache)
        
        messagebox.showinfo("Succès", "Tâche marquée comme terminée.")
        self.actualiser()
    
    @staticmethod
    def afficher_dialogue_tache(parent, gestionnaire_donnees: GestionnaireDonnees, tache: Tache = None, filtre_projet: str = None):
        """Afficher la boîte de dialogue de création/modification de tâche"""
        dialogue = tk.Toplevel(parent)
        dialogue.title("Modifier la Tâche" if tache else "Nouvelle Tâche")
        dialogue.geometry("600x700")
        dialogue.resizable(False, False)
        dialogue.transient(parent)
        dialogue.grab_set()
        
        # Centrer la boîte de dialogue
        dialogue.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Charger les données
        projets = gestionnaire_donnees.charger_projets()
        membres_equipe = gestionnaire_donnees.charger_membres_equipe()
        
        # Variables
        var_titre = tk.StringVar(value=tache.titre if tache else "")
        var_description = tk.StringVar(value=tache.description if tache else "")
        
        # Formater l'ID de projet pour l'affichage
        projet_display = ""
        if tache and tache.id_projet:
            projet_obj = gestionnaire_donnees.obtenir_projet(tache.id_projet)
            if projet_obj:
                projet_display = f"{projet_obj.id} - {projet_obj.nom}"
        elif filtre_projet:
            projet_obj = gestionnaire_donnees.obtenir_projet(filtre_projet)
            if projet_obj:
                projet_display = f"{projet_obj.id} - {projet_obj.nom}"
        
        var_projet = tk.StringVar(value=projet_display)
        var_priorite = tk.StringVar(value=tache.priorite if tache else Tache.PRIORITE_MOYENNE)
        var_statut = tk.StringVar(value=tache.statut if tache else Tache.STATUT_A_FAIRE)
        
        # Formater l'ID de membre assigné pour l'affichage
        assigne_display = ""
        if tache and tache.assigne_a:
            membre_obj = gestionnaire_donnees.obtenir_membre_equipe(tache.assigne_a)
            if membre_obj:
                assigne_display = f"{membre_obj.id} - {membre_obj.nom}"
        
        var_assigne = tk.StringVar(value=assigne_display)
        var_echeance = tk.StringVar(value=tache.echeance if tache else "")
        var_heures = tk.StringVar(value=str(tache.heures_estimees) if tache else "0")
        
        # Créer le formulaire
        cadre_principal = ttk.Frame(dialogue, padding=20)
        cadre_principal.pack(fill="both", expand=True)
        
        # Titre de la tâche
        ttk.Label(cadre_principal, text="Titre :*").pack(anchor="w", pady=(0, 5))
        entree_titre = ttk.Entry(cadre_principal, textvariable=var_titre, width=60)
        entree_titre.pack(fill="x", pady=(0, 15))
        entree_titre.focus()
        
        # Description
        ttk.Label(cadre_principal, text="Description :").pack(anchor="w", pady=(0, 5))
        texte_description = tk.Text(cadre_principal, width=60, height=6)
        texte_description.pack(fill="x", pady=(0, 15))
        texte_description.insert("1.0", var_description.get())
        
        # Cadre des détails
        cadre_details = ttk.Frame(cadre_principal)
        cadre_details.pack(fill="x", pady=(0, 15))
        
        # Projet
        ttk.Label(cadre_details, text="Projet :").grid(row=0, column=0, sticky="w", padx=(0, 10))
        combo_projet = ttk.Combobox(cadre_details, textvariable=var_projet, width=25)
        combo_projet['values'] = [f"{p.id} - {p.nom}" for p in projets]
        combo_projet.grid(row=0, column=1, sticky="w", padx=(0, 20))
        
        # Priorité
        ttk.Label(cadre_details, text="Priorité :").grid(row=0, column=2, sticky="w", padx=(0, 10))
        combo_priorite = ttk.Combobox(cadre_details, textvariable=var_priorite, 
                                     values=[Tache.PRIORITE_HAUTE, Tache.PRIORITE_MOYENNE, Tache.PRIORITE_BASSE],
                                     state="readonly", width=15)
        combo_priorite.grid(row=0, column=3, sticky="w")
        
        # Statut
        ttk.Label(cadre_details, text="Statut :").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        combo_statut = ttk.Combobox(cadre_details, textvariable=var_statut, 
                                   values=[Tache.STATUT_A_FAIRE, Tache.STATUT_EN_COURS, Tache.STATUT_TERMINE],
                                   state="readonly", width=25)
        combo_statut.grid(row=1, column=1, sticky="w", padx=(0, 20), pady=(10, 0))
        
        # Assigné à
        ttk.Label(cadre_details, text="Assigné à :").grid(row=1, column=2, sticky="w", padx=(0, 10), pady=(10, 0))
        combo_assigne = ttk.Combobox(cadre_details, textvariable=var_assigne, width=15)
        combo_assigne['values'] = [""] + [f"{m.id} - {m.nom}" for m in membres_equipe]
        combo_assigne.grid(row=1, column=3, sticky="w", pady=(10, 0))
        
        # Échéance et heures estimées
        cadre_date_heures = ttk.Frame(cadre_principal)
        cadre_date_heures.pack(fill="x", pady=(0, 15))
        
        ttk.Label(cadre_date_heures, text="Échéance (YYYY-MM-DD) :").grid(row=0, column=0, sticky="w", padx=(0, 10))
        entree_echeance = ttk.Entry(cadre_date_heures, textvariable=var_echeance, width=15)
        entree_echeance.grid(row=0, column=1, sticky="w", padx=(0, 20))
        
        ttk.Label(cadre_date_heures, text="Heures estimées :").grid(row=0, column=2, sticky="w", padx=(0, 10))
        entree_heures = ttk.Entry(cadre_date_heures, textvariable=var_heures, width=10)
        entree_heures.grid(row=0, column=3, sticky="w")
        
        # Compétences requises
        ttk.Label(cadre_principal, text="Compétences requises (une par ligne) :").pack(anchor="w", pady=(0, 5))
        texte_competences = tk.Text(cadre_principal, width=60, height=4)
        texte_competences.pack(fill="x", pady=(0, 20))
        if tache and tache.competences_requises:
            texte_competences.insert("1.0", "\n".join(tache.competences_requises))
        
        # Boutons
        cadre_boutons = ttk.Frame(cadre_principal)
        cadre_boutons.pack(fill="x")
        
        def sauvegarder_tache():
            # Valider l'entrée
            titre = var_titre.get().strip()
            if not titre:
                messagebox.showerror("Erreur de Validation", "Le titre de la tâche est requis.")
                return
            
            if not Validateurs.valider_longueur_texte(titre, longueur_max=200):
                messagebox.showerror("Erreur de Validation", "Le titre doit faire 200 caractères ou moins.")
                return
            
            description = texte_description.get("1.0", "end-1c").strip()
            if not Validateurs.valider_longueur_texte(description, longueur_max=1000):
                messagebox.showerror("Erreur de Validation", "La description doit faire 1000 caractères ou moins.")
                return
            
            # Valider l'échéance
            echeance = var_echeance.get().strip()
            if echeance and not Validateurs.valider_date(echeance):
                messagebox.showerror("Erreur de Validation", "Format d'échéance invalide. Utilisez YYYY-MM-DD.")
                return
            
            # Valider les heures estimées
            try:
                heures_estimees = int(var_heures.get())
                if heures_estimees < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Erreur de Validation", "Les heures estimées doivent être un entier non négatif.")
                return
            
            # Extraire l'ID du projet depuis la chaîne d'affichage
            id_projet = None
            if var_projet.get().strip():
                try:
                    id_projet = int(var_projet.get().split(" - ")[0])
                except (ValueError, IndexError):
                    id_projet = None
            
            # Extraire l'ID du membre assigné depuis la chaîne d'affichage
            assigne_a = None
            if var_assigne.get().strip():
                try:
                    assigne_a = int(var_assigne.get().split(" - ")[0])
                except (ValueError, IndexError):
                    assigne_a = None
            
            # Analyser les compétences
            competences = [c.strip() for c in texte_competences.get("1.0", "end-1c").split("\n") if c.strip()]
            
            try:
                if tache:
                    # Mettre à jour la tâche existante
                    tache.titre = titre
                    tache.description = description
                    tache.id_projet = id_projet
                    tache.priorite = var_priorite.get()
                    tache.statut = var_statut.get()
                    tache.assigne_a = assigne_a
                    tache.echeance = echeance
                    tache.heures_estimees = heures_estimees
                    tache.competences_requises = competences
                    gestionnaire_donnees.mettre_a_jour_tache(tache)
                    messagebox.showinfo("Succès", "Tâche mise à jour avec succès.")
                else:
                    # Créer une nouvelle tâche
                    nouvelle_tache = Tache(
                        titre=titre,
                        description=description,
                        id_projet=id_projet,
                        priorite=var_priorite.get(),
                        echeance=echeance
                    )
                    nouvelle_tache.statut = var_statut.get()
                    nouvelle_tache.assigne_a = assigne_a
                    nouvelle_tache.heures_estimees = heures_estimees
                    nouvelle_tache.competences_requises = competences
                    gestionnaire_donnees.ajouter_tache(nouvelle_tache)
                    messagebox.showinfo("Succès", "Tâche créée avec succès.")
                
                dialogue.destroy()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de la sauvegarde de la tâche : {str(e)}")
        
        def annuler():
            dialogue.destroy()
        
        ttk.Button(cadre_boutons, text="Sauvegarder", command=sauvegarder_tache).pack(side="right", padx=(10, 0))
        ttk.Button(cadre_boutons, text="Annuler", command=annuler).pack(side="right")
        
        # Lier les touches
        dialogue.bind("<Return>", lambda e: sauvegarder_tache())
        dialogue.bind("<Escape>", lambda e: annuler())
