import os
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select  # Adicionando o import para Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_webdriver(browser_name):
    if browser_name.lower() == 'chrome':
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")  # Desabilita notificações
        options.add_argument("--disable-popup-blocking")  # Desabilita bloqueio de pop-ups
        options.add_argument("--disable-extensions")  # Desabilita extensões do navegador
        options.add_argument("--disable-infobars")  # Desabilita barra de informações
        options.add_argument("--disable-dev-shm-usage")  # Desabilita o uso compartilhado de memória /tmp
        options.add_argument("--no-sandbox")  # Usa sandbox
        options.add_argument("--start-maximized")  # Inicia maximizado
        driver = webdriver.Chrome(options=options)
        return driver
    elif browser_name.lower() == 'firefox':
        return webdriver.Firefox()
    else:
        raise ValueError('Unsupported browser. Please choose either "chrome" or "firefox".')

def download_pdf(url, save_to):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_to, 'wb') as f:
            f.write(response.content)
            print(f'PDF baixado e salvo em: {save_to}')
    else:
        print(f'Erro ao baixar {url}')

def is_valid_date(date_str):
    # Verifica se a data está no formato dd/mm/aaaa
    return bool(re.match(r'\d{2}/\d{2}/\d{4}', date_str))

def search_normas(tipo_documento, numero_documento, conteudo_documento, periodo_inicial, periodo_final, browser_name):
    search_url = 'https://www.bcb.gov.br/estabilidadefinanceira/buscanormas'
    payload = {
        'tipoDocumento': tipo_documento,
        'numDocumento': numero_documento,
        'conteudoDocumento': conteudo_documento,
        'periodoInicial': periodo_inicial,
        'periodoFinal': periodo_final
    }
    print("Payload:", payload)

    # Inicializa o navegador
    browser = get_webdriver(browser_name)
    browser.get(search_url)

    try:
        # Aceitar cookies clicando em "prosseguir"
        print("Clicando em 'Prosseguir' para aceitar cookies...")
        prosseguir_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Prosseguir")]'))
        )
        prosseguir_button.click()
        print("Cookies aceitos.")
    except TimeoutException:
        print("Botão 'Prosseguir' não encontrado ou não foi necessário.")

    try:
        # Encontrar o seletor de tipo de documento
        element_tipo_documento = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'tipoDocumento'))
        )

        # Criar um objeto Select
        select = Select(element_tipo_documento)

        # Verificar se a opção exata fornecida pelo usuário está disponível
        options = [option.text.strip() for option in select.options]
        if tipo_documento not in options:
            raise NoSuchElementException(f'Tipo de documento "{tipo_documento}" não encontrado nas opções.')

        # Selecionar o tipo de documento desejado pelo usuário
        select.select_by_visible_text(tipo_documento)

        # Preenche o restante do formulário com verificações de validação
        for key, value in payload.items():
            element = WebDriverWait(browser, 10).until(
                EC.visibility_of_element_located((By.NAME, key))
            )
            if key == 'periodoInicial' or key == 'periodoFinal':
                if not is_valid_date(value):
                    print(f"Data inválida: {value}")
                    browser.quit()
                    return
            element.send_keys(value)

        # Enviar formulário
        print("Enviando formulário...")
        element_submit = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
        )
        element_submit.click()
    except TimeoutException as e:
        print(f"Elemento não encontrado: {e}")

    # Lógica para baixar os PDFs...
    # Aqui você pode implementar o código para baixar os PDFs conforme necessário

    # Fechar o navegador após a conclusão
    time.sleep(5)  # Aguarda 5 segundos para visualizar a página
    browser.quit()

if __name__ == '__main__':
    # Solicitar ao usuário o tipo de navegador
    browser_name = input('Digite o nome do navegador (chrome ou firefox): ')

    # Solicitar ao usuário o tipo de documento
    tipo_documento = input('Digite o tipo de documento (Comunicado, Resolucao, Circular, etc.): ')

    # Solicitar ao usuário o número do documento
    numero_documento = input('Digite o número do documento (se aplicável): ')

    # Solicitar ao usuário o conteúdo do documento (palavras-chave)
    conteudo_documento = input('Digite o conteúdo do documento (palavras-chave): ')

    # Validar e solicitar ao usuário o período inicial até que seja válida
    while True:
        periodo_inicial = input('Digite o período inicial (formato dd/mm/aaaa): ')
        if is_valid_date(periodo_inicial):
            break
        else:
            print('Período inicial inválido. Por favor, digite novamente.')

    # Validar e solicitar ao usuário o período final até que seja válida
    while True:
        periodo_final = input('Digite o período final (formato dd/mm/aaaa): ')
        if is_valid_date(periodo_final):
            break
        else:
            print('Período final inválido. Por favor, digite novamente.')

    # Executar a busca e baixar as normas
    search_normas(tipo_documento, numero_documento, conteudo_documento, periodo_inicial, periodo_final, browser_name)


























