from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import time

# Configuración de rutas
CHROME_DRIVER_PATH = r"C:\Users\ValentinoPons\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
PROFILE_PATH = r"C:\Users\ValentinoPons\AppData\Local\Google\Chrome\User Data\SeleniumProfile"
LOAN_NUMBER = "6544"

def setup_driver():
    """Configura y retorna una instancia del driver de Chrome"""
    if not os.path.exists(CHROME_DRIVER_PATH):
        raise FileNotFoundError(f"ChromeDriver no encontrado en: {CHROME_DRIVER_PATH}")

    options = Options()
    os.makedirs(PROFILE_PATH, exist_ok=True)
    options.add_argument(f"user-data-dir={PROFILE_PATH}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    service = Service(
        executable_path=CHROME_DRIVER_PATH,
        service_args=["--log-path=chromedriver.log"]
    )
    
    return webdriver.Chrome(service=service, options=options)

def obtener_nombre_loan(deal_element):
    """Extrae el nombre del loan de un elemento deal"""
    nombre_cliente = deal_element.find_element(By.XPATH, ".//div[@class='row'][2]//div[@class='col-4 r-item']/span").text.strip()
        
    print(f"Nombre del cliente: {nombre_cliente}")
    return nombre_cliente
        

def main():
    driver = None
    try:
        # Iniciar navegador
        driver = setup_driver()
        print("✅ Navegador configurado correctamente")
        
        # Navegar a la página
        driver.get("https://app.dealercenter.net/apps/shell/reports/home")
        print("🔍 Cargando página...")
        
        # Esperar elementos
        wait = WebDriverWait(driver, 500)
        input_element = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input.k-input-inner[placeholder*='Search Inventory']")
        ))
        
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "busy-loader--blocking"))
        )
        
          # Espera adicional
        
        # Interactuar con elementos
        input_element.click()
        print("Campo loan disponible. Escribiendo loan...")
        for char in LOAN_NUMBER:  # Corregido: Usar LOAN_NUMBER en lugar de loan_number
            input_element.send_keys(char)
            time.sleep(0.1)
        
        xpath_deal = f"//div[contains(@class, 'search-result-item') and .//div[contains(text(), 'Deal #:') and contains(., '{LOAN_NUMBER}')]]"

        # Esperar hasta que el deal aparezca
        deal_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath_deal))
        )
        obtener_nombre_loan(deal_element)
        deal_element.click()
            
        # Obtener nombre del deal
        
        
        input("Presiona Enter para cerrar el navegador...")
        
    except Exception as e:
        print(f"❌ Error durante la ejecución: {str(e)}")
        if "This version of ChromeDriver" in str(e):
            print("⚠️ Por favor actualiza ChromeDriver: https://chromedriver.chromium.org/downloads")
    finally:
        if driver:
            driver.quit()
            print("🛑 Navegador cerrado")

if __name__ == "__main__":
    main()