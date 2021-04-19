#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import datetime
import traceback
import dateutil.parser
import babel
from flask import  render_template, request, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from forms import *
from models import *

from flask_wtf import CSRFProtect
csrf = CSRFProtect()

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
    form = VenueForm()

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

    return render_template('pages/venues.html', areas=data, form=form)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    form = VenueForm()
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
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''), form=form)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    form = VenueForm()
    # First, get the venue connected to the given venue id.
    venue = Venue.query.filter_by(id=venue_id).first()

    [past_shows, upcoming_shows] = parse_shows(venue.shows)

    genres = venue.genres
    genre_list = []
    for genre in genres:
        genre_list.append(genre.name)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": genre_list,
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

    return render_template('pages/show_venue.html', venue=data, form=form)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    genre_choices = Genre.query.all()
    genre_list = []
    for genre in genre_choices:
        # Have to make a list of tuples as first value is code variable while second is the string to be displayed .
        genre_list.append((genre.name, genre.name))
    form.genres.choices = genre_list
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    caught_exception = None
    formset = VenueForm()
    genre_choices = Genre.query.all()
    genre_list = []
    for genre in genre_choices:
        # Have to make a list of tuples as first value is code variable while second is the string to be displayed .
        genre_list.append((genre.name, genre.name))
    formset.genres.choices = genre_list
    if formset.validate_on_submit():
        try:
            name = request.form.get('name', '')
            city = request.form.get('city', '')
            state = request.form.get('state', '')
            address = request.form.get('address', '')
            phone = request.form.get('phone', '')
            genres = request.form.getlist('genres')
            facebook_link = request.form.get('facebook_link', '')
            image_link = request.form.get('image_link', '')
            website_link = request.form.get('website_link', '')
            seeking_talent = request.form.get('seeking_talent', '')
            if seeking_talent == 'y':
                seeking_talent = True
            else:
                seeking_talent = False
            seeking_description = request.form.get('seeking_description', '')

            # Make a venue object
            venue = Venue(name=name,
                          city=city,
                          state=state,
                          address=address,
                          phone=phone,
                          facebook_link=facebook_link,
                          image_link=image_link,
                          website_link=website_link,
                          looking_for_talent=seeking_talent,
                          seeking_description=seeking_description)

            # Make a genre object for each given genre.
            for genre_instance in genres:
                db_genre_instance = Genre(name=genre_instance)
                venue.genres.append(db_genre_instance)

            db.session.add(venue)
            db.session.commit()
        except Exception as e:
            error = True
            caught_exception = e.args[0]
            tb = traceback.format_exc()
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        error = True
    if error:
        form_errors = formset.errors
        message = 'An error occurred. Venue ' + request.form.get('name', '') + ' could not be listed:'
        for error_item in form_errors:
            message = message + ', \n'
            message = message + form_errors[error_item][0]
        if caught_exception:
            message = message + ', \n'
            message = message + caught_exception
        flash(message)
    else:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html', form=formset)

