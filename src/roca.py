import time
import re

from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def goto_houses_pages(page : Page, 
                      lower_bound : int, upper_boud : int
                      ) -> None:
    "Uses the main page to acess the houses page"

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
    num_scrolls = (int(qtt_of_houses, 10) // 12)
    
    #https://roca.com.br/api/service/consult
    #These wait times are hardcoded because the wait for response does'nt fucking work
    #correctly, maybe the scrolls are not covering enough distance
    page.wait_for_timeout(1500)

    for _ in range(0, num_scrolls * 3):
        page.mouse.wheel(0, 720)
        page.wait_for_timeout(1500)

def scrape_roca_sc() -> None:
    #Current value starts with the minimum value
    curr_value = 300
    end_value = 1500

    with sync_playwright() as pw:
        browser = pw.firefox.launch(headless=False)
        page = browser.new_page()
        
        #Removing the images while scraping because they are useless
        page.route(re.compile(r"\.(jpg|png|svg)$"), lambda route: route.abort()) 

        goto_houses_pages(page, 700, 750)

        scroll_entire_houses_page(page)

        soup = BeautifulSoup(page.content())

        print(soup.prettify())

        browser.close()

scrape_roca_sc()