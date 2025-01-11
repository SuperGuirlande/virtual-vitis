import pandas as pd

# OBJET ANALISEUR
class ChemicalAnalyzer:
    # Applatisssement des données
    def __init__(self, csv_file=None, dataframe=None):
        try:
            if dataframe is not None:
                self.df = dataframe.copy()
            elif csv_file is not None:
                self.df = pd.read_csv(csv_file)
            else:
                raise ValueError("Vous devez fournir un CSV valide")
            
            self.df.drop_duplicates()
            self._validate_dataframe()
            print(f"OK : Donnée chargées : {len(self.df)} entrées")

        except Exception as e:
            print(f"X Erreur lord du chargement du CSV : {e}")
            self.df = None
            
    def _validate_dataframe(self):
        required_columns = ['chemical','activity','dosage','reference']
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"Colonnes manquantes dans  le dataFrame : {missing_columns}")
        
    def list_all_chemicals(self, return_list=False):
        if self.df is None:
            return "Aucune donnée disponible"

        chemicals = sorted(self.df['chemical'].unique())

        if return_list:
            return chemicals
        
        print("\nListe des éléments chimique \n")

        for i, chem in enumerate(chemicals, 1):
            print(f"  - {i}. {chem}")

        return None
    
    def search_by_chemical(self, chemical_name, return_data=False):
        if self.df is None:
            return "Aucune donnée disponible"
        
        results = self.df[self.df['chemical'].str.lower() == chemical_name.lower()]

        if len(results) == 0:
            if not return_data:
                print(f"\n Aucune donnée à retourner pour {chemical_name}")
            return None
        
        if return_data:
            return results
        
        print(f"\n==== Réusultas de la recherche pour {chemical_name} : {len(results)} activités ===")
        print("\nACTIVITÉS :")
        for _, row in results.iterrows():
            print(f"\n -- {row['activity']}")
            print(f"   Dosage {row['dosage']}")
            print(f"   Référence {row['reference']}")

        return None
    
    def search_by_activity(self, activity, exact_match = False, return_data=False):
        if self.df is None:
            return "Aucune donnée disponible"
        
        if exact_match:
            results = self.df[self.df['activity'].str.lower() == activity.lower()]
        else:
            results = self.df[self.df['activity'].str.lower().str.contains(activity.lower(), na=False)]

        if len(results) == 0:
            if not return_data:
                print(f"\n Aucune donnée à retourner pour {activity}")
            return None
        
        if return_data:
            return results
        
        print(f"\n==== Réusultas de la recherche pour {activity} : {len(results)} resultats ===")
        grouped = results.groupby('chemical')

        print("\nAgents Chimiques :")
        for chemical, group in grouped:
            print(f"\n -- {chemical}")
            for _, row in group.iterrows():
                print(f"   Dosage {row['dosage']}")
                print(f"   Référence {row['reference']}")

        return None


    
def main():
    print("===== TRAITEMENT DES DONNÉES =====")
    print("\n")
    print("Choisissez le ficher à traiter")

    file = input("Nom du fichier >")

    while True:
        print("\nMENU D'ANALYSES")
        print('1: Lister tous les éléments chimiques')
        print('2: Rechercher un élément chimique')
        print('3: Rechercher une activité')

        action = input("Votre choix : ")

        if action == "1":
            analizer = ChemicalAnalyzer(csv_file=file)
            analizer.list_all_chemicals()
        elif action == "2":
            chemical = input(f"\nVeuillez entrer l'élément chimique à rechercher : \nVotre choix >")
            analizer = ChemicalAnalyzer(csv_file=file)
            analizer.search_by_chemical(chemical_name=chemical)
        elif action == "3":
            activity = input(f"\nVeuillez entrer l'activité à rechercher' : \nVotre choix >")
            analizer = ChemicalAnalyzer(csv_file=file)
            analizer.search_by_activity(activity=activity)
