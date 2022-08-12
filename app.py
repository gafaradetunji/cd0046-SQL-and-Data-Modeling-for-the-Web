#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
from typing import final
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from models import db, Artist, Venue, Show
from flask_migrate import Migrate
import re
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  data = []
  venues = Venue.query.all()
  for area in Venue.query.distinct(Venue.city, Venue.state).all():
      data.append({
          'city': area.city,
          'state': area.state,
          'venues': [{
            'id': venue.id,
            'name': venue.name,
          } for venue in venues if
            venue.city == area.city and venue.state == area.state]
      })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
   search_param = request.form.get('search_term', '')
   data = []
   queries_param = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_param}%')).all()

   for queries in queries_param:
    num_upcoming_shows = len(Venue.query.join(Show).filter(Show.start_time > datetime.now()),(Show.venue_id == queries.id).all())
    data.append({
          'id': queries.id,
          'name': queries.name,
          'num_upcoming_shows': num_upcoming_shows
    })
   num_venues = len(queries_param)
   response = {
      'count': num_venues,
        'data': data,
    }
   return render_template('pages/search_venues.html', results=response, search=search_param)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

    venue = Venue.query.get(venue_id)

    upcoming = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(
        Show.start_time <= datetime.now()).all()
    past = \
        db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(
            Show.start_time > datetime.now()).all()

    upcoming_shows = []
    past_shows = []

    for show in past:
        past_shows.append({
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': format_datetime(str(show.start_time))
        })

    for show in upcoming:
      upcoming_shows.append({
          'artist_id': show.artist_id,
          'artist_name': show.artist.name,
          'artist_image_link': show.artist.image_link,
          'start_time': format_datetime(str(show.start_time))
    })

    data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres.split(','),
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website_link": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
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
  form = VenueForm()
  if form.validate_on_submit():
    try:
      venue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres = form.genres.data,
        image_link = form.image_link.data,
        facebook_link = form.facebook_link.data,
        website_link = form.website_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(venue)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
      print(e)
      db.session.rollback()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    
    finally:
      db.session.close()
  else:
    return render_template('forms/new_venue.html', form=form)
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  try:
    db.session.query(Venue).filter_by(venue_id=venue_id).delete()
    db.session.commit()
    flash(Venue.name + 'was successfully deleted!')
  except:
     flash('An error occurred.' + Venue.name + 'could not be deleted.')
  finally:
    db.session.close()
  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
 
  return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # search = request.form.get('search_term', '')
  # artist = Artist.query.all()


  search_param = request.form.get('search_term', '')
  queries_param = db.session.query(Artist).filter(Artist.name.like('%' + search_param + '%')).all()
  data = []
 
  for queries in queries_param:
    num_upcoming_shows = len(Artist.query.join(Show).filter(Show.start_time > datetime.now()),(Show.artist_id == queries.id).all())
    data.append({
          'id': queries.id,
          'name': queries.name,
          'num_upcoming_shows': num_upcoming_shows
    })
  num_artist = len(queries_param)
  response = {
    'count': num_artist,
      'data': data,
  }

  return render_template('pages/search_artists.html', results=response, search=search_param)
   

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = db.session.query(Artist).get(artist_id)

  past = db.session.query(Show).join(Venue).filter(Show.artist_id == artist.id).filter(
      Show.start_time < datetime.now()).all()
  upcoming = db.session.query(Show).join(Venue).filter(Show.artist_id == artist.id).filter(
      Show.start_time >= datetime.now()).all()

  past = []
  upcoming = []

  for show in past:
      past.append({
          'venue_id': show.venue_id,
          'venue_name': show.venue.name,
          'artist_image_link': show.venue.image_link,
          'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
  })

  for show in upcoming:
      upcoming.append({
          'venue_id': show.venue_id,
          'venue_name': show.venue.name,
          'artist_image_link': show.venue.image_link,
          'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S')
  })

  data = {
      "id": artist.id,
      "name": artist.name,
      "genres": (artist.genres).split(','),
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website_link": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past,
      "upcoming_shows": upcoming,
      "past_shows_count": len(past),
      "upcoming_shows_count": len(upcoming),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.genres.data = artist.genres.split(',')
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website_link
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  if form.validate_on_submit():
    try:
      artist.name = form.name.data
      artist.genres = ','.join(form.genres.data)
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.website_link = form.website_link.data
      artist.facebook_link = form.facebook_link.data
      artist.image_link = form.image_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data

      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
    finally:
      db.session.close()
  else:
    return render_template('forms/edit_artist.html', form=form, artist=artist)

  return redirect(url_for('show_artist',artist=artist))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.genres.data = venue.genres.split(',')
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  
  if form.validate_on_submit():
    try:
      venue.name = form.name.data
      venue.genres = ','.join(form.genres.data)
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.address = form.address.data
      venue.website = form.website_link.data
      venue.facebook_link = form.facebook_link.data
      venue.image_link = form.image_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data

      db.session.commit()

      flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    finally:
      db.session.close()
  else:
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  print(form.name.data)
 
  try:venue_idvenue_id
      artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      website_link = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
      )
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
    print(e)
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  all_shows = db.session.query(Show).join(Artist).join(Venue).all()
  data = []

  for show in all_shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
      })

  return render_template('pages/shows.html', shows= data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  try:
   if form.validate_on_submit():
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as e:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., 
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
