#!/usr/bin/env python
# -*- coding: utf-8 -*-


from concurrent.futures import ThreadPoolExecutor, wait
from configparser import ConfigParser
import argparse

from .zoopla import Zoopla, SearchParameters
from .db import create_session
from .posters.trello import TrelloPoster
from .posters.slack import SlackPoster


def main():
    description = '''
    Find a house!
    '''

    epilog = '''
    '''

    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('-c', '--config', required=False, default='config.cfg')
    args = parser.parse_args()

    config = ConfigParser()
    config.read(args.config)

    api = Zoopla(config['zoopla']['api_key'])

    params = SearchParameters()
    params.minimum_price = config['zoopla']['minimum_price']
    params.maximum_price = config['zoopla']['maximum_price']
    params.listing_status = 'sale'
    params.minimum_beds = config['zoopla']['minimum_beds']
    params.property_type = config['zoopla']['property_type']

    session = create_session(config=config)()

    listings = list(api.search_area(config['zoopla']['area'], search_params=params))

    futures = []
    with ThreadPoolExecutor() as executor:
        for listing in api.search_area(config['zoopla']['area'], search_params=params):
            if not listing.persisted(session):
                print(listing)
                session.add(listing)
                futures.append(
                    executor.submit(lambda: TrelloPoster(listing, config=config).post())
                )
                futures.append(
                    executor.submit(lambda: SlackPoster(listing, config=config).post())
                )

    wait(futures)
    session.commit()
