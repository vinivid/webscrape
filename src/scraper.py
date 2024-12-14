import os
import sqlite3 as sqll

import osmnx as ox
import networkx as nx

from cardinali import scrape_cardinali_sc

CARDINALI_DOMAIN = 'https://www.cardinali.com.br'
USP_COORDINATES = (-22.0062, -47.89518)

def init_sqll_db() -> tuple[sqll.Connection, sqll.Cursor]:
    """
    Initializes the database of coordinates of the city so you do not need to 
    acess the Nominatian API for repeteadet locations.
    """

    try:
        geocode_db = sqll.connect('./db/geocode.db')
        gcd_cur = geocode_db.cursor()
        gcd_cur.execute("CREATE TABLE IF NOT EXISTS geocode(location TEXT UNIQUE, coord1 REAL, coord2 REAL)")
        return geocode_db, gcd_cur
    except sqll.Error as error:
        raise SystemExit(error)

def init_map_of_city() -> nx.MultiDiGraph:
    """
        Creates the Graph that represents the map of the city. 
    """

    if os.path.isfile('./scgraph/sc.graphml'):
        print('Graph of the city already created, loading it.')
        try:
            GRAPH_SAO_CARLOS = ox.load_graphml('./scgraph/sc.graphml')
            return GRAPH_SAO_CARLOS
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
            return GRAPH_SAO_CARLOS
        except IOError as error:
            raise SystemExit(error)
        
def scrape_cardinali() -> None:
    sc_graph = init_map_of_city()
    geoc_db, geoc_cur = init_sqll_db()

    scrape_cardinali_sc(sc_graph, USP_COORDINATES, geoc_db, geoc_cur)

    geoc_db.close()