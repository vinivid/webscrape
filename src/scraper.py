import os
import sqlite3 as sqll
import time

import osmnx as ox
import networkx as nx

from funcs import *
from cardinali import scrape_cardinali_sc
from roca import scrape_roca_sc

USP_COORDINATES = (-22.0062, -47.89518)

def main():
    sc_graph = init_map_of_city()
    geoc_db, geoc_cur = init_sqll_db()

    if not os.path.exists('./scraped_data'):
        os.makedirs('./scraped_data')

    scrape_cardinali_sc(sc_graph, USP_COORDINATES, geoc_db, geoc_cur)
    scrape_roca_sc(sc_graph, USP_COORDINATES, geoc_db, geoc_cur)

if __name__ == '__main__':
    main()