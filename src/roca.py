import csv
import _csv
import time
import sqlite3 as sqll
import re
import json

import osmnx as ox
import networkx as nx
import requests
from bs4 import BeautifulSoup

def scrape_roca_sc(sc_graph_map : nx.MultiDiGraph, destination : tuple[float, float],
                   ) -> None:
    
    destination_node = ox.nearest_nodes(sc_graph_map, X=destination[1], Y=destination[0])

    print(f'\033[0;32mScraping Roca\033[0m')

    #Current value starts with the minimum value
    curr_value = 300
    end_value = 1500

    with open('./scraped_data/roca.csv', 'w', newline='') as cardinali_csv:
        ccsv = csv.writer(cardinali_csv, delimiter=',')

        start_of_scrape = time.time()

        #page.goto(f'https://roca.com.br/alugar/sao-carlos-sp/de-{300}.00/ate-{1300}.00')

        thingo = requests.post("https://roca.com.br/api/service/consult", headers={'content-type':'application/json; charset=utf-8'},data='{"start":0,"numRows":717,"type":"L","place":null,"idtCityList":[1],"idtDistrictList":[],"idtCondominiumList":[],"idtsCategories":[],"idtsSubCategories":[],"mapSubCategories":{},"rooms":null,"bathrooms":null,"garages":null,"characteristics":[],"condominiumCharacteristics":[],"fromPrice":"300.00","toPrice":"1300.00","minArea":null,"maxArea":null,"usefulArea":false,"namStreet":null,"searchTotal":false,"searchPrevisionOutput":false,"flgRentByPeriod":false,"idtsCampaigns":[],"getAccess":true,"post":true,"sortList":["moreRecentsLocation"],"fieldList":["idtProperty","jsonPhotos","jsonPhotosCondominium","namStreet","namDistrict","idtDistrict","namCity","idtCity","namState","namCategory","idtCategory","namSubCategory","idtSubCategory","prop_char_5","prop_char_1","prop_char_2","prop_char_95","prop_char_176","valLocation","valSales","valMonthIptu","valCondominium","numNumber","namCondominium","idtCondominium","latitude","longitude","latitudeAndLongitude","flgShowMapSite","indStatus","totalRooms","totalGarages","prop_char_12","idtsCharacteristics","idtsCondominiumCharacteristics","indType","flgHighlight","jsonCampaigns","campainSale","campainLocation","jsonOffers","flgHideValSaleSite","flgHideValLocationSite","flgRentByPeriod","idtsCaptivators","idtExternal","indApprovedDocumentationReserve","flgReservedLocation","flgReservedSale","flgPendingLocation","dtaPrevisionOutput","flgExclusiveLocation","flgExclusiveSale","desTitleSite","urlVideo","desUrl360Site","dtaExpirationAuthorizationCaptationLocation","dtaExpirationAuthorizationCaptationSales","valPercentageIptu","prop_char_106","prop_char_107"],"jsonPhotosNum":5}').json()

        with open('ok.json', 'w') as fl:
            fl.write(json.dumps(thingo, indent=2))

        #browser.close()
        
        end_of_scrape = time.time()
        print(f'\033[0;32mRoca scraped sucessufuly\nScraping took {round((end_of_scrape - start_of_scrape)/60, 2)} min\033[0m')
