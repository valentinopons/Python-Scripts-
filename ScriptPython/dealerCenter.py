from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time

from selenium.webdriver.support.ui import WebDriverWait
import os

# Configuración a prueba de errores
CHROME_DRIVER_PATH = r"C:\Users\ValentinoPons\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
USER_DATA_DIR = r"C:\Users\ValentinoPons\AppData\Local\Google\Chrome\User Data"
loan_number = "5227"
try:
    # 1. Verificar que el ChromeDriver existe
    if not os.path.exists(CHROME_DRIVER_PATH):
        raise FileNotFoundError(f"❌ ChromeDriver no encontrado en: {CHROME_DRIVER_PATH}")

    # 2. Configurar el servicio correctamente
    service = Service(
        executable_path=CHROME_DRIVER_PATH,
        service_args=["--verbose", "--log-path=chromedriver.log"]
    )

    # 3. Opciones de Chrome optimizadas
    options = Options()
    #options.add_argument(f"user-data-dir={USER_DATA_DIR}")
    options.add_argument("profile-directory=Default")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # 4. Iniciar el navegador
    driver = webdriver.Chrome(service=service, options=options)
    
    # 5. Navegar a la página
    driver.get("https://app.dealercenter.net/apps/shell/reports/home")
    print("✅ ¡Navegador iniciado con sesión persistente!")
    
    wait = WebDriverWait(driver, 500)
    input_element = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "input.k-input-inner[placeholder*='Search Inventory']")
    ))
    #Este wait me sirve para esperar a que cargue la pagina
    WebDriverWait(driver, 30).until(
    EC.invisibility_of_element_located((By.CLASS_NAME, "busy-loader--blocking"))
)
    time.sleep(5) #Espero para sacar manual el pop 
    # Click en el input 
    input_element.click()
    print("Campo loan disponible. Escribiendo loan...")
    for char in loan_number:
            input_element.send_keys(char)
            time.sleep(0.1)
    
    xpath_deal = f"//div[contains(@class, 'search-result-item') and .//div[contains(text(), 'Deal #:') and contains(., '{loan_number}')]]"

    # Esperar hasta que el deal aparezca
    deal_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath_deal))
    )
    deal_element.click()
        
    # Tu código de automatización aquí...
    input("Presiona Enter para cerrar...")

except Exception as e:
    print(f"❌ Error crítico: {str(e)}")
    if "This version of ChromeDriver" in str(e):
        print("⚠️ Descarga la versión compatible de ChromeDriver: https://chromedriver.chromium.org/downloads")

finally:
    if 'driver' in locals():
        driver.quit()