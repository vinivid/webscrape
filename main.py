import csv
#Used only for type hints
import _csv
import os

import osmnx as ox
import networkx as nx
import requests
from bs4 import BeautifulSoup

CARDINALI_DOMAIN = 'https://www.cardinali.com.br'
USP_MAT_COORDINATES = (-22.0062, -47.89518)

if os.path.isfile('./scgraph/sc.graphml'):
    print('ok')

GRAPH_SAO_CARLOS = ox.graph_from_place("São Carlos, São Paulo, Brazil", network_type='walk', simplify=False)
nx.set_edge_attributes(GRAPH_SAO_CARLOS, 5.1, 'speed_kph')
GRAPH_SAO_CARLOS = ox.add_edge_travel_times(GRAPH_SAO_CARLOS)

#origin_node = ox.nearest_nodes(graph_sao_carlos, X=origin[1], Y=origin[0])
#destination_node = ox.nearest_nodes(graph_sao_carlos, X=destino[1], Y=destino[0])

#travel_time_in_seconds = nx.shortest_path_length(graph_sao_carlos, origin_node, destination_node, weight='travel_time')
#print("travel time in seconds", travel_time_in_seconds)
# Get the distance in meters
#distance_in_meters = nx.shortest_path_length(graph_sao_carlos, origin_node, destination_node, weight='length')
#print("distance in meters", distance_in_meters)
# Distance in kilometers
#distance_in_kilometers = distance_in_meters / 1000
#print("distance in kilometers", distance_in_kilometers)

def card_process(card : BeautifulSoup, csv_file : 'csv._writer') -> None:
    """
        Process the cards from cardinali page, writing its contents to a
    csv file.

        For every card in the page we check the house name. 
    If the name indicates that it is a house we continue 
    processing the house info, else, we go to the next card.
        From the house info we start writing the data of the house,     
    to a csv.
    """

    #The house name is always in the singular h2 of the card
    house_name = card.find('h2').string.lstrip().rstrip()

    low_hs_name = house_name.lower()
    if 'comercial' in low_hs_name or 'terreno' in low_hs_name:
        return

    house_name.replace(',','.')

    #The path that contains the house info is in the links of the carrousell
    house_info_path = card.find('a')['href']
    house_info_soup = BeautifulSoup(requests.get(f'{CARDINALI_DOMAIN}/{house_info_path}').text, 'html.parser')

    #The rent value is located within a block of values, it is always contained in strong
    house_rent_block = house_info_soup.find(class_="valores_imovel p-3")
    house_rent_value = house_rent_block.find('strong').string.replace(',', '.')

    csv_file.writerow([house_name, house_rent_value])


def scrape_cardinali() -> None:
    pag = 1
    cur_card = 1
    vmin = 200
    vmax = 1500

    print(f'{'\033[0;31m'}Scraping Cardinali{'\033[0m'}')

    with open('cardinali.csv', 'w', newline='') as cardinali_csv:
        ccsv = csv.writer(cardinali_csv, delimiter=',')

        while True:
            print(f'{'\033[0;31m'}Currently on page {pag}{'\033[0m'}')
            response = requests.get(f'{CARDINALI_DOMAIN}/pesquisa-de-imoveis/?busca_free=&locacao_venda=L&id_cidade[]=190&dormitorio=&garagem=&finalidade=residencial&a_min=&a_max=&vmi={vmin}&vma={vmax}&ordem=1&&pag={pag}')
            houses_soup = BeautifulSoup(response.text, 'html.parser')

            #Separates all of the cards of the main page
            card_blocks : list[BeautifulSoup] = houses_soup.find_all('div', class_="muda_card1 ms-lg-0 col-12 col-md-12 col-lg-6 col-xl-4 mt-4 d-flex align-self-stretch justify-content-center")

            for card in card_blocks:
                print(f'Scraping page:{pag} Card: {cur_card}')
                card_process(card, ccsv)
                cur_card += 1

            pagination = houses_soup.find(class_='pagination')

            #When it is the last page the button to go to the next page receives the class disabled
            #Will not work if there is less than one page
            if pag != 1 and pagination.find(class_='disabled') != None:
                break

            pag += 1

scrape_cardinali()