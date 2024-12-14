import csv
#Used only for type hints
import _csv
import os
import time

import osmnx as ox
import networkx as nx
import requests
from bs4 import BeautifulSoup

CARDINALI_DOMAIN = 'https://www.cardinali.com.br'
USP_COORDINATES = (-22.0062, -47.89518)
GRAPH_SAO_CARLOS = None

if os.path.isfile('./scgraph/sc.graphml'):
    print('Graph of the city already created, loading it.')
    try:
        GRAPH_SAO_CARLOS = ox.load_graphml('./scgraph/sc.graphml')
    except IOError as error:
        raise SystemExit(error)
else:
    print('Graph has not been created, creating it.')
    GRAPH_SAO_CARLOS = ox.graph_from_place("São Carlos, São Paulo, Brazil", network_type='walk')
    nx.set_edge_attributes(GRAPH_SAO_CARLOS, 4.6, 'speed_kph')
    GRAPH_SAO_CARLOS = ox.distance.add_edge_lengths(GRAPH_SAO_CARLOS)
    GRAPH_SAO_CARLOS = ox.add_edge_travel_times(GRAPH_SAO_CARLOS)

    try:
        ox.save_graphml(GRAPH_SAO_CARLOS, "./scgraph/sc.graphml")
    except IOError as error:
        raise SystemExit(error)
    
USP_MAT_NODE = ox.nearest_nodes(GRAPH_SAO_CARLOS, X=USP_COORDINATES[1], Y=USP_COORDINATES[0])

def card_process(card : BeautifulSoup, csv_file : '_csv._writer') -> None:
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
    print('\t\033[0;33mGetting location info\033[0m')
    house_name = card.find('h2').string.lstrip().rstrip()

    low_hs_name = house_name.lower()
    if 'comercial' in low_hs_name or 'terreno' in low_hs_name:
        print('\tNot Residential')
        return

    house_name.replace(',','.')

    #The path that contains the house info is in the links of the carrousell
    house_info_path = card.find('a')['href']

    request = None
    try:
        request = requests.get(f'{CARDINALI_DOMAIN}/{house_info_path}')
    except requests.exceptions.RequestException as error:
        raise SystemExit(error)

    house_info_soup = BeautifulSoup(request.text, 'html.parser')

    #The rent value is located within a block of values, it is always contained in strong
    house_rent_block = house_info_soup.find(class_="valores_imovel p-3")
    house_rent_value = house_rent_block.find('strong').string.replace(',', '.')

    print('\t\033[0;33mCalculating distance and time to USP\033[0m')
    #The location of the house is always in that class, not sure if there are ever any typos in it
    #that would make it so this way does not work
    location : str = card.find(class_="card-bairro-cidade my-1 pt-1").contents[1].string
    location = location[:location.find('-') - 1]

    try:
        house_location = ox.geocode(f'{location}, São Carlos, Brazil')
    except ox._errors.InsufficientResponseError as error:
        print(f'\t\033[0;31mLocation \033[4m{location}\033[0m \033[0;31mnot on Nominatim\033[0m')
        print('\tWaiting 1.5 sec for the Nominatim api')
        time.sleep(1.5)
        return

    tma = time.time()
    house_node = ox.nearest_nodes(GRAPH_SAO_CARLOS, X=house_location[1], Y=house_location[0])
    travel_time = nx.shortest_path_length(GRAPH_SAO_CARLOS, house_node, USP_MAT_NODE, weight='travel_time') / 60
    shortest_distance = nx.shortest_path_length(GRAPH_SAO_CARLOS, house_node, USP_MAT_NODE, weight='length')
    tmb = time.time()

    if tmb - tma < 1.1:
        print('\tWaiting 1.5 sec for the Nominatim api')
        time.sleep(1.5)

    csv_file.writerow([house_name, house_rent_value, round(shortest_distance, 1), round(travel_time, 1),f'{CARDINALI_DOMAIN}/{house_info_path}'])

def scrape_cardinali() -> None:
    pag = 1
    cur_card = 1
    vmin = 200
    vmax = 1500

    print(f'\033[0;32mScraping Cardinali\033[0m')

    with open('cardinali.csv', 'w', newline='') as cardinali_csv:
        ccsv = csv.writer(cardinali_csv, delimiter=',')

        ccsv.writerow(['Nome da locação', 'Valor do aluguel', 'Menor distância', 'Tempo andando', 'Link para a pagina'])

        start_of_scrape = time.time()

        while True:
            print(f'\033[0;36mCurrently on page {pag}\033[0m')
            response = None
            
            try:
                response = requests.get(f'{CARDINALI_DOMAIN}/pesquisa-de-imoveis/?busca_free=&locacao_venda=L&id_cidade[]=190&dormitorio=&garagem=&finalidade=residencial&a_min=&a_max=&vmi={vmin}&vma={vmax}&ordem=1&&pag={pag}')
            except requests.exceptions.RequestException as error:
                raise SystemExit(error)
            
            houses_soup = BeautifulSoup(response.text, 'html.parser')

            #Separates all of the cards of the main page
            card_blocks : list[BeautifulSoup] = houses_soup.find_all('div', class_="muda_card1 ms-lg-0 col-12 col-md-12 col-lg-6 col-xl-4 mt-4 d-flex align-self-stretch justify-content-center")

            for card in card_blocks:
                print(f'\033[0;36mScraping page:{pag} Card: {cur_card}\033[0m')
                card_process(card, ccsv)

                cur_card += 1

            pagination = houses_soup.find(class_='pagination')

            #When it is the last page the button to go to the next page receives the class disabled
            #Will not work if there is less than one page
            if pag != 1 and pagination.find(class_='disabled') != None:
                break

            pag += 1
        
        end_of_scrape = time.time()

        print(f'\033[0;32mCardinali scraped sucessufuly\nScraping took {((end_of_scrape - start_of_scrape)/60):02f} min\033[0m')

scrape_cardinali()