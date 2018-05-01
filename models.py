from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

import geocoder
import urllib3
from urllib.parse import urljoin
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(120), unique = True)
    pwdhash = db.Column(db.String(54))

    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.email = email.lower()
        self.set_password(password)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

class Place(object):

    def meters_to_walking_time(self, meters):
        return int(meters / 80)

    def wiki_path(self, slug):
        return urljoin("http://en.wikipedia.org/wiki/", slug.replace(' ', '_'))

    def address_to_latlng(self, address):
        g = geocoder.google(address)
        print(g.latlng)
        return g.latlng

    def query(self, address):
        lat, lng = self.address_to_latlng(address)
        return lat, lng

    def get_places(self, lat, lng):
        http = urllib3.PoolManager()

        query_url = 'https://en.wikipedia.org//w/api.php?action=query&format=json&list=geosearch&gscoord={}%7C{}&gsradius=10000&gslimit=10'.format(lat, lng)
        response = http.request('GET', query_url)
        data = response.data
        data = json.loads(data)
        print (data)

        places = []
        for d in data.get("query").get("geosearch"):
            name = d.get("title")
            meters = d.get("dist")
            lat = d.get("lat")
            lng = d.get("lon")

            wiki_url = self.wiki_path(name)
            walking_time = self.meters_to_walking_time(meters)

            d = {
                'name': name,
                'url': wiki_url,
                'time': walking_time,
                'lat': lat,
                'lng': lng,
            }

            places.append(d)

        return places
