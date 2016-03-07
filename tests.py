from app import app, db, Url
from json import dumps
import unittest


class TestSomething(unittest.TestCase):
    def setUp(self):
        db.create_all()
        self.google_url = 'https://www.google.com/?gws_rd=ssl'

    def tearDown(self):
        db.session.remove()
        db.drop_all()

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
        self.assertEqual(response.data.decode(), url.to_json())

    def test_redirect(self):
        url = Url(self.google_url)
        db.session.add(url)
        db.session.commit()
        with app.test_client() as client:
            response = client.get('/{}'.format(url.short_url_hash))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, self.google_url)


if __name__ == '__main__':
    unittest.main()
