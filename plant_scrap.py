from playwright.sync_api import sync_playwright
import pandas as pd
import time
from config import SELECTORS, TIMEOUTS, BROWSER_CONFIG, BASE_PLANT_URL

### FONCTIONNEMENT DU PROGRAMME ###

# 1. Récupérer toute la liste des chemicals sur le tableau
# 2. Récupérer les infos des tableaux de la page du chemical
# 3. Récupérer les données des tableaux ACTIVITIES de la page du chemical
# 4. Sauvegarde dans un fichier CSV ACTIVITIES
# 5. Récupérer les données des tableaux PLANTS de la page du chemical
# 6. Sauvegarde dans un fichier CSV PLANTS
# 7. Naviguer vers la page suivante
# 8. Répéter les étapes 3 à 7 pour chaque chemical


### FONCTIONS ###

# Récupérer la liste des chemicals sur le tableau
def get_chemicals_links(page):
    chemical_links = page.evaluate('''() => {
        const chemicalTable = document.querySelector('.view-plant-chemicals');
        if (!chemicalTable) return [];
        
        // Sélectionner tous les liens sauf ceux dans l'en-tête (thead)
        const links = chemicalTable.querySelectorAll('tbody .views-field-title a');
        
        return Array.from(links, link => ({
            url: link.href,
            name: link.textContent.trim()
        }));
    }''')
    return chemical_links

# Récupérer les infos des tableaux de la page du chemical
def get_tab_data(page, chemical, tab_type):
    has_table = page.evaluate(f'''() => document.querySelector('{SELECTORS["table"]}') !==null;''')
    
    # On vérifie si c'est le tableau Activities ou Plants
    if not has_table:
        if tab_type == "Plants":
            return [{
                'chemical': chemical['name'],
                'plant': 'Non disponible',
                'plant_part': "Non disponible", 
                'low_ppm': "Non disponible",
                'high_ppm': "Non disponible",
                'std_dev': "Non disponible",
                'reference': 'No table found'
            }]
        else:
            return [{
                'chemical': chemical['name'],
                'activity': 'Non disponible',
                'dosage': 'Non disponible',
                'reference': 'No table found'
            }]
    
    all_tab_data = []
    
    # Récupérer les données de la première page
    if tab_type == "Plants":
        table_data = get_plants_table_data(page, chemical)
    else:  # Activities
        table_data = get_activities_table_data(page, chemical)
    all_tab_data.extend(table_data)
    
    # Sélectionner le bon conteneur de pagination selon l'onglet
    pagination_selector = SELECTORS['plants_pagination'] if tab_type == "Plants" else SELECTORS['activities_pagination']
    
    page_number = 1
    print(f"   → {tab_type} page {page_number}")
    
    # Vérifier s'il y a une page suivante
    while True:
        try:
            next_button = page.locator(pagination_selector)
            if not next_button.is_visible():
                break
                
            next_button.click()
            page.wait_for_load_state("networkidle", timeout=5000)
            time.sleep(TIMEOUTS['pagination'])
            
            page_number += 1
            print(f"   → {tab_type} page {page_number}")
            
            if tab_type == "Plants":
                table_data = get_plants_table_data(page, chemical)
            else:
                table_data = get_activities_table_data(page, chemical)
            all_tab_data.extend(table_data)
            
        except Exception as e:
            print(f"Erreur lors de la navigation : {e}")
            break
    
    return all_tab_data

# Récupérer les données des tableaux PLANTS de la page du chemical
def get_plants_table_data(page, chemical):
    data = page.evaluate('''() => {
        const plantsTab = document.querySelector('#quicktabs-tabpage-chemical-1:not(.quicktabs-hide)');
        if (!plantsTab) return [];
        
        const rows = plantsTab.querySelectorAll('.table tbody tr');
        return Array.from(rows, row => {
            const cells = row.querySelectorAll('td');
            return {
                plant: cells[0]?.textContent.trim() || '',
                part: cells[1]?.textContent.trim() || '',
                low_ppm: cells[2]?.textContent.trim() || '',
                high_ppm: cells[3]?.textContent.trim() || '',
                std_dev: cells[4]?.textContent.trim() || '',
                reference: cells[5]?.textContent.trim() || '',
            }                     
        });                  
    }''')
    return [{'chemical': chemical['name'], 
            'plant': item['plant'],
            'plant_part': item['part'],
            'low_ppm': item['low_ppm'],
            'high_ppm': item['high_ppm'],
            'std_dev': item['std_dev'],
            'reference': item['reference']} 
            for item in data]

