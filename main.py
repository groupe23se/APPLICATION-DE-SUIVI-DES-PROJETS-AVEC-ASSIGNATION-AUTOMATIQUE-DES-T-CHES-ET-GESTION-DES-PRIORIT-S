"""
Application de Suivi des Projets
Point d'entrée principal pour l'application de bureau
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys

# Ajouter le répertoire courant au chemin Python pour permettre les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.fenetre_principale import FenetrePrincipale

def principal():
    """Fonction principale pour démarrer l'application"""
    try:
        # Créer le répertoire données s'il n'existe pas
        if not os.path.exists('donnees'):
            os.makedirs('donnees')
        
        # Initialiser la fenêtre principale
        racine = tk.Tk()
        app = FenetrePrincipale(racine)
        
        # Démarrer l'application
        racine.mainloop()
        
    except Exception as e:
        messagebox.showerror("Erreur d'Application", f"Échec du démarrage de l'application : {str(e)}")

if __name__ == "__main__":
    principal()
