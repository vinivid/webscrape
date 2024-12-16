import csv
import _csv
import time
import sqlite3 as sqll
import re

import osmnx as ox
import networkx as nx
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup

from funcs import find_loc_coordinates

def goto_houses_pages(page : Page, 
                      lower_bound : int, upper_boud : int
                      ) -> None:
    """Uses the main page to acess the houses page, this is necessary
    so there won't be houses from locations other than são carlos"""

    page.goto("https://roca.com.br/")
    page.locator('#morefilter-search').click()
    page.get_by_placeholder('Buscar cidade, bairro, condomínio ou código').type('São Carlos, SP')
    page.get_by_label('De (R$').type(f'{lower_bound}00')
    page.get_by_label('Até (R$)').type(f'{upper_boud}00')
    page.locator('#search-findProperty').click()

def scroll_entire_houses_page(page : Page) -> None:
    "Scroll to the bottom the houses page."

    #Gets the number of houses that will be on this page so we can know how many times
    #we will have to scroll to go to the bottom of the page.
    page.wait_for_selector('h1')
    qtt_of_houses = page.locator('h1').all_text_contents()[0].split()[0]

    #Amount of scrolls necessary to scroll the whole page
    num_scrolls = (int(qtt_of_houses, 10) // 12) + 1
    
    #https://roca.com.br/api/service/consult
    #These wait times are hardcoded because the wait for response does'nt fucking work
    #correctly, maybe the scrolls are not covering enough distance
    page.wait_for_timeout(1500)

    for _ in range(0, num_scrolls * 3):
        page.mouse.wheel(0, 720)
        page.wait_for_timeout(1500)

def process_MuiGrid(mui : BeautifulSoup, 
                    destination , city_graph : nx.MultiDiGraph,
                    geocode_db : sqll.Connection, geocode_db_cursor : sqll.Cursor,
                    csv_file : '_csv._writer') -> None:
    
    house_name = mui.find('h2').text

    if re.match(r"comercial|terreno", house_name, re.IGNORECASE): 
        return
    
    house_link : str = 'https://roca.com.br' + (mui.find('a', href=True)['href'])
    house_page = BeautifulSoup(requests.get(house_link).text, 'html.parser')
    house_rent = house_page.find(class_='MuiTypography-root PricesSidebar__CustomTypography-sc-1yjdceo-0 hJGMSK MuiTypography-body1').text   
    location = house_page.find_all(class_="MuiTypography-root MuiLink-root MuiLink-underlineHover MuiTypography-colorInherit")[2].text

    house_location = find_loc_coordinates(location, geocode_db, geocode_db_cursor)
    if house_location == None:
        return

    house_node = ox.nearest_nodes(city_graph, X=house_location[1], Y=house_location[0])
    travel_time = nx.shortest_path_length(city_graph, house_node, destination, weight='travel_time') / 60
    shortest_distance = nx.shortest_path_length(city_graph, house_node, destination, weight='length')
    house_rent = house_rent.removeprefix('R$ ').replace(',', '.')

    csv_file.writerow(["'" + house_name + "'", house_rent, round(shortest_distance, 1), round(travel_time, 1), house_link])

def scrape_roca_sc(sc_graph_map : nx.MultiDiGraph, destination : tuple[float, float],
                   geocode_db : sqll.Connection, geocode_cur : sqll.Cursor,
                   ) -> None:
    
    destination_node = ox.nearest_nodes(sc_graph_map, X=destination[1], Y=destination[0])

    print(f'\033[0;32mScraping Roca\033[0m')

    #Current value starts with the minimum value
    curr_value = 300
    end_value = 1500

    with open('./scraped_data/roca.csv', 'w', newline='') as cardinali_csv:
        ccsv = csv.writer(cardinali_csv, delimiter=',')

        start_of_scrape = time.time()

        with sync_playwright() as pw:
            browser = pw.firefox.launch()
            page = browser.new_page()
            
            #Removing the images while scraping because they are useless
            page.route(re.compile(r"\.(jpg|png|svg)$"), lambda route: route.abort()) 

            while curr_value < end_value:
                goto_houses_pages(page, curr_value, curr_value + 50)

                scroll_entire_houses_page(page)

                soup = BeautifulSoup(page.content(), 'html.parser')
                all_muis : list[BeautifulSoup] = soup.find_all(class_="MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-md-6 MuiGrid-grid-lg-3")

                for mui in all_muis:
                    process_MuiGrid(mui, destination_node, sc_graph_map, geocode_db, geocode_cur, ccsv)

                curr_value += 50

            browser.close()
        
        end_of_scrape = time.time()
        print(f'\033[0;32mRoca scraped sucessufuly\nScraping took {round((end_of_scrape - start_of_scrape)/60, 2)} min\033[0m')
