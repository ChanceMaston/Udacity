#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import datetime
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
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
                             backref=db.backref('venues', lazy=True))
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
                             backref=db.backref('artists', lazy=True))
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


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

def compare_datetime(value1, value2):
    [value1_wd, value1_month, value1_day, value1_year, value1_time] = value1.split()
    [value2_wd, value2_month, value2_day, value2_year, value2_time] = value2.split()

    # First check the year
    if value1_year == value2_year:
        # Years are the same, check month
        if value1_month == value2_month:
            # Years and Months same, check day
            if value1_day == value2_day:
                # Year/Month/Day same, check time
                if 'PM' in value1_time:
                    value1_time = int(value1_time.replace('PM', '').replace(':', '')) + 1200
                else:
                    value1_time = int(value1_time.replace('AM', '').replace(':', ''))
                if 'PM' in value2_time:
                    value2_time = int(value2_time.replace('PM', '').replace(':', '')) + 1200
                else:
                    value2_time = int(value2_time.replace('AM', '').replace(':', ''))
                if value1_time == value2_time:
                    return 0  # Times are exact same
                else:  # Years/month/day same,time different.
                    if value1_time > value2_time:
                        return -1
                    else:
                        return 1
            else:  # Years and month same, day different.
                if value1_day > value2_day:
                    return -1
                else:
                    return 1
        else: # Years are same, months are different
            if value1_month > value2_month:
                return -1
            else:
                return 1
    else:  # Years are different.
        if value1_year > value2_year:
            return -1
        else:
            return 1

def parse_shows(shows_to_parse=None):
    if not shows_to_parse:
        raise Exception("Tried to parse shows with no input! (app.py, line 180")

    past_shows = []
    future_shows = []
    current_datetime = datetime.now()

    for show in shows_to_parse:
        datetime_comparison = compare_datetime(format_datetime(str(current_datetime)), format_datetime(show.start_time))
        if datetime_comparison > 0:  # Show is in the future
            future_shows.append(show)
        else:
            past_shows.append(show)

    return [past_shows, future_shows]

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/')
def index():
    return render_template('pages/home.html')


#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
    # Step 0: Create empty data object.
    data = []

    # Step 1: Pull venue data from database.
    venues = Venue.query.all()

    # Step 2: Cycle through each venue
    for venue in venues:
        # Step 2a: Initialize dictionary objects for venue data storage.
        venue_dict = {}
        city_state = {}

        # Step 2b: locate the city, state, and shows of this venue.
        venue_city = venue.city
        venue_state = venue.state
        venue_shows = venue.shows

        # Step 2c: Check if City/State combo already exists.
        index = 0
        found_city = False
        for city_dict in data:
            if city_dict.get('city', '') == venue_city and city_dict.get('state', '') == venue_state:
              # Found a dictionary that matches this venue's city/state combination.
                found_city = True  # Found the city
                break  # break out of the for loop.
            else:
              index += 1  # Increase index to keep track of what dictionary we are on.

        # Step 2d: Create venue object.
        venue_dict["id"] = venue.id
        venue_dict["name"] = venue.name
        [past_shows, future_shows] = parse_shows(venue_shows)
        venue_dict["num_upcoming_shows"] = len(future_shows)

        # Step 2e: If City/State combo already exists, add venue to its 'venues' list
        if found_city:
            data[index]["venues"].append(venue_dict)
        # Step 2f: Otherwise, create new city/state object in data object.
        else:
            city_state["city"] = venue_city
            city_state["state"] = venue_state
            city_state["venues"] = [venue_dict]
            data.append(city_state)

    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = '%' + request.form.get('search_term', '') + '%'
    venues = Venue.query.filter(Venue.name.ilike(search_term)).all()
    count = len(venues)

    # Build Data object
    data = []
    for venue in venues:
        data_object = {}
        data_object["id"] = venue.id
        data_object["name"] = venue.name
        [past_shows, future_shows] = parse_shows(venue.shows)
        data_object["num_upcoming_shows"] = len(future_shows)
        data.append(data_object)

    response={
      "count": count,
      "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # First, get the venue connected to the given venue id.
    venue = Venue.query.filter_by(id=venue_id).first()

    [past_shows, upcoming_shows] = parse_shows(venue.shows)

    genres = venue.genres

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.looking_for_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists_all = Artist.query.all()
  for artist_instance in artists_all:
      artist_dict = {
          "id": artist_instance.id,
          "name": artist_instance.name
      }
      data.append(artist_dict)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # First, get the venue connected to the given venue id.
    artist = Artist.query.filter_by(id=artist_id).first()
    shows = Show.query.filter_by(artist_id=artist_id).all()

    [past_shows, upcoming_shows] = parse_shows(shows_to_parse=shows)

    genres = artist.genres
    genre_list = []
    for genre in genres:
        genre_list.append(genre.name)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": genre_list,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows

  data = []
  all_shows = Show.query.all()
  for show_instance in all_shows:
      venue_instance = Venue.query.filter_by(id=show_instance.venue_id).first()
      artist_instance = Artist.query.filter_by(id=show_instance.artist_id).first()
      show_dict = {
          "venue_id": venue_instance.id,
          "venue_name": venue_instance.name,
          "artist_id": artist_instance.id,
          "artist_name": artist_instance.name,
          "artist_image_link": artist_instance.image_link,
          "start_time": show_instance.start_time
      }
      data.append(show_dict)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
