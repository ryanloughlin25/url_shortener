from app import app, db, Url
from json import dumps, loads
import unittest
from string import ascii_lowercase
from random import sample


class TestUrlShortener(unittest.TestCase):
    def setUp(self):
        db.create_all()
        self.google_url = 'https://www.google.com/?gws_rd=ssl'

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def get_random_url(self):
        return 'http://www.{}.com'.format(''.join(sample(ascii_lowercase, 5)))


class TestValidRequests(TestUrlShortener):
    def test_post_url(self):
        self.assertEqual(Url.query.all(), [])
        with app.test_client() as client:
            response = client.post(
                '/urls',
                data=dumps({'url': self.google_url}),
                content_type='application/json',
            )
        self.assertEqual(response.status_code, 201)
        url = Url.query.first()
        self.assertEqual(url.domain, 'www.google.com')
        self.assertEqual(url.short_url_hash, 'NzJqKe')

    def test_get_url(self):
        url = Url(self.google_url)
        db.session.add(url)
        db.session.commit()
        with app.test_client() as client:
            response = client.get('/urls/{}'.format(url.short_url_hash))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), dumps(url.serialize()))

    def test_redirect(self):
        url = Url(self.google_url)
        db.session.add(url)
        db.session.commit()
        with app.test_client() as client:
            response = client.get('/{}'.format(url.short_url_hash))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, self.google_url)

    def test_number_of_vists(self):
        url = Url(self.google_url)
        db.session.add(url)
        db.session.commit()
        for i in range(1, 5):
            with app.test_client() as client:
                client.get('/{}'.format(url.short_url_hash))
            url = Url.query.filter_by(short_url_hash=url.short_url_hash).first()
            self.assertEqual(url.number_of_visits, i)

    def test_recent_urls(self):
        random_urls = [Url(self.get_random_url()) for _ in range(200)]
        for url in random_urls:
            db.session.add(url)
            db.session.commit()
        with app.test_client() as client:
            response = client.get('/urls')
        urls = loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        for url, random_url in zip(urls, random_urls[-1:-100]):
            self.assertEqual(url['longUrl'], random_url.long_url)

    def test_popular_domains(self):
        random_urls = [Url(self.get_random_url()) for _ in range(15)]
        for index, url in enumerate(random_urls):
            db.session.add(url)
            db.session.commit()
            for _ in range(index):
                with app.test_client() as client:
                    client.get('/{}'.format(url.short_url_hash))
        with app.test_client() as client:
            response = client.get('/urls/popular_domains')
        urls = loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(urls[0]['numberOfVisits'], 14)
        for url, random_url in zip(urls, random_urls[-1:-10]):
            self.assertEqual(url['longUrl'], random_url.long_url)


class TestInvalidRequests(TestUrlShortener):
    def test_get_invalid_url(self):
        url = Url(self.google_url)
        with app.test_client() as client:
            response = client.get('/urls/{}'.format(url.short_url_hash))
        self.assertEqual(response.status_code, 404)

    def test_get_invalid_url_redirect(self):
        url = Url(self.google_url)
        with app.test_client() as client:
            response = client.get('/{}'.format(url.short_url_hash))
        self.assertEqual(response.status_code, 404)

    def test_post_url_without_json(self):
        self.assertEqual(Url.query.all(), [])
        with app.test_client() as client:
            response = client.post('/urls')
        self.assertEqual(response.status_code, 415)
        url = Url.query.first()
        self.assertIsNone(url)

    def test_post_url_invalid_json(self):
        self.assertEqual(Url.query.all(), [])
        self.assertEqual(Url.query.all(), [])
        with app.test_client() as client:
            response = client.post(
                '/urls',
                data=dumps({'a': 'b', 'c': 'd'}),
                content_type='application/json',
            )
        self.assertEqual(response.status_code, 422)
        url = Url.query.first()
        self.assertIsNone(url)

if __name__ == '__main__':
    unittest.main()
