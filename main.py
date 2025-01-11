from plant_scrap import main as plant_scrap
from traitement_datas import main as traitement_datas
import os

### PROGRAMME PRINCIPAL ###
# Ce programme regroupe tous les programmes de traitement des données des plantes


### FONCTIONS ###

# FONCTION : Créer le dossier datas s'il n'existe pas
def create_data_directory():
    """Crée le dossier datas s'il n'existe pas"""
    if not os.path.exists('datas'):
        os.makedirs('datas')

### FONCTION PRINCIPALE : Choix du programme ###
def main():
    create_data_directory()
    
    choice = input("\n\n----- ### AGRICULTEUR 2.0 ### -----\nL'assistant virtuel de l'agriculture\n\n----- CHOISISSEZ UNE ACTION -----\n1: RÉCUPÉRER LES DONNÉES D'UNE PLANTE\n2: PROGRAMME DE TRAITEMENT DES DONNES\n3: Arrêter le programme\nVotre choix > ")
    ##### CHOIX 1 : RECUPERER LES DONNEES D'UNE PLANTE #####
    if choice == "1":
        # Récupérer le nom de la plante
        plant = input("Quelle plante voulez-vous récupérer ? ")
        # Récupérer le nombre de pages à collecter
        page_number = input("Combien de pages voulez-vous récupérer ? (Laisser vide pour récupérer toutes les pages)")
        # Convertir page_number en entier s'il n'est pas vide
        if page_number:
            try:
                page_number = int(page_number)
            except ValueError:
                print("Le nombre de pages doit être un nombre entier")
                return
        else:
            page_number = float('inf')
        # Création de l'url de la plante
        BASE_PLANT_URL = "https://phytochem.nal.usda.gov/plant-" # URL de base des plantes
        plant_url = f"{BASE_PLANT_URL}{plant.lower().replace(' ', '-')}" # Création de l'url de la plante

        # Création des chemins pour les fichiers CSV
        activities_file = f"datas/{plant.lower().replace(' ', '-')}-activities.csv"
        plants_file = f"datas/{plant.lower().replace(' ', '-')}-plants.csv"
        
        # Lancement du programme
        print(f"URL de la plante : {plant_url}")
        print(f"Récupération des données de la plante {plant}...")
        print("--------------------------------")
        print("LANCEMENT DU PROGRAMME")
        print("--------------------------------")
        plant_scrap(plant_url, plant, page_number)

    elif choice == "2":
        traitement_datas()
    elif choice == "3":
        print("Arrêt du programme")
        exit()
    else:
        print("Choix invalide")

# LANCEMENT DU PROGRAMME #
if __name__ == "__main__":
    main()
