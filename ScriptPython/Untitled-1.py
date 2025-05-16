from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Ruta donde guardar los PDFs
download_folder = "pdfs"
os.makedirs(download_folder, exist_ok=True)

# Configurar Chrome para descargar PDFs automáticamente
chrome_options = Options()
prefs = {
    "download.default_directory": os.path.abspath(download_folder),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
}
chrome_options.add_experimental_option("prefs", prefs)

try:
    # Iniciar navegador
    service = Service(r"C:\Users\ValentinoPons\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Ir al sitio web
    driver.get("https://app.dealercenter.net/apps/shell/reports/home")
    
    # Esperar a que el campo de búsqueda esté disponible
    print("buscando")
    search_field = WebDriverWait(driver, 300).until(
        EC.visibility_of_element_located((By.ID, "k-b22094e4-2578-48f4-880e-e428c914106c"))
        
    )
    print("lo encontre")
    search_field.click()
    # Buscar Loan
    loan_number = "6023"
    search_field.send_keys(loan_number)
    
    # Esperar y hacer click en el deal
    deal = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'container')]//div[contains(text(), 'Deal #:') and contains(., '{loan_number}')]"))
    )
    deal.click()

    # Ir a la sección de Files
    files_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "Files"))
    )
    files_link.click()

    # Esperar a que la tabla de archivos esté cargada
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//table//tbody//tr"))
    )

    # Descargar PDFs
    pdf_links = driver.find_elements(By.XPATH, "//table//tbody//tr//td[1]/a[contains(@href, '.pdf')]")
    
    for link in pdf_links:
        try:
            link.click()
            WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) == 1)  # Esperar si se abre nueva pestaña
        except Exception as e:
            print(f"Error al descargar archivo: {e}")
            continue

except Exception as e:
    print(f"Ocurrió un error: {e}")
finally:
    if 'driver' in locals():
        driver.quit()