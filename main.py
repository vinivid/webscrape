import csv
import _csv
import requests
from bs4 import BeautifulSoup

cardinali_domain = 'https://www.cardinali.com.br'

response = requests.get(f'{cardinali_domain}/pesquisa-de-imoveis/?locacao_venda=L&id_cidade[]=190&finalidade=residencial&dormitorio=&garagem=&vmi=&vma=1.300%2C00&ordem=1&&pag=3')
soup = BeautifulSoup(response.text, 'html.parser')

#Seprating the house blocks, not sure if the return of find all
#really is a list of BeautifulSoup
all_blocks : list[BeautifulSoup] = soup.find_all('div', class_="muda_card1 ms-lg-0 col-12 col-md-12 col-lg-6 col-xl-4 mt-4 d-flex align-self-stretch justify-content-center")

"""
Process the cards from cardinali page, writing its contents to a
csv file.

    For every card in the page we check the house name. 
If the name indicates that it is a house we continue 
processing the house info, else, we go to the next card.
    From the house info we start writing the data of the house,     
to a csv.
"""
def card_process(csv_file : '_csv._writer') -> None:
    for card in all_blocks:
        #The house name is always in the singular h2 of the card
        house_name = card.find('h2').string.lstrip().rstrip()

        #The path that contains the house info is in the links of the carrousell
        house_info_path = card.find('a')['href']
        house_info_soup = BeautifulSoup(requests.get(f'{cardinali_domain}/{house_info_path}').text, 'html.parser')

        #The rent value is located within a block of values, it is always contained in strong
        house_rent_block = house_info_soup.find(class_="valores_imovel p-3")
        house_rent_value = house_rent_block.find('strong').string

        csv_file.writerow([house_name, house_rent_value])


with open('ok.tst', 'w') as c:
    jik = csv.writer(c, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    card_process(jik)