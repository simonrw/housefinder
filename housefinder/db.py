import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


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


def create_session(config):
    engine = sa.create_engine('postgres://simon@localhost/housefinder')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    return Session
