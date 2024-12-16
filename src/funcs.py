import os
import sqlite3 as sqll
import time

import osmnx as ox
import networkx as nx

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
        
def find_loc_coordinates(location : str, 
                         geocode_db : sqll.Connection, geocode_db_cursor : sqll.Cursor
                         ) -> None | tuple[float, float]:
    query_location = geocode_db_cursor.execute("SELECT coord1, coord2 FROM geocode WHERE location LIKE ?", ("'" + location + "'",))
    house_location = query_location.fetchall()

    #Value is not already in databases
    if house_location == []:
        try:
            house_location = ox.geocode(f'{location}, São Carlos, Brazil')
            geocode_db_cursor.execute("INSERT INTO geocode VALUES (?, ?, ?)", ("'" + location + "'", house_location[0], house_location[1]))
            geocode_db.commit()
            time.sleep(1.1)
            return house_location
        except ox._errors.InsufficientResponseError as error:
            time.sleep(1.1)
            return None
    else:
        return house_location[0]