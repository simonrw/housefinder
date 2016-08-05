import requests
from .db import Listing


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
