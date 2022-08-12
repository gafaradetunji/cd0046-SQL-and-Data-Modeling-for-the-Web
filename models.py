from flask_sqlalchemy import SQLAlchemy
from app import datetime

db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False, nullable=False)
    seeking_description = db.Column(db.String(120))
    venues = db.relationship('Show', backref = 'venue')


    def __repr__(self):
      return '< Venue: {self.id} {self.name} {self.city} {self.image_link} {self.state} {self.address} {self.phone} {self.facebook_link}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(),default=False, nullable=False)
    seeking_description = db.Column(db.String(120))
    artists = db.relationship('Show', backref = 'artist')

    def __repr__(self):
      return '< Artist: {self.id} {self.name} {self.city} {self.genres} {self.state} {self.phone} {self.image_link} {self.facebook_link}>'


class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  start_time = db.Column(db.DateTime(), default=datetime.today(),nullable=False)

  def __repr__(self):
        return '<Show {self.artist_id}, {self.venue_id}>'