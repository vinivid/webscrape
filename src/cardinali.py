import csv
import _csv
import time
import sqlite3 as sqll

import osmnx as ox
import networkx as nx
import requests
from bs4 import BeautifulSoup

CARDINALI_DOMAIN = 'https://www.cardinali.com.br'

def card_process(card : BeautifulSoup, 
                 destination , city_graph : nx.MultiDiGraph,
                 geocode_db : sqll.Connection, geocode_db_cursor : sqll.Cursor,
                 csv_file : '_csv._writer') -> None:
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

    query_location = geocode_db_cursor.execute("SELECT coord1, coord2 FROM geocode WHERE location LIKE ?", ("'" + location + "'",))
    house_location = query_location.fetchall()

    #Value is not already in databases
    if house_location == []:
        print('\t\033[0;33mLocation not already in database. Using Nominatim API and updating it.\033[0m')
        try:
            house_location = ox.geocode(f'{location}, São Carlos, Brazil')
            geocode_db_cursor.execute("INSERT INTO geocode VALUES (?, ?, ?)", ("'" + location + "'", house_location[0], house_location[1]))
            geocode_db.commit()
            print('\tWaiting 1.1 sec for the Nominatim api')
            time.sleep(1.1)
        except ox._errors.InsufficientResponseError as error:
            print(f'\t\033[0;31mLocation \033[4m{location}\033[0m \033[0;31mnot on Nominatim\033[0m')
            print('\tWaiting 1.1 sec for the Nominatim api')
            time.sleep(1.1)
            return
    else:
        print("\t\033[0;32mLocation already in database.\033[0m")
        house_location = house_location[0]

    house_node = ox.nearest_nodes(city_graph, X=house_location[1], Y=house_location[0])
    travel_time = nx.shortest_path_length(city_graph, house_node, destination, weight='travel_time') / 60
    shortest_distance = nx.shortest_path_length(city_graph, house_node, destination, weight='length')

    csv_file.writerow([house_name, house_rent_value, round(shortest_distance, 1), round(travel_time, 1),f'{CARDINALI_DOMAIN}/{house_info_path}'])

def scrape_cardinali_sc(sc_graph_map : nx.MultiDiGraph, destination : tuple[float, float],
                     geocode_db : sqll.Connection, geocode_cur : sqll.Cursor
                     ) -> None:
    
    destination_node = ox.nearest_nodes(sc_graph_map, X=destination[1], Y=destination[0])

    pag = 1
    cur_card = 1
    vmin = 200
    vmax = 1500

    print(f'\033[0;32mScraping Cardinali\033[0m')

    with open('../scraped_data/cardinali.csv', 'w', newline='') as cardinali_csv:
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
                card_process(card, destination_node, sc_graph_map, geocode_db, geocode_cur, ccsv)

                cur_card += 1

            pagination = houses_soup.find(class_='pagination')

            #When it is the last page the button to go to the next page receives the class disabled
            #Will not work if there is less than one page
            if pag != 1 and pagination.find(class_='disabled') != None:
                break

            pag += 1
       
    end_of_scrape = time.time()

    print(f'\033[0;32mCardinali scraped sucessufuly\nScraping took {round((end_of_scrape - start_of_scrape)/60, 2)} min\033[0m')