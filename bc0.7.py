import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from fpdf import FPDF
import os

def get_webdriver():    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Executar em modo headless
    return webdriver.Chrome(options=options)

def click_element(browser, element):
    try:
        element.click()
    except TimeoutException:
        action = webdriver.ActionChains(browser)
        action.move_to_element(element).click().perform()

def submit_form(browser, tipo_documento_option, numero_documento, conteudo_documento):
    print("Clicando no botão 'Pesquisar'...")
    # Clicar no elemento do menu suspenso para exibir as opções
    tipo_documento_dropdown = browser.find_element(By.ID, "tipoDocumento")
    browser.execute_script("arguments[0].click();", tipo_documento_dropdown)
    time.sleep(1)  # Aguardar um curto período para que as opções sejam carregadas

    # Localizar a opção desejada com base no texto correspondente
    xpath = f"//option[text()='{tipo_documento_option}']"
    tipo_documento_element = browser.find_element(By.XPATH, xpath)

    # Clicar na opção desejada para selecioná-la
    tipo_documento_element.click()

    # Preencher o campo "Número do Documento"
    numero_documento_input = browser.find_element(By.ID, "numero")
    numero_documento_input.clear()
    numero_documento_input.send_keys(numero_documento)

    # Preencher o campo "Conteúdo do Documento"
    conteudo_documento_input = browser.find_element(By.ID, "conteudo")
    conteudo_documento_input.clear()
    conteudo_documento_input.send_keys(conteudo_documento)

    # Clicar no botão de pesquisa
    search_button = browser.find_element(By.XPATH, '//button[@title="Buscar conteúdo no site"]')
    search_button.click()

def search_normas():
    search_url = 'https://www.bcb.gov.br/estabilidadefinanceira/buscanormas'

    try:
        # Iniciar o navegador
        browser = get_webdriver()
        browser.get(search_url)
        # Preencher e enviar o formulário
        inputs = get_search_inputs()
        submit_form(browser, inputs['tipo_documento_option'], inputs['numero_documento'], inputs['conteudo_documento'])

        # Esperar até que os links sejam encontrados na página
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "encontrados"))
        )

        # Coletar os links dos resultados da pesquisa
        links = browser.find_elements(By.XPATH, '//div[@class="encontrados"]//a')
        links_urls = [link.get_attribute("href") for link in links]

        if links_urls:
            for link_url in links_urls:
                browser.get(link_url)
                # Esperar até que a página seja carregada completamente
                time.sleep(1)  # Aguarda 1 segundo para garantir que a página seja carregada
                # Verificar se o título e os parágrafos estão presentes
                try:
                    WebDriverWait(browser, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "h2"))
                    )
                    title = browser.find_element(By.TAG_NAME, "h2").text
                    paragraphs = browser.find_elements(By.TAG_NAME, "p")
                    # Adicionamos agora os elementos <pre> à lista de parágrafos
                    pre_elements = browser.find_elements(By.TAG_NAME, "pre")
                    paragraphs.extend(pre_elements)
                    # Convertendo todos os elementos para strings
                    texts = [text.text if isinstance(text, WebElement) else text for text in paragraphs]
                    # Gerar e salvar o PDF
                    generate_pdf(title, texts)
                    print(f"PDF gerado para o link: {link_url}")
                except TimeoutException:
                    print(f"Link: {link_url} - Revogado")

        else:
            print("Nenhum link encontrado nos resultados da pesquisa.")

    except TimeoutException as e:
        print(f"Elemento não encontrado: {e}")


def generate_pdf(title, texts):
    # Criar um objeto PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Adicionar o título ao PDF
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    # Adicionar os textos ao PDF
    for text in texts:
        # Converter o texto extraído para string antes de usar o método replace
        text_str = text.text if isinstance(text, WebElement) else text
        pdf.multi_cell(0, 10, txt=text_str.replace('\n', ''))  # Remover quebras de linha
    # Obter o diretório onde o programa está sendo executado
    current_directory = os.getcwd()
    # Criar uma pasta 'pdfs' dentro do diretório atual, se ainda não existir
    pdfs_directory = os.path.join(current_directory, 'pdfs')
    if not os.path.exists(pdfs_directory):
        os.makedirs(pdfs_directory)
    # Limpar o título para torná-lo compatível com o sistema de arquivos
    cleaned_title = "".join(x for x in title if x.isalnum() or x in [' ', '.', '_', '-'])
    # Adicionar o PDF com o título limpo como nome do arquivo na pasta 'pdfs'
    pdf_file_name = os.path.join(pdfs_directory, f"{cleaned_title}.pdf")

    print(f"PDF gerado: {pdf_file_name}")

    # Salvar o PDF apenas se houver textos a serem adicionados
    if texts:
        pdf.output(pdf_file_name)  # Salvar o PDF
        print(f"Caminho do arquivo PDF: {pdf_file_name}")


def get_search_inputs():
    
    print("Digite o numero correspondente ao tipo de documento desejado:") 
    tipo_documento_options = ["Todos", "Ato de Diretor", "Ato Normativo Conjunto", "Ato do Presidente",
        "Carta Circular", "Circular", "Comunicado", "Comunicado Conjunto", "Decisão Conjunta",
        "Instrução Normativa BCB", "Instrução Normativa Conjunta", "Portaria Conjunta",
        "Resolução BCB", "Resolução CMN", "Resolução Conjunta", "Resolução Coremec"
    ]
    tipo_documento_choice = int(input('\n'.join([f'{i+1}. {opt}' for i, opt in enumerate(tipo_documento_options)]) + '\nEscolha: '))
    tipo_documento_option = tipo_documento_options[tipo_documento_choice - 1] if 0 < tipo_documento_choice <= len(tipo_documento_options) else ""

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
        'tipo_documento_option': tipo_documento_option,
        'numero_documento': numero_documento,
        'conteudo_documento': conteudo_documento,
        'periodo_inicial': periodo_inicial,
        'periodo_final': periodo_final
    }

def is_valid_date(date_str):
    
    #Verifica se a data está no formato dd/mm/aaaa.
    
    return bool(re.match(r'\d{2}/\d{2}/\d{4}', date_str))

if __name__ == '__main__':
    search_normas()
