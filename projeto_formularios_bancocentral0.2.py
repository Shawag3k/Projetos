import time
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_webdriver(browser_name):
    """
    Retorna uma instância do navegador especificado.
    """
    if browser_name.lower() == 'chrome':
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
        return driver
    elif browser_name.lower() == 'firefox':
        return webdriver.Firefox()
    else:
        raise ValueError('Unsupported browser. Please choose either "chrome" or "firefox".')

def is_valid_date(date_str):
    """
    Verifica se a data está no formato dd/mm/aaaa.
    """
    return bool(re.match(r'\d{2}/\d{2}/\d{4}', date_str))

def handle_cookies(browser):
    """
    Aceita os cookies clicando no botão 'Prosseguir'.
    """
    try:
        print("Clicando em 'Prosseguir' para aceitar cookies...")
        prosseguir_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Prosseguir")]'))
        )
        prosseguir_button.click()
        print("Cookies aceitos.")
    except TimeoutException:
        print("Botão 'Prosseguir' não encontrado ou não foi necessário.")

def search_normas(browser_name):
    """
    Realiza a busca de normas de acordo com as informações fornecidas pelo usuário.
    """
    search_url = 'https://www.bcb.gov.br/estabilidadefinanceira/buscanormas'

    try:
        # Solicitar tipo de navegador
        browser_name = input('Digite o nome do navegador (chrome ou firefox): ')

        # Solicitar outras informações do usuário
        tipo_documento = None
        numero_documento = None
        conteudo_documento = None
        periodo_inicial = None
        periodo_final = None

        # Coletar informações do usuário
        while True:
            tipo_documento_choice = input('Escolha o número correspondente ao tipo de documento desejado:\n'
                                          '1. Todos\n'
                                          '2. Ato de Diretor\n'
                                          '3. Ato Normativo Conjunto\n'
                                          '4. Ato do Presidente\n'
                                          '5. Carta Circular\n'
                                          '6. Circular\n'
                                          '7. Comunicado\n'
                                          '8. Comunicado Conjunto\n'
                                          '9. Decisão Conjunta\n'
                                          '10. Instrução Normativa BCB\n'
                                          '11. Instrução Normativa Conjunta\n'
                                          '12. Portaria Conjunta\n'
                                          '13. Resolução BCB\n'
                                          '14. Resolução CMN\n'
                                          '15. Resolução Conjunta\n'
                                          '16. Resolução Coremec\n'
                                          'Escolha: ')
            if tipo_documento_choice.isdigit():
                tipo_documento_choice = int(tipo_documento_choice)
                if 1 <= tipo_documento_choice <= 16:
                    tipo_documento_options = [
                        "Todos", "Ato de Diretor", "Ato Normativo Conjunto", "Ato do Presidente",
                        "Carta Circular", "Circular", "Comunicado", "Comunicado Conjunto", "Decisão Conjunta",
                        "Instrução Normativa BCB", "Instrução Normativa Conjunta", "Portaria Conjunta",
                        "Resolução BCB", "Resolução CMN", "Resolução Conjunta", "Resolução Coremec"
                    ]
                    tipo_documento = tipo_documento_options[tipo_documento_choice - 1]
                    break
            print("Escolha inválida. Por favor, digite o número correspondente à opção desejada.")

        numero_documento = input('Digite o número do documento (se aplicável): ')
        conteudo_documento = input('Digite o conteúdo do documento (palavras-chave): ')

        while True:
            periodo_inicial = input('Digite o período inicial (formato dd/mm/aaaa): ')
            if is_valid_date(periodo_inicial):
                break
            else:
                print('Período inicial inválido. Por favor, digite novamente.')

        while True:
            periodo_final = input('Digite o período final (formato dd/mm/aaaa): ')
            if is_valid_date(periodo_final):
                break
            else:
                print('Período final inválido. Por favor, digite novamente.')

        # Iniciar o navegador
        browser = get_webdriver(browser_name)
        browser.get(search_url)

        # Lidar com cookies
        handle_cookies(browser)

        # Tratar elemento tipoDocumento
        select_tipo_documento = None
        try:
            select_tipo_documento = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, 'tipoDocumento'))
            )
            select_tipo_documento = Select(select_tipo_documento)
        except TimeoutException:
            print("Elemento tipoDocumento não encontrado.")

        if select_tipo_documento:
            select_tipo_documento.select_by_visible_text(tipo_documento)

            # Preencher o formulário
            payload = {
                'numDocumento': numero_documento,
                'conteudoDocumento': conteudo_documento,
                'periodoInicial': periodo_inicial,
                'periodoFinal': periodo_final
            }
            for key, value in payload.items():
                element = WebDriverWait(browser, 10).until(
                    EC.visibility_of_element_located((By.NAME, key))
                )
                element.send_keys(value)

            # Enviar formulário
            print("Enviando formulário...")
            element_submit = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
            )
            element_submit.click()

            time.sleep(5)
            browser.quit()
    except TimeoutException as e:
        print(f"Elemento não encontrado: {e}")
        browser.quit()

if __name__ == '__main__':
    # Executar a busca e baixar as normas
    search_normas(None)



























