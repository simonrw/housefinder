import requests


class TrelloPoster(object):

    LISTS_URL = 'https://trello.com/1/lists/{list_id}/cards'
    ATTACHMENTS_URL = 'https://trello.com/1/cards/{card_id}/attachments'

    def __init__(self, listing):
        self.listing = listing
        self.session = requests.Session()
        self.session.params = {
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
