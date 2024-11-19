from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


# Initialisation du WebDriver (chemin vers votre driver Chrome)
driver_path = "C:/Users/ANTEC/Downloads/MIF_map/scaped/chromedriver-win64/chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service)
 

# Liste pour stocker les données
# Charger la page
driver.get("https://www.marques-de-france.fr/listing/")
url = "https://www.marques-de-france.fr/listing/"

# Attente explicite pour que l'élément soit visible
wait = WebDriverWait(driver, 10)
page_number = 1

# Fonction pour récupérer le favicon
def get_favicon(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    favicon = soup.find('link', rel='icon')
    if favicon and 'href' in favicon.attrs:
        return favicon.attrs['href']
    return None

def clean_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

with open('marques_france.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['name', 'description', 'image_url', 'link', 'favicon_url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    try:
        while True:  # On va continuer tant que la page contient des marques
            print(f"Chargement de la page {page_number}...")
            
            # Récupérer tous les éléments li de la liste
            list_items = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="archive-listings"]/div/div/ol/li')))
            
            # Boucle sur chaque élément li
            for index, li in enumerate(list_items, start=1):
                try:
                    # Dynamique XPath pour récupérer le nom
                    name_xpath = f'//*[@id="archive-listings"]/div/div/ol/li[{index}]/a/div/div[2]/h3'
                    name_element = driver.find_element(By.XPATH, name_xpath)
                    name = name_element.text

                    # Dynamique XPath pour récupérer la description
                    description_xpath = f'//*[@id="archive-listings"]/div/div/ol/li[{index}]/a/div/div[2]/small'
                    description_element = driver.find_element(By.XPATH, description_xpath)
                    description = description_element.text

                    # Dynamique XPath pour récupérer l'URL de l'image
                    image_xpath = f'//*[@id="archive-listings"]/div/div/ol/li[{index}]/a/div/div[1]/div[1]/img'
                    image_element = driver.find_element(By.XPATH, image_xpath)
                    image_url = image_element.get_attribute('src')  # Récupérer l'URL de l'image

                    # Cliquer sur le lien pour ouvrir la page détaillée
                    link_xpath = f'//*[@id="archive-listings"]/div/div/ol/li[{index}]/a'
                    link_element = driver.find_element(By.XPATH, link_xpath)
                    link_element.click()  # Cliquer sur le lien

                    # Attendre que la page se charge et récupérer l'URL
                    wait.until(EC.presence_of_element_located((By.ID, "listing-store-link")))
                    page_url = driver.find_element(By.ID, "listing-store-link").get_attribute("href")
                    page_url = clean_url(page_url)
                    favicon_url = get_favicon(page_url)
                    

                    # Revenir à la page précédente
                    driver.back()
                    time.sleep(2)  # Attendre un peu pour éviter une navigation trop rapide

                    # Afficher les résultats
                    print(f"Nom {index}: {name}")
                    print(f"Description {index}: {description}")
                    print(f"Image URL {index}: {image_url}")
                    print(f"Link {index}: {page_url}")

                    # Ajouter au fichier CSV
                    writer.writerow({'name': name, 'description': description, 'image_url': image_url, 'link': page_url, 'favicon_url': favicon_url})
                    
                except Exception as e:
                    print(f"Erreur pour l'élément {index}: {e}")
            
            # Incrémenter le numéro de page et mettre à jour l'URL
            page_number += 1
            new_url = f"{url}?page={page_number}"
            driver.get(new_url)  # Naviguer vers la page suivante
            time.sleep(2)  # Attendre un peu pour que la page charge

    except Exception as e:
        print(f"Erreur lors du chargement des éléments: {e}")

# Fermer le navigateur
driver.quit()