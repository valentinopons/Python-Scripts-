from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# Configuración mejorada
CHROME_DRIVER_PATH = r"C:\Users\ValentinoPons\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
PROFILE_PATH = r"C:\Users\ValentinoPons\AppData\Local\Google\Chrome\User Data\SeleniumProfile"  # Perfil dedicado
LOGIN_URL = "https://app.dealercenter.net/login"
TARGET_URL = "https://app.dealercenter.net/apps/shell/reports/home"

def setup_driver():
    """Configura el driver de Chrome con opciones optimizadas"""
    # Verificar que ChromeDriver existe
    if not os.path.exists(CHROME_DRIVER_PATH):
        raise FileNotFoundError(f"❌ ChromeDriver no encontrado en: {CHROME_DRIVER_PATH}")

    # Crear directorio para el perfil si no existe
    os.makedirs(PROFILE_PATH, exist_ok=True)

    options = Options()
    
    # Configuración del perfil persistente
    options.add_argument(f"user-data-dir={PROFILE_PATH}")
    options.add_argument("--profile-directory=Default")
    
    # Opciones de rendimiento y stealth
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # User-Agent moderno
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    service = Service(executable_path=CHROME_DRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)

def is_logged_in(driver):
    """Verifica si el login fue exitoso buscando elementos de la página principal"""
    try:
        # Busca elementos que solo existen cuando estás logueado
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.k-input-inner[placeholder*='Search Inventory']"))
        )
        return True
    except:
        return False

def main():
    driver = None
    try:
        # Iniciar navegador
        driver = setup_driver()
        print("✅ Navegador configurado correctamente")
        
        # Navegar directamente al login (por si acaso)
        driver.get(LOGIN_URL)
        print("🔐 Por favor inicia sesión manualmente...")
        
        # Esperar a que el usuario complete el login
        input("Presiona Enter después de iniciar sesión para continuar...")
        
        # Verificar login exitoso
        driver.get(TARGET_URL)
        if is_logged_in(driver):
            print("✅ Login exitoso - Sesión guardada en:", PROFILE_PATH)
            input("Puedes cerrar este navegador. Presiona Enter para salir...")
        else:
            print("❌ No se detectó login exitoso. Verifica:")
            print("- ¿Completaste el login correctamente?")
            print("- ¿Apareció algún error?")
            print("- ¿Te redirigió a otra página?")
            
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
    finally:
        if driver:
            driver.quit()
            print("🛑 Navegador cerrado")

if __name__ == "__main__":
    main()