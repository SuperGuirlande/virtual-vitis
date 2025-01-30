from playwright.sync_api import sync_playwright
import pandas as pd
import time
from plant_scrap import get_tab_data
from config import SELECTORS, DATA_PATHS, TIMEOUTS, BROWSER_CONFIG, BASE_CHEMICAL_SEARCH_URL


def get_chemicals_links(page):
    chemical_links = page.evaluate(f'''() => {{
        const links = document.querySelectorAll('{SELECTORS["chemical_links"]}');
        return Array.from(links, link => ({{
            url: link.href,
            name: link.textContent.trim()
        }}));
    }}''')
    return chemical_links


def get_ubiquitous_status(page):
    """Récupère le statut ubiquitous du chemical"""
    try:
        ubiquitous_element = page.query_selector(SELECTORS['ubiquitous_status'])
        if ubiquitous_element:
            status = ubiquitous_element.inner_text().strip()
            print(f"→ Statut ubiquitous: {status}")
            return status
        print("→ Élément ubiquitous non trouvé")
        return "Not found"
    except Exception as e:
        print(f"Erreur lors de la récupération du statut ubiquitous: {e}")
        return "Error"


def navigate_to_page(page, current_page_number):
    try:
        url = f"{BASE_CHEMICAL_SEARCH_URL}{current_page_number}"
        page.goto(url)
        time.sleep(TIMEOUTS['page_load'])
        return True
    except Exception as e:
        print(f"n✗ Erreur {e}")
        return False


def main():
    start_page = input(f"A quelle page voulez vous commencer la récupération ? (0 pour la première)")
    max_pages = input(f"Combien de pages voulez vous récupérer")

    max_pages = int(max_pages) + int(start_page)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=BROWSER_CONFIG['headless'])
        context = browser.new_context(
            viewport=BROWSER_CONFIG['viewport'],
            no_viewport=False
        )
        page = context.new_page()

        activities_data = []
        plants_data = []
        ubiquitous_data = []

        current_page = int(start_page)
        chemicals_number = 0

        try:
            print("====== LANCEMENT DU PROGRAMME DE RÉCUPERATION DES DONNEES =======")
            while current_page < max_pages:
                if not navigate_to_page(page, current_page):
                    break

                print(f"\n####### PAGE {current_page + 1} #######")
                chemicals = get_chemicals_links(page)

                if not chemicals:
                    break

                for chemical in chemicals:
                    chemicals_number += 1
                    print(f"\n### Métabolite {chemicals_number}: {chemical['name']}")

                    try:
                        print(f"→ Navigation vers {chemical['url']}")
                        page.goto(chemical['url'])
                        time.sleep(TIMEOUTS['page_load'])
                        
                        ubiquitous_status = get_ubiquitous_status(page)
                        ubiquitous_data.append({
                            'chemical': chemical['name'],
                            'is_ubiquitous': ubiquitous_status
                        })

                        print(f"→ Récupération des activités")
                        activities = get_tab_data(page, chemical, "Activities")
                        activities_data.extend(activities)

                        print(f"→ Récupération des plantes")
                        page.click(SELECTORS['plants_tab'])
                        time.sleep(TIMEOUTS['tab_switch'])

                        plants = get_tab_data(page, chemical, "Plants")
                        plants_data.extend(plants)
                        time.sleep(TIMEOUTS['data_save'])

                        # Sauvegarder les datas
                        pd.DataFrame(activities_data).to_csv(DATA_PATHS['activities'], index=False, mode='a', header=False)
                        pd.DataFrame(plants_data).to_csv(DATA_PATHS['plants'], index=False, mode='a', header=False)
                        pd.DataFrame(ubiquitous_data).to_csv(DATA_PATHS['ubiquitous'], index=False, mode='a', header=False)

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






