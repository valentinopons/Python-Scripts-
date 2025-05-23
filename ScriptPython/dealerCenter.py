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

def main():
    driver = None
    datos = []  # Lista para almacenar datos scrapeados

    try:
        # Iniciar navegador
        driver = setup_driver()
        print("✅ Navegador configurado correctamente")

        # Navegar a la página
        driver.get("https://app.dealercenter.net/apps/shell/reports/home")
        print("🔍 Cargando página...")

        wait = WebDriverWait(driver, 30)

        # Esperar input de búsqueda
        input_element = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "input.k-input-inner[placeholder*='Search Inventory']")
        ))

        # Esperar que desaparezca el loader
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "busy-loader--blocking")))

        # Interactuar con input
        input_element.click()
        print("Campo loan disponible. Escribiendo loan...")
        for char in LOAN_NUMBER:
            input_element.send_keys(char)
            time.sleep(0.1)

        xpath_deal = f"//div[contains(@class, 'search-result-item') and .//div[contains(text(), 'Deal #:') and contains(., '{LOAN_NUMBER}')]]"

        # Esperar que aparezca el deal y hacer click
        deal_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath_deal))
        )
        deal_element.click()

        # Cambiar a iframe del pop-up
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dc-iframe-dialog"))
        )
        driver.switch_to.frame(iframe)

        # Esperar y obtener los contenedores con datos
        containers = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.mb-2.d-flex.align-items-center"))
        )

        for container in containers:
            try:
                label_element = WebDriverWait(container, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".mr-auto.label, span.mr-auto.label"))
                )
                label = label_element.text.strip().lower().replace(" ", "_")

                input_element = WebDriverWait(container, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-valuenow]"))
                )
                valor_str = input_element.get_attribute("aria-valuenow")

                if valor_str and valor_str != "":
                    valor = float(valor_str)
                    if valor.is_integer():
                        valor = int(valor)
                else:
                    valor = None

                datos.append((label, valor))

            except Exception as e:
                print(f"No se pudo extraer información de un campo: {e}")

        print("Datos extraídos:")
        print(datos)

    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        if "This version of ChromeDriver" in str(e):
            print("⚠️ Por favor actualiza ChromeDriver: https://chromedriver.chromium.org/downloads")
    finally:
        if driver:
            driver.quit()
            print("🛑 Navegador cerrado")

if __name__ == "__main__":
    main()
