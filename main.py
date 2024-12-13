import requests
from bs4 import BeautifulSoup

response = requests.get('https://www.cardinali.com.br/pesquisa-de-imoveis/?locacao_venda=L&id_cidade[]=190&finalidade=residencial&dormitorio=&garagem=&vmi=&vma=1.300%2C00&ordem=1&&pag=3')
soup = BeautifulSoup(response.text, 'html.parser')

#Separa todas as caixas que representam as casas 
all_blocks : list[BeautifulSoup] = soup.find_all('div', class_="muda_card1 ms-lg-0 col-12 col-md-12 col-lg-6 col-xl-4 mt-4 d-flex align-self-stretch justify-content-center")

def card_process():
    for block in all_blocks:
        print(block.find('h2').string.lstrip().rstrip())

        ok = block.find(class_="card-valores")

        for str in ok.stripped_strings:
            print(str)

card_process()