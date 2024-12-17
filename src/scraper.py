import os
import sys
import argparse

from funcs import *
from cardinali import scrape_cardinali_sc
from roca import scrape_roca_sc

USP_COORDINATES = (-22.0062, -47.89518)

def main():
    arg_parser = argparse.ArgumentParser(
        prog='Scraper imobiliarias',
        description='Coloca todos os dados das casas das imobiliarias em arquivos .csv',
        epilog='Para qualquer ajuda envie um email para frato.vini@gmail.com'
    )

    arg_parser.add_argument('filename', help='O nome do arquivo, que ja é dado quando o script é executado.')
    arg_parser.add_argument('-vmin', help='O menor valor que uma casa pode ter. Valor padrão é 0.', default=0)
    arg_parser.add_argument('-vmax', help='Mais ou menos o valor máximo que uma casa pode ter. Não é um limite muito preciso. Valor padrão 2000', default=2000)
    arg_parser.add_argument('-p', help='O caminho em que deve ser salvo os arquivos csv\'s.', default=None)
    
    arg_parser.print_help()

    args = vars(arg_parser.parse_args(sys.argv))

    sc_graph = init_map_of_city()

    if not os.path.exists('./db'):
        os.makedirs('./db')

    geoc_db, geoc_cur = init_sqll_db()

    if args['p'] != None:
        if not os.path.exists(args['p']):
            os.makedirs(args['p'])

        scrape_cardinali_sc(sc_graph, USP_COORDINATES, geoc_db, geoc_cur, args['vmin'], args['vmax'], args['p'])
        scrape_roca_sc(sc_graph, USP_COORDINATES, args['vmin'], args['vmax'], args['p'])
    else:
        if not os.path.exists('./scraped_data'):
            os.makedirs('./scraped_data')

        scrape_cardinali_sc(sc_graph, USP_COORDINATES, geoc_db, geoc_cur, args['vmin'], args['vmax'], './scraped_data')
        scrape_roca_sc(sc_graph, USP_COORDINATES, args['vmin'], args['vmax'], './scraped_data')

if __name__ == '__main__':
    main()