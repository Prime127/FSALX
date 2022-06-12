#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from markupsafe import Markup
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.(DONE-WORKING)
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database(DONE IN Config.py)(DONE-WORKING)

#----------------------------------------------------------------------------#
# Models.(DONE-WORKING)
#----------------------------------------------------------------------------#






#----------------------------------------------------------------------------#
# Filters.(DONE-WORKING)
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.(DONE-WORKING)
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues(DONE-WORKING)
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.(DONE-WORKING)
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.(DONE-WORKING)

    areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
    response = []
    for area in areas:

        result = Venue.query.filter(Venue.state == area.state).filter(Venue.city == area.city).all()

        venue_data = []

        for venue in result:
            venue_data.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(db.session.query(Show).filter(Show.start_time > datetime.now()).all())
            })

            response.append({
                'city': area.city,
                'state': area.state,
                'venues': venue_data
            })

    return render_template('pages/venues.html', areas=response)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.(DONE-WORKING)
  # search for Hop should return "The Musical Hop".(DONE-WORKING)
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"(DONE-WORKING)
    search_term = request.form.get('search_term', '')
    result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
    count = len(result)
    response = {
        "count": count,
        "data": result
    }
    return render_template('pages/search_venues.html', results=response,
      search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id(DONE-WORKING)
  # TODO: replace with real venue data from the venues table, using venue_id (DONE-WORKING)
    venue = Venue.query.filter(Venue.id == venue_id).first()

    past = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
        Show.start_time < datetime.now()).join(Artist, Show.artist_id == Artist.id).add_columns(Artist.id, Artist.name,Artist.image_link,Show.start_time).all()
                                                                                                
    upcoming = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
        Show.start_time > datetime.now()).join(Artist, Show.artist_id == Artist.id).add_columns(Artist.id, Artist.name,Artist.image_link,Show.start_time).all()
                                                                                                
    upcoming_shows = []

    past_shows = []

    for i in upcoming:
        upcoming_shows.append({
            'artist_id': i[1],
            'artist_name': i[2],
            'image_link': i[3],
            'start_time': str(i[4])
        })

    for i in past:
        past_shows.append({
            'artist_id': i[1],
            'artist_name': i[2],
            'image_link': i[3],
            'start_time': str(i[4])
        })

    if venue is None:
        abort(404)

    response = {
        "id": venue.id,
        "name": venue.name,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "facebook_link": venue.facebook_link,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }
    return render_template('pages/show_venue.html', venue=response)
  

#  Create Venue(DONE-WORKING)
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        venue = Venue()
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        tmp_genres = request.form.getlist('genres')
        venue.genres = ','.join(tmp_genres)
        venue.facebook_link = request.form['facebook_link']
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occured. Venue ' +
                  request.form['name'] + ' Could not be listed!')
        else:
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using(DONE-WORKING)
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.(DONE-WORKING)
  def delete_venue(venue_id):
    try:
        venue_to_delete = Venue.query.filter(Venue.id == venue_id).one()
        venue_to_delete.delete()
        flask("Venue {0} has been deleted successfully".format(
            venue_to_delete[0]['name']))
    except NoResultFound:
        abort(404)
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that(UNABLE TO COMPLETE)
  # clicking that button delete it from the db then redirect the user to the homepage(UNABLE TO COMPLETE)
  return None

#  Artists(DONE-WORKING)
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database(DONE-WORKING)
    response = Artist.query.all()
    return render_template('pages/artists.html', artists=response)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.(DONE-WORKING)
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".(DONE-WORKING)
  # search for "band" should return "The Wild Sax Band".(DONE-WORKING)
  search_term = request.form['search_term']
  search = "%{}%".format(search_term)

  artists = Artist.query \
      .with_entities(Artist.id, Artist.name) \
      .filter(Artist.name.match(search)) \
      .all()

  data_artists = []
  for artist in artists:
      upcoming_shows = db.session \
              .query(Show) \
              .filter(Show.artist_id == artist.id) \
              .filter(Show.start_time > datetime.now()) \
              .all()

      data_artists.append({
          'id': artist.id,
          'name': artist.name,
          'num_upcoming_shows': len(upcoming_shows)
      })

  results = {
      'data': data_artists,
      'count': len(artists)
  }

  return render_template(
    'pages/search_artists.html',
    results=results,
    search_term=search_term
  )


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id(DONE-WORKING)
  # TODO: replace with real artist data from the artist table, using artist_id(DONE-WORKING)
  artist = Artist.query.filter(Artist.id == artist_id).first()

  past = db.session.query(Show).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id, Venue.name,Venue.image_link,Show.start_time).all()
      
  upcoming = db.session.query(Show).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id, Venue.name,Venue.image_link,Show.start_time).all()

  upcoming_shows = []

  past_shows = []

  for i in upcoming:
        upcoming_shows.append({
            'venue_id': i[1],
            'venue_name': i[2],
            'image_link': i[3],
            'start_time': str(i[4])
        })

  for i in past:
        past_shows.append({
            'venue_id': i[1],
            'venue_name': i[2],
            'image_link': i[3],
            'start_time': str(i[4])
        })

  if artist is None:
        abort(404)

  response = {
        "id": artist.id,
        "name": artist.name,
        "genres": [artist.genres],
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }
  return render_template('pages/show_artist.html', artist=response)

