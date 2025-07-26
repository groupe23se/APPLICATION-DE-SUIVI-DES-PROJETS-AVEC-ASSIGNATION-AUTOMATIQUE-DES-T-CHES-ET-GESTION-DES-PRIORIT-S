"""
Gestionnaire de base de données SQLite pour l'application de suivi des projets
"""

import sqlite3
import os
from datetime import datetime

class BaseDonnees:
    def __init__(self, chemin_db='donnees/suivi_projets.db'):
        """Initialiser la connexion à la base de données"""
        self.chemin_db = chemin_db
        
        # Créer le répertoire s'il n'existe pas
        os.makedirs(os.path.dirname(chemin_db), exist_ok=True)
        
        # Initialiser la base de données
        self.initialiser_db()
    
    def obtenir_connexion(self):
        """Obtenir une connexion à la base de données"""
        conn = sqlite3.connect(self.chemin_db)
        conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
        return conn
    
    def initialiser_db(self):
        """Créer les tables si elles n'existent pas"""
        with self.obtenir_connexion() as conn:
            curseur = conn.cursor()
            
            # Table des projets
            curseur.execute('''
                CREATE TABLE IF NOT EXISTS projets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    description TEXT,
                    statut TEXT NOT NULL DEFAULT 'Actif',
                    date_debut TEXT,
                    date_fin TEXT,
                    cree_le TEXT NOT NULL,
                    mis_a_jour_le TEXT NOT NULL
                )
            ''')
            
            # Table des membres d'équipe
            curseur.execute('''
                CREATE TABLE IF NOT EXISTS membres_equipe (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    email TEXT,
                    role TEXT,
                    disponibilite INTEGER DEFAULT 100,
                    heures_max_par_semaine INTEGER DEFAULT 40,
                    charge_travail_heures INTEGER DEFAULT 0,
                    cree_le TEXT NOT NULL,
                    mis_a_jour_le TEXT NOT NULL
                )
            ''')
            
            # Table des compétences des membres
            curseur.execute('''
                CREATE TABLE IF NOT EXISTS competences_membres (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    membre_id INTEGER NOT NULL,
                    competence TEXT NOT NULL,
                    FOREIGN KEY (membre_id) REFERENCES membres_equipe (id) ON DELETE CASCADE
                )
            ''')
            
            # Table des tâches
            curseur.execute('''
                CREATE TABLE IF NOT EXISTS taches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titre TEXT NOT NULL,
                    description TEXT,
                    id_projet INTEGER,
                    priorite TEXT NOT NULL DEFAULT 'Moyenne',
                    statut TEXT NOT NULL DEFAULT 'À faire',
                    assigne_a INTEGER,
                    echeance TEXT,
                    heures_estimees INTEGER DEFAULT 0,
                    cree_le TEXT NOT NULL,
                    mis_a_jour_le TEXT NOT NULL,
                    FOREIGN KEY (id_projet) REFERENCES projets (id) ON DELETE SET NULL,
                    FOREIGN KEY (assigne_a) REFERENCES membres_equipe (id) ON DELETE SET NULL
                )
            ''')
            
            # Table des compétences requises pour les tâches
            curseur.execute('''
                CREATE TABLE IF NOT EXISTS competences_taches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tache_id INTEGER NOT NULL,
                    competence TEXT NOT NULL,
                    FOREIGN KEY (tache_id) REFERENCES taches (id) ON DELETE CASCADE
                )
            ''')
            
            # Table des tâches assignées aux membres (pour historique)
            curseur.execute('''
                CREATE TABLE IF NOT EXISTS assignations_taches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    membre_id INTEGER NOT NULL,
                    tache_id INTEGER NOT NULL,
                    assigne_le TEXT NOT NULL,
                    FOREIGN KEY (membre_id) REFERENCES membres_equipe (id) ON DELETE CASCADE,
                    FOREIGN KEY (tache_id) REFERENCES taches (id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
    
    def executer_requete(self, requete, parametres=None):
        """Exécuter une requête et retourner les résultats"""
        with self.obtenir_connexion() as conn:
            curseur = conn.cursor()
            if parametres:
                curseur.execute(requete, parametres)
            else:
                curseur.execute(requete)
            return curseur.fetchall()
    
    def executer_modification(self, requete, parametres=None):
        """Exécuter une requête de modification (INSERT, UPDATE, DELETE)"""
        with self.obtenir_connexion() as conn:
            curseur = conn.cursor()
            if parametres:
                curseur.execute(requete, parametres)
            else:
                curseur.execute(requete)
            conn.commit()
            return curseur.lastrowid
    
    def maintenant(self):
        """Retourner la date/heure actuelle en format ISO"""
        return datetime.now().isoformat()