# Récupérer les données des tableaux ACTIVITIES de la page du chemical
def get_activities_table_data(page, chemical):
    data = page.evaluate('''() => {
        const activitiesTab = document.querySelector('#quicktabs-tabpage-chemical-0:not(.quicktabs-hide)');
        if (!activitiesTab) return [];
        
        const rows = activitiesTab.querySelectorAll('.table tbody tr');
        return Array.from(rows, row => {
            const cells = row.querySelectorAll('td');
            return {
                activity: cells[0]?.textContent.trim() || '',
                dosage: cells[1]?.textContent.trim() || '',
                reference: cells[2]?.textContent.trim() || '',
            }                     
        });                  
    }''')
    return [{'chemical': chemical['name'], 
            'activity': item['activity'],
            'dosage': item['dosage'], 
            'reference': item['reference']} 
            for item in data]

# Naviguer vers la page suivante
def navigate_to_page(page, current_page_number):
    try:
        print(f"Page {current_page_number}", end=" ", flush=True)
        
        # Cliquer sur Next pour aller à la page suivante
        next_button = page.locator('.pager__item--next a').first
        if next_button.is_visible():
            next_button.click()
            time.sleep(.5)
            print("✓")
            return True
        else:
            print("✗")
            return False
            
    except Exception as e:
        print(f"\n✗ Erreur navigation page {current_page_number}: {e}")
        return False


# FONCTION PRINCIPALE
def main(plant_url, plant_name, page_number=float('inf')):
    with sync_playwright() as p:
        # Configuration de la taille de l'écran
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},  # Taille Full HD
            no_viewport=False
        )
        page = context.new_page()

        plant_name = plant_name.replace(' ', '-').lower()
        base_url = plant_url
        activities_data = []
        plants_data = []
        current_page = 1
        chemicals_list = []  # Pour stocker tous les chemicals
        max_pages = page_number  # max_pages sera maintenant soit un nombre soit inf

        # Définir les chemins des fichiers CSV
        activities_file = f"datas/{plant_name}-activities.csv"
        plants_file = f"datas/{plant_name}-plants.csv"

        try:
            page.goto(base_url)
            time.sleep(0.5)

            # D'abord récupérer la liste complète des chemicals
            print("\n=== Récupération de la liste des chemicals ===")
            while current_page <= max_pages:  # Cette comparaison fonctionnera maintenant
                if current_page > 1:
                    if not navigate_to_page(page, current_page):
                        break

                chemicals = get_chemicals_links(page)
                if not chemicals:
                    break
                
                chemicals_list.extend(chemicals)
                current_page += 1

            # Première passe : récupérer toutes les activités
            print("\n=== Récupération des activités ===")
            for chemical in chemicals_list:
                try:
                    print(f"→ {chemical['name']} (Activities)")
                    page.goto(chemical['url'])
                    time.sleep(.5)
                    activities = get_tab_data(page, chemical, "Activities")
                    activities_data.extend(activities)
                    
                    # Sauvegarder après chaque produit
                    activities_df = pd.DataFrame(activities_data)
                    activities_df.to_csv(activities_file, index=False)
                except Exception as e:
                    print(f"Erreur sur {chemical['name']} : {e}")
                    continue

            # Deuxième passe : récupérer toutes les plantes
            print("\n=== Récupération des plantes ===")
            for chemical in chemicals_list:
                try:
                    print(f"→ {chemical['name']} (Plants)")
                    page.goto(chemical['url'])
                    time.sleep(0.5)
                    page.click('#quicktabs-tab-chemical-1 a')
                    time.sleep(0.5)
                    plants = get_tab_data(page, chemical, "Plants")
                    plants_data.extend(plants)
                    time.sleep(.3)
                    
                    # Sauvegarder après chaque produit
                    plants_df = pd.DataFrame(plants_data)
                    plants_df.to_csv(plants_file, index=False)
                    time.sleep(.3)
                except Exception as e:
                    print(f"Erreur sur {chemical['name']} : {e}")
                    continue

        except Exception as e:
            print(f"Erreur {e}")
        finally:
            context.close()
            browser.close()


# LANCER LE PROGRAMME
if __name__ == '__main__':
    main()

    