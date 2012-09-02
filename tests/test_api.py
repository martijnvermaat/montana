"""
High-level REST API unit tests.

Todo: Look at http://packages.python.org/Flask-Testing/
"""


import json

from nose.tools import *

from montana import create_app, db


TEST_SETTINGS = {
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite://',
    'API_KEY': 'testing'
}


class TestApi():
    """
    High-level unit tests, using the REST API entry points of Montana.
    """
    def setup(self):
        """
        Run once before every test. Setup the test database.
        """
        self.app = create_app(TEST_SETTINGS)
        self.client = self.app.test_client()
        with self.app.test_request_context():
            db.create_all()
            db.session.commit()

    def teardown(self):
        """
        Run once after every test. Drop the test database.
        """
        with self.app.test_request_context():
            db.session.remove()
            db.drop_all()

    def test_root(self):
        """
        Dummy test.
        """
        r = self.client.get('/')
        assert_equal(r.status_code, 200)
        assert_equal(json.loads(r.data)['api']['status'], 'ok')

    def test_parameter_type(self):
        """
        Test request with incorrect parameter type.
        """
        r = self.client.get('/events/notanumber')
        assert_equal(r.status_code, 404)

    def test_incorrect_api_key(self):
        """
        Test event creation with incorrect api key.
        """
        data = {'service': 'mail backup',
                'status': 'ok',
                'host': 'laptop',
                'seconds': 148,
                'key': 'incorrect'}
        r = self.client.post('/events', data=data)
        assert_equal(r.status_code, 403)

    def test_missing_api_key(self):
        """
        Test event creation with missing api key.
        """
        data = {'service': 'mail backup',
                'status': 'ok',
                'host': 'laptop',
                'seconds': 148}
        r = self.client.post('/events', data=data)
        assert_equal(r.status_code, 403)

    def test_event(self):
        """
        Test event creation.
        """
        self._add_event()

    def test_events(self):
        """
        Test multiple event creation.
        """
        for _ in range(10):
            self._add_event()

        r = self.client.get('/events')
        assert_equal(r.status_code, 200)
        assert_equal(len(json.loads(r.data)['events']), 10)

    def _add_event(self, service='some service', status='ok', host='laptop', seconds=148):
        data = {'service': service,
                'status': status,
                'host': host,
                'seconds': seconds,
                'key': 'testing'}
        r = self.client.post('/events', data=data)
        assert_equal(r.status_code, 201)
        # Todo: Something better than the replace.
        event = r.headers['Location'].replace('http://localhost', '')

        r = self.client.get(event)
        assert_equal(r.status_code, 200)
        return event
