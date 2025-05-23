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
datos = []  # Lista para almacenar datos scrapeados
frames =[] # Lista de frames para ir cambiando de paginas
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
    """Extrae el nombre del cliente desde el elemento deal"""
    nombre_cliente = deal_element.find_element(By.XPATH, ".//div[@class='row'][2]//div[@class='col-4 r-item']/span").text.strip()
    print(f"Nombre del cliente: {nombre_cliente}")
    datos.append(("Name", nombre_cliente))
    return nombre_cliente


def click_nombre_cliente(driver, nombre_cliente):
    wait = WebDriverWait(driver, 15)
    # Normalizo nombre para evitar doble espacio, mayúsculas, etc
    nombre_normalizado = " ".join(nombre_cliente.upper().split())
    
    xpath = (
        f"//div[contains(@class, 'header-customer-name__label') and "
        f"contains(normalize-space(@title), '{nombre_normalizado}')]//a"
    )

    elemento = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    elemento.click()
    print(f"✅ Hiciste clic en el nombre del cliente: {nombre_cliente}")

def main():
    driver = None
   

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
        nommbre_cliente = obtener_nombre_loan(deal_element)
        deal_element.click()

        # Cambiar a iframe del pop-up
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dc-iframe-dialog"))
        )
        driver.switch_to.frame(iframe)

        containers = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.mb-2.d-flex.align-items-center"))
        )

        for container in containers:
            try:
                label_element = container.find_element(By.CSS_SELECTOR, ".mr-auto.label, span.mr-auto.label")
                label = label_element.text.strip().lower().replace(" ", "_")

                # Buscar input con aria-valuenow directamente, incluso si está deshabilitado
                try:
                    input_element = container.find_element(By.CSS_SELECTOR, "input[aria-valuenow]")
                    valor_str = input_element.get_attribute("aria-valuenow")
                except Exception as e_input:
                    print(f"⚠️ No se encontró input válido para '{label}': {e_input}")
                    valor_str = None

                if valor_str:
                    try:
                        valor = float(valor_str)
                        if valor.is_integer():
                            valor = int(valor)
                    except ValueError:
                        print(f"⚠️ No se pudo convertir el valor de '{label}': {valor_str}")
                        valor = None
                else:
                    valor = None

                datos.append((label, valor))

            except Exception as e:
                print(f"❌ No se pudo extraer información de un campo: {e}")

        #Agarro el amount financed por separado
        amount_financed_element = driver.find_element(
        By.XPATH,
        "//div[contains(text(), 'Amount Financed')]/following-sibling::div"
        )

        amount_text = amount_financed_element.text.strip()
        print("Amount Financed:", amount_text)
        datos.append(("Amount Financed:", amount_text))

        
        #Abro el link al nombre del cliente
        click_nombre_cliente(driver, nommbre_cliente)
        iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.k-window iframe")))
        # Cambiar al iframe
        driver.switch_to.frame(iframe)
        print("Estas en la pestania de Edit Buyer")
        credit_app_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[.//span[text()='Credit App']]")))
        credit_app_tab.click()

        containers_dob = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "kendo-datepicker[formcontrolname='dateOfBirth'] input.k-input-inner"))
        )
        dob_input = driver.find_element(By.CSS_SELECTOR, "kendo-datepicker[formcontrolname='dateOfBirth'] input.k-input-inner")
        dob = dob_input.get_attribute("value")
        datos.append(("Date of Birth", dob))

        # SSN
        # Ubicar el campo SSN (input oculto dentro del kendo-textbox)
        visible_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "kendo-textbox[formcontrolname='ssn'] input.k-input-inner"))
            )

        # Hacer click para revelar el SSN completo
        visible_input.click()

        # Ahora obtener el input oculto que tiene el valor completo
        hidden_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "dc-ui-shared-masked-input[formcontrolname='ssn'] input.masked-input-textbox"))
        )

        # Obtener el valor completo del SSN
        ssn_value = hidden_input.get_attribute("value")
        print("SSN completo:", ssn_value)

        # Agregar a la lista data
        datos.append(("SSN", ssn_value))

        # Email
        email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "kendo-textbox[formcontrolname='email'] input.k-input-inner"))
        )

        # Obtener el valor directamente
        email_value = email_input.get_attribute("value")
        print("Email:", email_value)

        # Agregar a la lista de datos
        datos.append(("Email", email_value))

        # Cell Phone
        phone_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.k-input-inner[aria-placeholder='(999) 000-0000']"))
        )

        # Obtener el valor
        phone_value = phone_input.get_attribute("value")
        print("Phone:", phone_value)

        # Agregar a la lista
        datos.append(("Phone", phone_value))

        #Obtener adress
        address_input = driver.find_element(By.XPATH, '//input[@formcontrolname="FullAddress"]')

        # Obtener el valor de la dirección
        address = address_input.get_attribute('value')

        print("Dirección actual:", address)
        datos.append(("Adress", address))
        print("Datos extraídos:")
        print(datos)
        time.sleep(500)
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
