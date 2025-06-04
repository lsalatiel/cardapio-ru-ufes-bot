from bs4 import BeautifulSoup
from urllib.request import urlopen

def process_menu_string(text):
    if text.startswith('['):
        text = text[1:]
    
    text = text.replace(', Salada', ' Salada')
    text = text.replace(',Salada', ' Salada')
    
    text = text.replace('Salada', '\n\nSalada')
    
    words_to_add_newline = [
        'Prato Principal',
        'Opção',
        'Acompanhamento',
        'Guarnição',
        'Sobremesa'
    ]
    
    for word in words_to_add_newline:
        text = text.replace(word, '\n' + word)

    words_to_add_bold = words_to_add_newline + ['Salada']

    for word in words_to_add_bold:
        text = text.replace(word, '*' + word + '*')
    
    lines_to_remove = [
        '* Cardápio sujeito a alterações.',
        '** Informamos que todas as nossas preparações podem conter traços de glúten e leite (contaminação cruzada).'
    ]
    
    for line in lines_to_remove:
        text = text.replace(line, '')
    
    text = text.replace(', Jantar', 'Jantar')
    text = text.replace(',Jantar', 'Jantar')
    text = text.replace('\n\n\nJantar', '\nJantar')
    
    text = text.replace(', , ]', '')
    
    return text.strip()

def get_menu():
    url = "https://ru.ufes.br/cardapio"
    html = urlopen(url).read()

    soup = BeautifulSoup(html, "html.parser")

    content_html = soup.find_all(class_ = "field-content")
    content_soup = BeautifulSoup(str(content_html), "html.parser")

    content = content_soup.get_text()

    if content.startswith('['):
        return "Menu still not available for today..."

    menu = process_menu_string(content)

    return menu
