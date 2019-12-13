#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import os
from datetime import datetime
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
UPLOAD_FOLDER = 'static/uploads';
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif', 'jpeg'])

app = Flask(__name__, static_folder='static')
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres@localhost:5432/fyyur'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', back_populates='venue', cascade='all,delete')
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue = db.relationship('Venue', back_populates='shows', lazy=True)
    artist = db.relationship('Artist', backref='shows', lazy=True)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  all_venues = Venue.query.all()
  cities = set()

  for venue in all_venues:
      cities.add((venue.city, venue.state))
  
  data = []
  for city in cities:
      city_venues = db.session.query(Venue.id, Venue.name).filter_by(city=city[0], state=city[1])
      venue_data = {
        "city": city[0],
        "state": city[1],
        "venues": city_venues
      }
      data.append(venue_data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  result= db.session.query(Venue.id, Venue.name).filter(Venue.name.ilike('%'+search_term+'%'))

  response={
    "count": result.count(),
    "data": result
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  shows_data = upcoming_or_past(venue.shows)
  data = {
    'id': venue.id,
    'name': venue.name,
    'genres': venue.genres,
    'address': venue.address,
    'city': venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    "image_link": venue.image_link,
    'upcoming_shows_count': shows_data['upcoming_shows_count'],
    'upcoming_shows': shows_data['upcoming_shows'],
    'past_shows_count': shows_data['past_shows_count'],
    'past_shows': shows_data['past_shows']
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
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error = False
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    address = request.form.get('address', '')
    phone = request.form.get('phone', '')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link', '')
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print('Error happened')
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + name + ' could not be listed.')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  result= db.session.query(Artist.id, Artist.name).filter(Artist.name.ilike('%'+search_term+'%'))

  response={
    "count": result.count(),
    "data": result
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  show_data = upcoming_or_past(artist.shows)
  data = {
    'id': artist.id,
    'name': artist.name,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'genres': artist.genres,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'website': artist.website,
    'image_link': artist.image_link,
    'facebook_link': artist.facebook_link,
    'upcoming_shows_count': show_data['upcoming_shows_count'],
    'upcoming_shows': show_data['upcoming_shows'],
    'past_shows_count': show_data['past_shows_count'],
    'past_shows': show_data['past_shows']
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.seeking_description.data = artist.seeking_description
  form.website.data = artist.website
  form.facebook_link.data = artist.facebook_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.phone = request.form.get('phone', '')
    artist.genres = request.form.getlist('genres')
    artist.seeking_description = request.form.get('seeking_description', '')
    artist.website = request.form.get('website', '')
    artist.facebook_link = request.form.get('facebook_link', '')

    if artist.seeking_description:
        artist.seeking_venue = True
    else:
        artist.seeking_venue = False

    file = ''
    filename = ''
    image_path = ''
    print(request.files['image_link'])
    if request.files['image_link']:
        file = request.files['image_link']
        if file.filename:
          filename = file.filename

    if file and is_valid_image(filename):
        filename = secure_filename(filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)

    artist.image_link = image_path
        
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.seeking_description.data = venue.seeking_description
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name', '')
    venue.city = request.form.get('city', '')
    venue.state = request.form.get('state', '')
    venue.address = request.form.get('address', '')
    venue.phone = request.form.get('phone', '')
    venue.genres = request.form.getlist('genres')
    venue.seeking_description = request.form.get('seeking_description', '')
    venue.website = request.form.get('website', '')
    venue.facebook_link = request.form.get('facebook_link', '')

    if venue.seeking_description:
        venue.seeking_talent = True
    else:
        venue.seeking_talent = False

    file = ''
    filename = ''
    image_path = ''
    print(request.files)
    if request.files['image_link']:
        file = request.files['image_link']
        if file.filename:
          filename = file.filename

    if file and is_valid_image(filename):
        filename = secure_filename(filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(image_path)
    venue.image_link = image_path

    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
    
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
  error = False
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link', '')
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link)

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  
  if not error:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
 
  shows = Show.query.all()

  data = []
  for show in shows:
    detail = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y/%m/%d')
    }
    data.append(detail)
  
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
  error = False
  try:
    artist_id = request.form.get('artist_id', '')
    venue_id = request.form.get('venue_id', '')
    start_time = request.form.get('start_time', '')
    artist = Artist.query.get(artist_id)
    venue = Venue.query.get(venue_id)
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time, venue=venue, artist=artist)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback();
  finally:
    db.session.close()

  if not error:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  else: 
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.')
  return render_template('pages/home.html')

# classify shows by time
def upcoming_or_past(shows):
    data = {}
    upcoming_shows = []
    past_shows = []
    for show in shows:
        if show.start_time > datetime.now():
            show.start_time = show.start_time.isoformat()
            upcoming_shows.append(show)
        else:
            show.start_time = show.start_time.isoformat()
            past_shows.append(show)
    data['upcoming_shows'] = upcoming_shows
    data['upcoming_shows_count'] = len(upcoming_shows)
    data['past_shows'] = past_shows
    data['past_shows_count'] = len(past_shows)

    return data

# Check an image is valid
def is_valid_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
