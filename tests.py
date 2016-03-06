from app import app, db, Url
from json import dumps
import unittest


class TestSomething(unittest.TestCase):
    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_post_url(self):
        self.assertEqual(Url.query.all(), [])
        with app.test_client() as client:
            response = client.post(
                '/urls',
                data=dumps({'url': 'https://www.google.com/?gws_rd=ssl'}),
                content_type='application/json',
            )
        self.assertEqual(response.status_code, 201)
        url = Url.query.first()
        self.assertEqual(url.domain, 'www.google.com')
        self.assertEqual(url.short_url_hash, 'NzJqKe')

if __name__ == '__main__':
    unittest.main()