#  Update(DONE-WORKING)
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>(DONE-WORKING)
  artist = Artist.query.filter(Artist.id == artist_id).first()
  form = ArtistForm()
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)
  

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing(DONE-WORKING)
  # artist record with ID <artist_id> using the new attributes(DONE-WORKING)

  error = False
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  seeking_talent = True if 'seeking_talent' in request.form else False
  seeking_description = request.form['seeking_description']

  try:
        artist = Artist.query.get(artist_id)
        artist.name = name
        artist.city = city
        artist.state = state
        artist.phone = phone
        artist.genres = genres
        artist.image_link = image_link
        artist.facebook_link = facebook_link
        artist.seeking_talent = seeking_talent
        artist.seeking_description = seeking_description
        db.session.commit()
  except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
  finally:
        db.session.close()

  if error:
        abort(400)
        flash(
          'An error occurred. Artist '
          + name
          + ' could not be updated.',
          'danger'
        )
  if not error:
        flash(
          'Artist '
          + name
          + ' was successfully updated!',
          'success'
        )

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.filter(Venue.id == venue_id).first()
    form = VenueForm()
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.image_link.data = venue.image_link
    form.facebook_link.data = venue.facebook_link
   

    return render_template('forms/edit_venue.html', form=form, venue=venue)

  # TODO: populate form with values from venue with ID <venue_id>(DONE-WORKING)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
  # TODO: take values from the form submitted, and update existing(DONE-WORKING)
  # venue record with ID <venue_id> using the new attributes(DONE-WORKING)
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)

    error = False
    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        tmp_genres = request.form.getlist('genres')
        venue.genres = ','.join(tmp_genres)  # convert list to string
        venue.facebook_link = request.form['facebook_link']
        db.session.add(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        if error:
            flash('An error occurred. Venue ' +
                  request.form['name'] + ' could not be updated.')
        else:
            flash('Venue ' + request.form['name'] +
                  ' was successfully updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist(DONE-WORKING)
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead(DONE-WORKING)
  # TODO: modify data to be the data object returned from db insertion(DONE-WORKING)
  form_data = request.form
  artist = Artist()
  artist.name = form_data['name']
  artist.city = form_data['city']
  artist.state = form_data['state']
  artist.phone = form_data['phone']
  artist.genres = ';'.join(form_data.getlist('genres'))
  artist.image_link = form_data['image_link']
  artist.facebook_link = form_data['facebook_link']
  artist.website = form_data['website_link']
  artist.seeking_venue = True if form_data['seeking_venue']=='true' else False
  artist.seeking_description = form_data['seeking_description']
  db.session.add(artist)
  db.session.commit()
  print(form_data['genres'])
  # on successful db insert, flash success(DONE-WORKING)
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

  # on successful db insert, flash success(DONE-WORKING)
  # TODO: on unsuccessful db insert, flash an error instead.(DONE-WORKING)
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows(DONE-WORKING)
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    data = []

    shows = db.session \
        .query(
          Venue.name,
          Artist.name,
          Artist.image_link,
          Show.venue_id,
          Show.artist_id,
          Show.start_time
        ) \
        .filter(Venue.id == Show.venue_id, Artist.id == Show.artist_id)

    
    for show in shows:
        data.append({
          'venue_name': show[0],
          'artist_name': show[1],
          'artist_image_link': show[2],
          'venue_id': show[3],
          'artist_id': show[4],
          'start_time': str(show[5])
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False

    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    try:
        show = Show(
          artist_id=artist_id,
          venue_id=venue_id,
          start_time=start_time,
        )
        db.session.add(show)
        db.session.commit()
    except Exception:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
        flash(
          'An error occurred. Show could not be listed.',
          'danger'
        )
    if not error:
        flash(
          'Show was successfully listed!',
          'success'
        )

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
