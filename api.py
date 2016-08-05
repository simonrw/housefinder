#!/usr/bin/env python
# -*- coding: utf-8 -*-


from concurrent.futures import ThreadPoolExecutor, wait
import requests
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from slackclient import SlackClient
from configparser import ConfigParser

config = ConfigParser()
config.read('config.cfg')

SLACK_API_KEY = config['slack']['api_key']
SLACK_CHANNEL = config['slack']['channel']
ZOOPLA_API_KEY = config['zoopla']['api_key']

engine = sa.create_engine('postgres://simon@localhost/housefinder')
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)

slack_client = SlackClient(SLACK_API_KEY)

class SlackPoster(object):
    def __init__(self, listing):
        self.listing = listing
        self.client = slack_client

    def post(self):
        desc = '{}, {} £{}k | {} bedrooms | detail: {} | {}'.format(
            self.listing.property_type, self.listing.price_modifier_human,
            self.listing.price_thousands, self.listing.num_bedrooms,
            self.listing.details_url, self.listing.image_url)
        self.client.api_call(
            'chat.postMessage', channel=SLACK_CHANNEL, text=desc,
            username='housefinder', icon_emoji=':robot_face:'
        )

class TrelloPoster(object):

    LISTS_URL = 'https://trello.com/1/lists/{list_id}/cards'
    ATTACHMENTS_URL = 'https://trello.com/1/cards/{card_id}/attachments'

    def __init__(self, listing):
        self.listing = listing
        self.session = requests.Session()
        self.auth_params = {
            'key': config['trello']['api_key'],
            'token': config['trello']['token'],
        }

    def post(self):
        card_id = self.post_card()
        self.add_thumbnail(card_id)

    def post_card(self):
        data = {
            'name': '{listing.price_human} - {listing.displayable_address}'.format(
                listing=self.listing),
            'desc': '''{listing.property_type}

* {listing.price_modifier_human} {listing.price_human}
* {listing.num_bedrooms} bedrooms
* {listing.num_bathrooms} bathrooms
* Details: {listing.details_url}

{listing.description}
'''.format(listing=self.listing),
        }

        response = self.session.post(
            self.LISTS_URL.format(
                list_id=config['trello']['list_id']
            ),
            data=data,
            params=self.auth_params
        )
        response.raise_for_status()

        card = response.json()
        return card['id']

    def add_thumbnail(self, card_id):
        data = {
            'url': self.listing.image_url,
        }

        response = self.session.post(
            self.ATTACHMENTS_URL.format(
                card_id=card_id
            ),
            data=data,
            params=self.auth_params
        )
        response.raise_for_status()


class Listing(Base):
    __tablename__ = 'listings'

    listing_id = sa.Column(sa.Integer, primary_key=True)
    details_url = sa.Column(sa.String, nullable=False)
    price = sa.Column(sa.Float, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    longitude = sa.Column(sa.Float)
    latitude = sa.Column(sa.Float)
    status = sa.Column(sa.String)
    listing_status = sa.Column(sa.String)
    num_bedrooms = sa.Column(sa.Integer)
    property_type = sa.Column(sa.String)
    displayable_address = sa.Column(sa.String)
    price_modifier = sa.Column(sa.String)
    num_bathrooms = sa.Column(sa.Integer)
    thumbnail_url = sa.Column(sa.String)
    image_url = sa.Column(sa.String)

    @property
    def price_thousands(self):
        return int(self.price) // 1000

    @property
    def price_human(self):
        return '£{}k'.format(self.price_thousands)

    def persisted(self, session):
        return session.query(self.__class__).get(self.listing_id) is not None

    def __repr__(self):
        return '<Listing {} - {}>'.format(self.listing_id, self.details_url)

    @property
    def price_modifier_human(self):
        if self.price_modifier:
            return self.price_modifier.replace('_', ' ')
        else:
            return ''

    def post_to(self, poster=TrelloPoster):
        poster(self).post()


class SearchParameters(object):
    keys = ['order_by', 'ordering', 'listing_status', 'include_sold', 'include_rented',
            'minimum_price', 'maximum_price', 'minimum_beds', 'maximum_beds', 'furnished',
            'property_type', 'new_homes', 'chain_free', 'keywords', 'listing_id',
            'branch_id', 'page_number', 'page_size', 'summarised']

    def __init__(self):
        for key in self.keys:
            setattr(self, key, None)

    def serialize(self):
        return { key: getattr(self, key) for key in self.keys
                if getattr(self, key, None) is not None }


class Zoopla(object):

    LISTINGS_URI = 'http://api.zoopla.co.uk/api/v1/property_listings.json'

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()

    def get_nentries(self, area, search_params):
        params = {'area': area, 'api_key': self.api_key, 'page_size': 1}
        for key in search_params.serialize():
            params[key] = getattr(search_params, key)

        response = self.session.get(self.LISTINGS_URI, params=params)
        response.raise_for_status()
        return response.json()['result_count']


    def search_area(self, area, search_params=None):
        search_params = search_params if search_params is not None else SearchParameters()

        params = {'area': area, 'api_key': self.api_key, 'page_size': 10}
        for key in search_params.serialize():
            params[key] = getattr(search_params, key)

        nentries = self.get_nentries(area, search_params)
        params['page_size'] = 100

        for i in range((nentries // 100) + 1):
            response = self.session.get(self.LISTINGS_URI, params=params)
            response.raise_for_status()

            json = response.json()
            results_count = json['result_count']
            params['page_number'] = i + 1

            for listing in json['listing']:
                column_names = Listing.metadata.tables['listings'].columns.keys()
                listing = Listing(**{ key: listing.get(key) for key in column_names })
                yield listing

            nentries -= 100

            if nentries < 100:
                params['page_size'] = nentries

    def search_postcode(self, postcode):
        pass


if __name__ == '__main__':
    Base.metadata.create_all()
    api = Zoopla(ZOOPLA_API_KEY)
    params = SearchParameters()
    params.minimum_price = config['zoopla']['minimum_price']
    params.maximum_price = config['zoopla']['maximum_price']
    params.listing_status = 'sale'
    params.minimum_beds = config['zoopla']['minimum_beds']
    params.property_type = config['zoopla']['property_type']

    session = Session()

    futures = []
    with ThreadPoolExecutor() as executor:
        for listing in api.search_area(config['zoopla']['area'], search_params=params):
            if not listing.persisted(session):
                print(listing)
                session.add(listing)
                futures.append(executor.submit(listing.post_to))

    wait(futures)
    session.commit()
