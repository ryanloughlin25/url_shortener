from config import Config
from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from urllib.parse import urlparse
from hashlib import sha1
from base64 import urlsafe_b64encode
from json import dumps
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError, InvalidRequestError

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


class Url(db.Model):
    short_url_hash_size = 6
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.Text)
    short_url_hash = db.Column(db.String(short_url_hash_size), unique=True)
    domain = db.Column(db.Text)
    number_of_visits = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, long_url):
        self.long_url = long_url
        self.generate_short_url_hash()
        self.domain = urlparse(long_url).netloc
        self.number_of_visits = 0
        self.created_at = self.updated_at = datetime.utcnow()

    def generate_short_url_hash(self):
        self.short_url_hash = urlsafe_b64encode(
            sha1(self.long_url.encode('utf-8')).digest()
        ).decode()[:Url.short_url_hash_size]

    def serialize(self):
        return {
            'longUrl': self.long_url,
            'shortUrlHash': self.short_url_hash,
            'domain': self.domain,
            'numberOfVisits': self.number_of_visits,
        }

def select_url(short_url_hash):
    url = Url.query.filter_by(short_url_hash=short_url_hash).first()
    return url

@app.route('/<short_url_hash>', methods=['GET'])
def redirect_to_existing_url(short_url_hash):
    url = select_url(short_url_hash)
    if url:
        url.number_of_visits += 1
        db.session.commit()
        return redirect(url.long_url, code=302)
    else:
        return "url not found", 404

@app.route('/urls/<short_url_hash>', methods=['GET'])
def get_url(short_url_hash):
    url = select_url(short_url_hash)
    if url:
        return dumps(url.serialize()), 200
    else:
        return "url not found", 404

@app.route('/urls', methods=['GET'])
def search_urls():
    urls = Url.query.order_by(Url.created_at.desc()).limit(100).all()
    return dumps([url.serialize() for url in urls]), 200

@app.route('/urls/popular_domains', methods=['GET'])
def popular_domains():
    results = Url.query.with_entities(
        Url.domain,
        func.sum(Url.number_of_visits).label('visits')
    ).group_by(Url.domain).order_by('"visits" DESC').limit(10)
    return dumps([
        {
            'domain': result[0],
            'numberOfVisits': result[1],
        } for result in results
    ]), 200

@app.route('/urls', methods=['POST'])
def post_url():
    data = request.get_json()
    if data is None:
        return "POST to /urls must include json data with a 'url' property", 415
    elif 'url' not in data:
        return "missing parameter 'url'", 422
    url = Url(data['url'])
    db.session.add(url)
    try:
        db.session.commit()
    except (IntegrityError, InvalidRequestError):
        db.session.rollback()
        return dumps(select_url(url.short_url_hash).serialize()), 409
    else:
        return dumps(url.serialize()), 201

if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.run()
