import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def get_webdriver():
    """
    Retorna uma instância do navegador Chrome em modo headless.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Executar em modo headless
    return webdriver.Chrome(options=options)

def submit_form(browser, tipo_documento="", numero_documento="", conteudo_documento="", periodo_inicial="", periodo_final=""):
    """
    Preenche e envia o formulário de busca de normas.
    """
    try:
        # Preencher o formulário
        payload = {'numero': numero_documento, 'conteudo': conteudo_documento, 'dataInicioBusca': periodo_inicial, 'dataFimBusca': periodo_final}
        for key, value in payload.items():
            if value:
                element = browser.find_element(By.NAME, key)
                element.clear()
                element.send_keys(value)

        # Clicar no botão de pesquisa
        print("Clicando no botão 'Pesquisar'...")
        click_element(browser, browser.find_element(By.XPATH, '//button[@title="Buscar conteúdo no site"]'))

        time.sleep(5)

    except TimeoutException as e:
        print(f"Elemento não encontrado: {e}")

def click_element(browser, element):
    """
    Tenta clicar em um elemento, lidando com possíveis exceções.
    """
    try:
        element.click()
    except TimeoutException:
        # Se ocorrer uma exceção, tentamos usar a ação de movimento do mouse para clicar no elemento
        action = webdriver.ActionChains(browser)
        action.move_to_element(element).click().perform()

def search_normas():
    """
    Realiza a busca de normas de acordo com as informações fornecidas pelo usuário.
    """
    search_url = 'https://www.bcb.gov.br/estabilidadefinanceira/buscanormas'

    try:
        # Iniciar o navegador
        browser = get_webdriver()
        browser.get(search_url)

        # Preencher e enviar o formulário
        submit_form(browser, **get_search_inputs())

        # Após enviar o formulário de pesquisa, encontrar o elemento <div> com a classe "encontrados"
        encontrados_div = browser.find_element(By.CLASS_NAME, "encontrados")

        # Em seguida, encontrar todos os elementos <a> dentro desse <div>
        links = encontrados_div.find_elements(By.TAG_NAME, "a")

        # Agora você pode iterar sobre esses links e acessá-los conforme necessário
     
    except TimeoutException as e:
        print(f"Elemento não encontrado: {e}")

def get_search_inputs():
    """
    Coleta as informações necessárias para a pesquisa de normas.
    """
    tipo_documento_options = [
        "", "Ato de Diretor", "Ato Normativo Conjunto", "Ato do Presidente",
        "Carta Circular", "Circular", "Comunicado", "Comunicado Conjunto", "Decisão Conjunta",
        "Instrução Normativa BCB", "Instrução Normativa Conjunta", "Portaria Conjunta",
        "Resolução BCB", "Resolução CMN", "Resolução Conjunta", "Resolução Coremec"
    ]
    tipo_documento_choice = input('\n'.join([f'{i+1}. {opt}' for i, opt in enumerate(tipo_documento_options)]) + '\nEscolha: ')
    tipo_documento = tipo_documento_options[int(tipo_documento_choice) - 1] if tipo_documento_choice.isdigit() and 0 < int(tipo_documento_choice) <= len(tipo_documento_options) else ""

    numero_documento = input('Digite o número do documento (ou deixe em branco se não aplicável): ')
    conteudo_documento = input('Digite o conteúdo do documento (palavras-chave): ')

    periodo_inicial = input('Digite o período inicial (formato dd/mm/aaaa): ')
    while periodo_inicial and not is_valid_date(periodo_inicial):
        print('Período inicial inválido. Por favor, digite novamente.')
        periodo_inicial = input('Digite o período inicial (formato dd/mm/aaaa): ')

    periodo_final = input('Digite o período final (formato dd/mm/aaaa): ')
    while periodo_final and not is_valid_date(periodo_final):
        print('Período final inválido. Por favor, digite novamente.')
        periodo_final = input('Digite o período final (formato dd/mm/aaaa): ')

    return {
        'tipo_documento': tipo_documento,
        'numero_documento': numero_documento,
        'conteudo_documento': conteudo_documento,
        'periodo_inicial': periodo_inicial,
        'periodo_final': periodo_final
    }

def is_valid_date(date_str):
    """
    Verifica se a data está no formato dd/mm/aaaa.
    """
    return bool(re.match(r'\d{2}/\d{2}/\d{4}', date_str))

if __name__ == '__main__':
    # Executar a busca
    search_normas()