@app.route('/venues/<venue_id>/delete', methods=['GET', 'DELETE'])
def delete_venue(venue_id):
    name="(NAME UNOBTAINABLE)"
    form = VenueForm()
    try:
        error=False
        venue_instance = Venue.query.filter_by(id=venue_id).first()
        name = venue_instance.name
        db.session.delete(venue_instance)
        db.session.commit()
    except Exception as e:
        error = True
        tb = traceback.format_exc()
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + name + ' could not be deleted.')
    else:
        # on successful db insert, flash success
        flash('Venue ' + name + ' was successfully deleted!')
    return render_template('pages/home.html', form=form)


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    form = ArtistForm()
    data = []
    artists_all = Artist.query.all()
    for artist_instance in artists_all:
        artist_dict = {
            "id": artist_instance.id,
            "name": artist_instance.name
        }
        data.append(artist_dict)
    return render_template('pages/artists.html', artists=data, form=form)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    form = ArtistForm()
    search_term = '%' + request.form.get('search_term', '') + '%'
    artists = Artist.query.filter(Artist.name.ilike(search_term)).all()
    count = len(artists)

    # Build Data object
    data = []
    for artist in artists:
        data_object = {}
        data_object["id"] = artist.id
        data_object["name"] = artist.name
        [past_shows, future_shows] = parse_shows(artist.shows)
        data_object["num_upcoming_shows"] = len(future_shows)
        data.append(data_object)

    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''), form=form)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    form = ArtistForm()

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

    return render_template('pages/show_artist.html', artist=data, form=form)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # Obtain artist object based on artist id.
    db_artist = Artist.query.filter_by(id=artist_id).first()
    genres = db_artist.genres
    genre_list = []
    for genre in genres:
        genre_list.append(genre.name)
    genre_choices = Genre.query.all()
    genre_choice_list = []
    for genre in genre_choices:
        # Have to make a list of tuples as first value is code variable while second is the string to be displayed .
        genre_choice_list.append((genre.name, genre.name))
    form.genres.choices = genre_choice_list
    artist={
        'id': db_artist.id,
        'name': db_artist.name,
        'genres': genre_list,
        'city': db_artist.city,
        'state': db_artist.state,
        'phone': db_artist.phone,
        'website': db_artist.website_link,
        'facebook_link': db_artist.facebook_link,
        'seeking_venue': db_artist.seeking_venue,
        'seeking_description': db_artist.seeking_description,
        'image_link': db_artist.image_link
    }

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    caught_exception = False
    formset = ArtistForm()
    genre_choices = Genre.query.all()
    genre_list = []
    for genre in genre_choices:
        # Have to make a list of tuples as first value is code variable while second is the string to be displayed .
        genre_list.append((genre.name, genre.name))
    formset.genres.choices = genre_list
    if formset.validate_on_submit():
        try:
            name = request.form.get('name', '')
            city = request.form.get('city', '')
            state = request.form.get('state', '')
            phone = request.form.get('phone', '')
            genres = request.form.getlist('genres')
            facebook_link = request.form.get('facebook_link', '')
            image_link = request.form.get('image_link', '')
            website_link = request.form.get('website_link', '')
            seeking_venue = request.form.get('seeking_venue', '')
            if seeking_venue == 'y':
                seeking_venue = True
            else:
                seeking_venue = False
            seeking_description = request.form.get('seeking_description', '')

            # Grab the artist object
            artist = Artist.query.filter_by(id=artist_id).first()

            # Modify the values of the artist entry.
            artist.name = name
            artist.city = city
            artist.state = state
            artist.phone = phone
            artist.facebook_link = facebook_link
            artist.image_link = image_link
            artist.website_link = website_link
            artist.seeking_venue = seeking_venue
            artist.seeking_description = seeking_description

            # Clear the genre's associated with the artist to make way for new ones.
            artist.genres.clear()

            # Make a genre object for each given genre.
            for genre_instance in genres:
                db_genre_instance = Genre(name=genre_instance)
                artist.genres.append(db_genre_instance)

            print("1")
            db.session.commit()
        except Exception as e:
            error = True
            caught_exception = e.args[0]
            tb = traceback.format_exc()
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        error = True
    if error:
        form_errors = formset.errors
        message = 'An error occurred. Artist ' + request.form.get('name', '') + ' could not be modified:'
        for error_item in form_errors:
            message = message + ', \n'
            message = message + form_errors[error_item][0]
        if caught_exception:
            message = message + ', \n'
            message = message + caught_exception
        flash(message)
    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully modified!')

    return redirect(url_for('show_artist', artist_id=artist_id, form=formset))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # Obtain artist object based on artist id.
    db_venue = Venue.query.filter_by(id=venue_id).first()
    genres = db_venue.genres
    genre_list = []
    for genre in genres:
        genre_list.append(genre.name)
    genre_choices = Genre.query.all()
    genre_choice_list = []
    for genre in genre_choices:
        # Have to make a list of tuples as first value is code variable while second is the string to be displayed .
        genre_choice_list.append((genre.name, genre.name))
    form.genres.choices = genre_choice_list
    venue = {
        "id": db_venue.id,
        "name": db_venue.name,
        "genres": genre_list,
        "address": db_venue.address,
        "city": db_venue.city,
        "state": db_venue.state,
        "phone": db_venue.phone,
        "website": db_venue.website_link,
        "facebook_link": db_venue.facebook_link,
        "seeking_talent": db_venue.looking_for_talent,
        "seeking_description": db_venue.seeking_description,
        "image_link": db_venue.image_link
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    caught_exception = False
    formset = VenueForm()
    genre_choices = Genre.query.all()
    genre_list = []
    for genre in genre_choices:
        # Have to make a list of tuples as first value is code variable while second is the string to be displayed .
        genre_list.append((genre.name, genre.name))
    formset.genres.choices = genre_list
    if formset.validate_on_submit():
        try:
            name = request.form.get('name', '')
            city = request.form.get('city', '')
            state = request.form.get('state', '')
            phone = request.form.get('phone', '')
            genres = request.form.getlist('genres')
            address = request.form.get('address', '')
            facebook_link = request.form.get('facebook_link', '')
            image_link = request.form.get('image_link', '')
            website_link = request.form.get('website_link', '')
            seeking_talent = request.form.get('seeking_talent', '')
            if seeking_talent == 'y':
                seeking_talent = True
            else:
                seeking_talent = False
            seeking_description = request.form.get('seeking_description', '')

            # Grab the venue object
            venue = Venue.query.filter_by(id=venue_id).first()

            # Modify the values of the venue entry.
            venue.name = name
            venue.city = city
            venue.state = state
            venue.address = address
            venue.phone = phone
            venue.facebook_link = facebook_link
            venue.image_link = image_link
            venue.website_link = website_link
            venue.looking_for_talent = seeking_talent
            venue.seeking_description = seeking_description

            # Clear the genre's associated with the venue to make way for new ones.
            venue.genres.clear()

            # Make a genre object for each given genre.
            for genre_instance in genres:
                db_genre_instance = Genre(name=genre_instance)
                venue.genres.append(db_genre_instance)

            print("1")
            db.session.commit()
        except Exception as e:
            error = True
            caught_exception = e.args[0]
            tb = traceback.format_exc()
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        error = True
    if error:
        form_errors = formset.errors
        message = 'An error occurred. venue ' + request.form.get('name', '') + ' could not be modified:'
        for error_item in form_errors:
            message = message + ', \n'
            message = message + form_errors[error_item][0]
        if caught_exception:
            message = message + ', \n'
            message = message + caught_exception
        flash(message)
    else:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully modified!')

    return redirect(url_for('show_venue', venue_id=venue_id, form=formset))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    genre_choices = Genre.query.all()
    genre_list = []
    for genre in genre_choices:
        # Have to make a list of tuples as first value is code variable while second is the string to be displayed .
        genre_list.append((genre.name, genre.name))
    form.genres.choices = genre_list
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    caught_exception = False
    formset = ArtistForm()
    genre_choices = Genre.query.all()
    genre_list = []
    for genre in genre_choices:
        # Have to make a list of tuples as first value is code variable while second is the string to be displayed .
        genre_list.append((genre.name, genre.name))
    formset.genres.choices = genre_list
    if formset.validate_on_submit():
        try:
            name = request.form.get('name', '')
            city = request.form.get('city', '')
            state = request.form.get('state', '')
            phone = request.form.get('phone', '')
            genres = request.form.getlist('genres')
            facebook_link = request.form.get('facebook_link', '')
            image_link = request.form.get('image_link', '')
            website_link = request.form.get('website_link', '')
            seeking_venue = request.form.get('seeking_venue', '')
            if seeking_venue == 'y':
                seeking_venue = True
            else:
                seeking_venue = False
            seeking_description = request.form.get('seeking_description', '')

            # Make a artist object
            artist = Artist(name=name,
                            city=city,
                            state=state,
                            phone=phone,
                            facebook_link=facebook_link,
                            image_link=image_link,
                            website_link=website_link,
                            seeking_venue=seeking_venue,
                            seeking_description=seeking_description)

            # Make a genre object for each given genre.
            for genre_instance in genres:
                db_genre_instance = Genre(name=genre_instance)
                artist.genres.append(db_genre_instance)

            db.session.add(artist)
            db.session.commit()
        except Exception as e:
            error = True
            caught_exception = e.args[0]
            tb = traceback.format_exc()
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        error = True
    if error:
        form_errors = formset.errors
        message = 'An error occurred. Artist ' + request.form.get('name', '') + ' could not be listed:'
        for error_item in form_errors:
            message = message + ', \n'
            message = message + form_errors[error_item][0]
        if caught_exception:
            message = message + ', \n'
            message = message + caught_exception
        flash(message)
    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html', form=formset)

@app.route('/artists/<artist_id>/delete', methods=['GET', 'DELETE'])
def delete_artist(artist_id):
    form = ArtistForm()
    name="(NAME UNOBTAINABLE)"
    try:
        error=False
        artist_instance = Artist.query.filter_by(id=artist_id).first()
        name = artist_instance.name
        db.session.delete(artist_instance)
        db.session.commit()
    except Exception as e:
        error = True
        tb = traceback.format_exc()
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + name + ' could not be deleted.')
    else:
        # on successful db insert, flash success
        flash('Artist ' + name + ' was successfully deleted!')
    return render_template('pages/home.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    form = ShowForm()

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

    return render_template('pages/shows.html', shows=data, form=form)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    show_name = '(NAME UNAVAILABLE)'
    caught_exception = False
    formset = ShowForm()
    if formset.validate_on_submit():
        try:
            artist_id = request.form.get('artist_id', '')
            artist = Artist.query.filter_by(id=artist_id).first()
            artist_name = artist.name
            artist_image = artist.image_link

            venue_id = request.form.get('venue_id', '')
            venue = Venue.query.filter_by(id=venue_id).first()
            venue_name = venue.name
            venue_image = venue.image_link

            show_name = artist_name + '/' + venue_name

            start_time = format_datetime(request.form.get('start_time', ''))

            # Make a venue object
            show = Show(start_time=start_time,
                        artist_name=artist_name,
                        artist_image_link=artist_image,
                        venue_name=venue_name,
                        venue_image_link=venue_image,
                        artist_id=artist_id,
                        venue_id=venue_id,)

            db.session.add(show)
            db.session.commit()
        except Exception as e:
            error = True
            caught_exception = e.args[0]
            tb = traceback.format_exc()
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        error = True
    if error:
        form_errors = formset.errors
        message = 'An error occurred. Show ' + show_name + ' could not be listed:'
        for error_item in form_errors:
            message = message + ', \n'
            message = message + form_errors[error_item][0]
        if caught_exception:
            message = message + ', \n'
            message = message + caught_exception
        flash(message)
    else:
        # on successful db insert, flash success
        flash('Show ' + show_name + ' was successfully listed!')

    return render_template('pages/home.html')

@app.route('/shows/<show_id>/delete', methods=['GET', 'DELETE'])
def delete_show(show_id):
    form = ShowForm()
    show_name="(NAME UNOBTAINABLE)"
    try:
        error=False
        show_instance = Show.query.filter_by(id=show_id).first()
        show_name = show_instance.artist_name + '/' + show_instance.venue_name
        db.session.delete(show_instance)
        db.session.commit()
    except Exception as e:
        error = True
        tb = traceback.format_exc()
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show ' + show_name + ' could not be deleted.')
    else:
        # on successful db insert, flash success
        flash('Show ' + show_name + ' was successfully deleted!')
    return render_template('pages/home.html', form=form)


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
