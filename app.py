from config import Config
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from urllib.parse import urlparse
from hashlib import sha1
from base64 import urlsafe_b64encode

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


class Url(db.Model):
    short_url_hash_size = 6
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.Text)
    short_url_hash = db.Column(db.String(short_url_hash_size))
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


@app.route('/urls', methods=['POST'])
def post_url():
    data = request.get_json()
    url = Url(data['url'])
    db.session.add(url)
    db.session.commit()
    return jsonify({'url': url.long_url}), 201

if __name__ == '__main__':
    db.create_all()
    app.run()
