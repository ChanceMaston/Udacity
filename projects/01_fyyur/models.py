from flask import Flask
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from forms import *

from flask_wtf import CSRFProtect
csrf = CSRFProtect()

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
csrf.init_app(app)
db = SQLAlchemy(app)

migrate = Migrate(app=app, db=db)



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# Need an association table for Venue-to-Genre
venue_genre_items = db.Table('venue_genre_items',
                             db.Column('genre_id',
                                       db.Integer,
                                       db.ForeignKey('genres.id'),
                                       primary_key=True),
                             db.Column('venue_id',
                                       db.Integer,
                                       db.ForeignKey('venues.id'),
                                       primary_key=True)
)

# Need an association table for Artist-to-Genre
artist_genre_items = db.Table('artist_genre_items',
                              db.Column('genre_id',
                                        db.Integer,
                                        db.ForeignKey('genres.id'),
                                        primary_key=True),
                              db.Column('artist_id',
                                        db.Integer,
                                        db.ForeignKey('artists.id'),
                                        primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('Genre',
                             secondary=venue_genre_items,
                             backref=db.backref('venues', cascade="all", lazy=True))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    looking_for_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venues', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'



class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('Genre',
                             secondary=artist_genre_items,
                             backref=db.backref('artists', cascade='all', lazy=True))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artists', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String)
    artist_name = db.Column(db.String)
    artist_image_link = db.Column(db.String(500))
    venue_name = db.Column(db.String)
    venue_image_link = db.Column(db.String(500))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} {self.start_time}>'


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return f'<Genre {self.id} {self.name}>'

