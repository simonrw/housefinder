from slackclient import SlackClient


class SlackPoster(object):

    def __init__(self, listing, config):
        self.listing = listing
        self.client = SlackClient(config['slack']['api_key'])
        self.channel = config['slack']['channel']
        self.username = config['slack'].get('username', 'housefinder')

    def post(self):
        desc = '{}, {}, {} £{}k | {} bedrooms | detail: {} | {}'.format(
            self.listing.property_type, self.listing.displayable_address,
            self.listing.price_modifier_human,
            self.listing.price_thousands, self.listing.num_bedrooms,
            self.listing.details_url, self.listing.image_url)
        self.client.api_call(
            'chat.postMessage', channel=self.channel, text=desc,
            username=self.username, icon_emoji=':robot_face:'
        )
