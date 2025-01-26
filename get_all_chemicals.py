from playwright.sync_api import sync_playwright
import pandas as pd
import time
from plant_scrap import get_tab_data


def get_chemicals_links(page):
    chemical_links = page.evaluate('''() => {
        const links = document.querySelectorAll('.usa-collection__item .views-field-title a');
        return Array.from(links, link => ({
            url: link.href,
            name: link.textContent.trim()
        }));
    }''')
    return chemical_links


def get_ubiquitous_status(page):
    """Récupère le statut ubiquitous du chemical"""
    try:
        # Attendre que l'élément soit présent
        page.wait_for_selector('.field--name-chemical-is-ubiquitous .field--item', timeout=5000)
        ubiquitous_element = page.query_selector('.field--name-chemical-is-ubiquitous .field--item')
        if ubiquitous_element:
            status = ubiquitous_element.inner_text().strip()
            print(f"→ Statut ubiquitous: {status}")  # Debug
            return status
        print("→ Élément ubiquitous non trouvé")  # Debug
        return "Not found"
    except Exception as e:
        print(f"Erreur lors de la récupération du statut ubiquitous: {e}")
        return "Error"


# Naviguer vers la page suivante
def navigate_to_page(page, current_page_number):
    try:
        base_url = f"https://phytochem.nal.usda.gov/?type=chemical&keyword=&page={current_page_number}"
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        return True
    except Exception as e:
        print(f"n✗ Erreur {e}")


def main():
    start_page = input(f"A quelle page voulez vous commencer la récupération ? (0 pour la première)")
    max_pages = input(f"Combien de pages voulez vous récupérer")

    max_pages = int(max_pages) + int(start_page)

    with sync_playwright() as p:
        # Navigateur
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},  # Taille Full HD
            no_viewport=False
        )
        page = context.new_page()

        activities_data = []
        plants_data = []
        ubiquitous_data = []  # Nouvelle liste pour les données ubiquitous

        current_page = int(start_page)
        chemicals_number = 0

        try:
            print("====== LANCEMENT DU PROGRAMME DE RÉCUPERATION DES DONNEES =======")
            # Essai de naviguer a la page suivante
            while current_page < max_pages:
                if not navigate_to_page(page, current_page):
                    break

                print(f"\n####### PAGE {current_page + 1} #######")

                # Récupère tous les chemicals
                chemicals = get_chemicals_links(page)

                if not chemicals:
                    break

                
                # Récupérer tous les liens visibles
                for chemical in chemicals:
                    chemicals_number += 1
                    print(f"\n### Métabolite {chemicals_number}: {chemical['name']}")

                    try:
                        # D'abord aller sur la page du chemical
                        print(f"→ Navigation vers {chemical['url']}")
                        page.goto(chemical['url'])
                        time.sleep(.5)  # Attendre un peu plus longtemps
                        
                        # Ensuite récupérer le statut ubiquitous
                        ubiquitous_status = get_ubiquitous_status(page)
                        ubiquitous_data.append({
                            'chemical': chemical['name'],
                            'is_ubiquitous': ubiquitous_status
                        })

                        # Récupère les activités
                        print(f"→ Récupération des activités")
                        activities = get_tab_data(page, chemical, "Activities")
                        activities_data.extend(activities)

                        # Récupère les plantes
                        print(f"→ Récupération des plantes")

                        page.click('#quicktabs-tab-chemical-1 a')
                        time.sleep(.2)

                        plants = get_tab_data(page, chemical, "Plants")
                        plants_data.extend(plants)


                        # Sauvegarder les datas
                        pd.DataFrame(activities_data).to_csv("datas/all_chemicals_activities.csv", index=False, mode='a', header=False)
                        pd.DataFrame(plants_data).to_csv("datas/all_chemicals_plants.csv", index=False, mode='a', header=False)
                        pd.DataFrame(ubiquitous_data).to_csv("datas/chemicals_ubiquitous.csv", index=False, mode='a', header=False)

                        plants_data = []
                        activities_data = []
                        ubiquitous_data = []

                    except Exception as e:
                        print(f"n✗ Erreur {e}")

                current_page += 1
        except Exception as e:
            print(f"Erreur Complète du programme: {e}")
        finally:
            print(f"Nombre total traité : {chemicals_number}")
            context.close()
            browser.close()






