#!/usr/bin/env python
# -*- coding: utf-8 -*-


from concurrent.futures import ThreadPoolExecutor, wait
from configparser import ConfigParser

from .zoopla import Zoopla, SearchParameters
from .db import create_session
from .posters.trello import TrelloPoster

config = ConfigParser()
config.read('config.cfg')

ZOOPLA_API_KEY = config['zoopla']['api_key']

def main():
    api = Zoopla(ZOOPLA_API_KEY)

    params = SearchParameters()
    params.minimum_price = config['zoopla']['minimum_price']
    params.maximum_price = config['zoopla']['maximum_price']
    params.listing_status = 'sale'
    params.minimum_beds = config['zoopla']['minimum_beds']
    params.property_type = config['zoopla']['property_type']

    session = create_session(config=config)()

    futures = []
    with ThreadPoolExecutor() as executor:
        for listing in api.search_area(config['zoopla']['area'], search_params=params):
            if not listing.persisted(session):
                print(listing)
                session.add(listing)
                futures.append(executor.submit(lambda: TrelloPoster(listing).post()))

    wait(futures)
    session.commit()
