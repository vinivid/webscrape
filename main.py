import csv
import _csv
from datetime import timedelta

import osmnx as ox
import networkx as nx
import requests
from bs4 import BeautifulSoup

CARDINALI_DOMAIN = 'https://www.cardinali.com.br'

graph_sao_carlos = ox.graph_from_place("São Carlos, São Paulo, Brazil", network_type='walk', simplify=False)
nx.set_edge_attributes(graph_sao_carlos, 5.1, 'speed_kph')
graph_sao_carlos = ox.add_edge_travel_times(graph_sao_carlos)

#destino = ox.geocode("Avenida Trabalhador São-Carlense")
#origin = ox.geocode("Vila Celina, Monjolinho, São Carlos, Região Imediata de São Carlos, Região Geográfica Intermediária de Araraquara, São Paulo, Southeast Region, Brazil")

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

def card_process(page_contents, csv_file : '_csv._writer') -> None:
    """
        Process the cards from cardinali page, writing its contents to a
    csv file.

        For every card in the page we check the house name. 
    If the name indicates that it is a house we continue 
    processing the house info, else, we go to the next card.
        From the house info we start writing the data of the house,     
    to a csv.
    """

    for card in page_contents:
        #The house name is always in the singular h2 of the card
        house_name = card.find('h2').string.lstrip().rstrip()

        low_hs_name = house_name.lower()
        if 'comercial' in low_hs_name or 'terreno' in low_hs_name:
            continue

        #The path that contains the house info is in the links of the carrousell
        house_info_path = card.find('a')['href']
        house_info_soup = BeautifulSoup(requests.get(f'{CARDINALI_DOMAIN}/{house_info_path}').text, 'html.parser')

        #The rent value is located within a block of values, it is always contained in strong
        house_rent_block = house_info_soup.find(class_="valores_imovel p-3")
        house_rent_value = house_rent_block.find('strong').string

        csv_file.writerow([house_name, house_rent_value])


def scrape_cardinali() -> None:
    response = requests.get(f'{CARDINALI_DOMAIN}/pesquisa-de-imoveis/?locacao_venda=L&id_cidade[]=190&finalidade=residencial&dormitorio=&garagem=&vmi=&vma=1.300%2C00&ordem=1&&pag=3')
    soup = BeautifulSoup(response.text, 'html.parser')

    #Seprating the house blocks, not sure if the return of find all
    #really is a list of BeautifulSoup
    all_blocks : list[BeautifulSoup] = soup.find_all('div', class_="muda_card1 ms-lg-0 col-12 col-md-12 col-lg-6 col-xl-4 mt-4 d-flex align-self-stretch justify-content-center")

    with open('ok.tst', 'w', newline='') as c:
        jik = csv.writer(c, delimiter=' ')

        card_process(all_blocks, jik)