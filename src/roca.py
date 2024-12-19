import csv
import _csv
import time

import osmnx as ox
import networkx as nx
import requests
from bs4 import BeautifulSoup

def process_house(house : dict, 
                  sc_graph_map : nx.MultiDiGraph, destination,
                  csv_w : '_csv._writer'
                  ) -> None:
    
    if not 'desTitleSite' in house:
        return

    if house['namCategory'] == 'Comercial' or house['namCategory'] == 'Terreno':
        return

    if not 'latitude' in house or not 'longitude' in house:
        return

    house_node = ox.nearest_nodes(sc_graph_map, X=float(house['longitude']), Y=float(house['latitude']))
    travel_time = nx.shortest_path_length(sc_graph_map, house_node, destination, weight='travel_time') / 60
    shortest_distance = nx.shortest_path_length(sc_graph_map, house_node, destination, weight='length')

    if not 'valLocation' in house:
        return
    
    rent = house['valLocation']

    if 'valMonthIptu' in house and house['valMonthIptu'] != None:
        rent += house['valMonthIptu']

    if 'valCondominium' in house and house['valCondominium'] != None:
        rent += house['valCondominium']

    csv_w.writerow([house['desTitleSite'].replace(',', ' '), rent, round(travel_time, 1) ,round(shortest_distance, 1), house['namDistrict'],f'https://roca.com.br/imovel/locacao/{house['namCategory']}/sao-carlos/{house['namDistrict'].replace(' ', '-').lower()}/{house['idtProperty']}'])

def scrape_roca_sc(sc_graph_map : nx.MultiDiGraph, destination : tuple[float, float],
                   minimun : int, maximum : int, path_to_save : str,
                   ) -> None:
    
    destination_node = ox.nearest_nodes(sc_graph_map, X=destination[1], Y=destination[0])

    print(f'\033[0;32mScraping Roca\033[0m')

    #Current value starts with the minimum value
    start_value = minimun
    end_value = maximum

    with open(f'{path_to_save}/roca.csv', 'w', newline='') as cardinali_csv:
        ccsv = csv.writer(cardinali_csv, delimiter=',')
        
        ccsv.writerow(['Mome da casa', 'Valor do aluguel', 'Tempo até a USP andando', 'Tamanho do menor caminho', 'Bairro', 'Link para a propriedade'])

        start_of_scrape = time.time()

        page = requests.get(f'https://roca.com.br/alugar/sao-carlos-sp/de-{start_value}.00/ate-{end_value}.00/valor-total')
        page_soup = BeautifulSoup(page.text, 'html.parser')
        number_of_houses = page_soup.find('h1').find('span').string

        all_houses : dict = requests.post("https://roca.com.br/api/service/consult", headers={'content-type':'application/json; charset=utf-8'},data='{"start":0,"numRows":' + number_of_houses + ',"type":"L","place":null,"idtCityList":[1],"idtDistrictList":[],"idtCondominiumList":[],"idtsCategories":[],"idtsSubCategories":[],"mapSubCategories":{},"rooms":null,"bathrooms":null,"garages":null,"characteristics":[],"condominiumCharacteristics":[],"fromPrice":"' + str(start_value) + '","toPrice":"'+ str(end_value) +'","minArea":null,"maxArea":null,"usefulArea":false,"namStreet":null,"searchTotal":true,"searchPrevisionOutput":false,"flgRentByPeriod":false,"idtsCampaigns":[],"getAccess":true,"post":true,"sortList":["moreRecentsLocation"],"fieldList":["idtProperty","jsonPhotos","jsonPhotosCondominium","namStreet","namDistrict","idtDistrict","namCity","idtCity","namState","namCategory","idtCategory","namSubCategory","idtSubCategory","prop_char_5","prop_char_1","prop_char_2","prop_char_95","prop_char_176","valLocation","valSales","valMonthIptu","valCondominium","numNumber","namCondominium","idtCondominium","latitude","longitude","latitudeAndLongitude","flgShowMapSite","indStatus","totalRooms","totalGarages","prop_char_12","idtsCharacteristics","idtsCondominiumCharacteristics","indType","flgHighlight","jsonCampaigns","campainSale","campainLocation","jsonOffers","flgHideValSaleSite","flgHideValLocationSite","flgRentByPeriod","idtsCaptivators","idtExternal","indApprovedDocumentationReserve","flgReservedLocation","flgReservedSale","flgPendingLocation","dtaPrevisionOutput","flgExclusiveLocation","flgExclusiveSale","desTitleSite","urlVideo","desUrl360Site","dtaExpirationAuthorizationCaptationLocation","dtaExpirationAuthorizationCaptationSales","valPercentageIptu","prop_char_106","prop_char_107"],"jsonPhotosNum":5}').json()

        for house in all_houses['response']['docs']:
            process_house(house, sc_graph_map, destination_node, ccsv)
        
        end_of_scrape = time.time()
        print(f'\033[0;32mRoca scraped sucessufuly\nScraping took {round((end_of_scrape - start_of_scrape)/60, 2)} min\033[0m')
