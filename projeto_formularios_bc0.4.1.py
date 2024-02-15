import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from fpdf import FPDF

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
        return webdriver.Chrome(options=options)
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

def submit_form(browser, tipo_documento, numero_documento="", conteudo_documento="", periodo_inicial="", periodo_final=""):
    """
    Preenche e envia o formulário de busca de normas.
    """
    try:
        # Lidar com tipo de documento
        select_tipo_documento = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, 'tipoDocumento'))
        )
        select_tipo_documento = Select(select_tipo_documento)
        select_tipo_documento.select_by_visible_text(tipo_documento)

        # Preencher o formulário
        payload = {
            'numero': numero_documento,
            'conteudo': conteudo_documento,
            'dataInicioBusca': periodo_inicial,
            'dataFimBusca': periodo_final
        }
        for key, value in payload.items():
            element = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.NAME, key))
            )
            element.clear()
            if value:
                element.send_keys(value)  # Só preenche se houver valor

        # Clicar no botão de pesquisa
        print("Clicando no botão 'Pesquisar'...")
        search_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@title="Buscar conteúdo no site"]'))
        )
        click_element(browser, search_button)

        time.sleep(5)

        # Após o envio do formulário, procurar e acessar todas as normas encontradas
        access_all_normas(browser)

    except TimeoutException as e:
        print(f"Elemento não encontrado: {e}")

def click_element(browser, element):
    """
    Tenta clicar em um elemento, lidando com possíveis exceções.
    """
    try:
        element.click()
    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
        # Se ocorrer uma exceção, tentamos usar a ação de movimento do mouse para clicar no elemento
        action = webdriver.ActionChains(browser)
        action.move_to_element(element).click().perform()

def access_all_normas(browser):
    """
    Acessa todas as normas encontradas após o envio do formulário de pesquisa.
    """
    try:
        # Encontrar links para as normas
        norma_links = browser.find_elements(By.XPATH, '//a[contains(@href, "/estabilidadefinanceira/exibenormativo")]')
        for link in norma_links:
            norma_url = link.get_attribute('href')
            print(f"Acessando norma: {norma_url}")
            browser.execute_script("window.open('" + norma_url + "');")
            browser.switch_to.window(browser.window_handles[-1])

            # Copiar o título e o conteúdo da norma
            title = browser.find_element(By.XPATH, '//h2[@class="titulo-pagina cormorant"]').text.strip()
            content_elements = browser.find_elements(By.XPATH, '//div[@class="conteudo"]//p')
            content = '\n'.join([element.text for element in content_elements])

            # Salvar como PDF
            save_as_pdf(title, content)

            # Fechar a aba atual e voltar para a anterior
            browser.close()
            browser.switch_to.window(browser.window_handles[0])

    except Exception as e:
        print(f"Erro ao acessar normas: {e}")

def save_as_pdf(title, content):
    """
    Salva o título e o conteúdo como PDF.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    pdf_file_name = title.replace('/', '_').replace(':', '-') + ".pdf"
    pdf.output(pdf_file_name)
    print(f"PDF salvo como {pdf_file_name}")

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

        # Preencher e enviar o formulário
        submit_form(browser, tipo_documento, numero_documento, conteudo_documento, periodo_inicial, periodo_final)

        browser.quit()

    except TimeoutException as e:
        print(f"Elemento não encontrado: {e}")

if __name__ == '__main__':
    # Executar a busca e baixar as normas
    search_normas(None)

