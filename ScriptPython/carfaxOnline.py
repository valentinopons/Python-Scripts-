from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import time


options = Options()
# define the proxy server
PROXY = "47.237.107.41:8080"


# add the proxy as argument
options.add_argument(f"--proxy-server={PROXY}")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
options.add_argument(r"user-data-dir=C:\Users\ValentinoPons\selenium-profile")
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)


service = Service(r"C:\Users\ValentinoPons\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
try:
    driver.get("https://www.carfaxonline.com/")
    wait = WebDriverWait(driver, 60)

    campo_vin = wait.until(EC.element_to_be_clickable((By.ID, "vin")))
    print("Campo VIN disponible. Escribiendo VIN...")

    for char in "1HGCM82633A123456":
        campo_vin.send_keys(char)
        time.sleep(0.1)

    def boton_habilitado(driver):
        try:
            boton = driver.find_element(By.ID, "run_vhr_button")
            return boton.is_enabled()
        except:
            return False

    wait.until(boton_habilitado)
    time.sleep(1.5)

    boton = driver.find_element(By.ID, "run_vhr_button")
    boton.click()

    div = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "carfax-value-row")))
    p_tags = div.find_elements(By.TAG_NAME, "p")
    precio = p_tags[0].text.replace("$", "").replace(",", "").strip()
    print("Precio:", precio)

    input("Presiona Enter para salir...")

except Exception as e:
    print("No se pudo ejecutar el script:", e)

finally:
    driver.quit()
