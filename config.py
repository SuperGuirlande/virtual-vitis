# URLs de base
BASE_URL = "https://phytochem.nal.usda.gov"
BASE_PLANT_URL = f"{BASE_URL}/plant-"
BASE_CHEMICAL_URL = f"{BASE_URL}/chemical-"
BASE_CHEMICAL_SEARCH_URL = f"{BASE_URL}/?type=chemical&keyword=&page="

# Sélecteurs CSS
SELECTORS = {
    # Sélecteurs pour les onglets
    'plants_tab': '#quicktabs-tab-chemical-1 a',
    'activities_tab': '#quicktabs-tab-chemical-0 a',
    
    # Sélecteurs pour la pagination
    'plants_pagination': '#quicktabs-tabpage-chemical-1 .pager__item--next a',
    'activities_pagination': '#quicktabs-tabpage-chemical-0 .pager__item--next a',
    
    # Sélecteurs pour les données
    'chemical_links': '.usa-collection__item .views-field-title a',
    'ubiquitous_status': '.field--name-chemical-is-ubiquitous .field--item',
    'table': '.table'
}

# Chemins des fichiers de données
DATA_PATHS = {
    'activities': "datas/all_chemicals_activities.csv",
    'plants': "datas/all_chemicals_plants.csv",
    'ubiquitous': "datas/chemicals_ubiquitous.csv"
}

# Temps d'attente (en secondes)
TIMEOUTS = {
    'page_load': 1.0,      # Attente après chargement de page
    'tab_switch': 0.3,     # Attente après changement d'onglet
    'data_save': 0.3,      # Attente après sauvegarde de données
    'pagination': 0.3      # Attente après changement de page
}

# Configuration du navigateur
BROWSER_CONFIG = {
    'viewport': {
        'width': 1920,
        'height': 1080
    },
    'headless': False
} 