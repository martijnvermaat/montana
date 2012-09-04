#!/usr/bin/env python


# Using an in-memory SQLite database should only be done with a static
# connection pool such that all threads share the same connection.
#
# This is implemented in this pull request:
#     https://github.com/mitsuhiko/flask-sqlalchemy/pull/81
#
# Until it is merged, we monkey patch Flask-SQLAlchemy.
from sqlalchemy.pool import StaticPool
from flask.ext.sqlalchemy import SQLAlchemy
_apply_driver_hacks = SQLAlchemy.apply_driver_hacks
def apply_driver_hacks(self, app, info, options):
    if info.drivername == 'sqlite' and info.database in (None, '', ':memory:'):
        options['poolclass'] = StaticPool
        options['connect_args'] = {'check_same_thread': False}
        try:
            del options['pool_size']
        except KeyError:
            pass
    _apply_driver_hacks(self, app, info, options)
SQLAlchemy.apply_driver_hacks = apply_driver_hacks


from sqlalchemy.engine.url import make_url
from montana import create_app, db


app = create_app()

# If we have an in-memory database, setup the schema first.
info = make_url(app.config['SQLALCHEMY_DATABASE_URI'])
if info.drivername == 'sqlite' and info.database in (None, '', ':memory:'):
    print 'Setting up in-memory database...'
    with app.test_request_context():
        db.create_all()
        if True:
            # Change the condition to have some fake data inserted.
            from datetime import datetime, timedelta
            from montana.models import Event, Service
            service = Service('mail backup martijn', timedelta(days=1))
            event = Event(service, 'ok')
            event.logged = datetime.now()
            db.session.add(event)
            event = Event(service, 'ok')
            event.logged = datetime.now() - timedelta(days=1)
            db.session.add(event)
            event = Event(service, 'error')
            event.logged = datetime.now() - timedelta(days=2)
            db.session.add(event)
            event = Event(service, 'ok')
            event.logged = datetime.now() - timedelta(days=3)
            db.session.add(event)
            event = Event(service, 'ok')
            event.logged = datetime.now() - timedelta(days=3)
            db.session.add(event)
            event = Event(service, 'ok')
            event.logged = datetime.now() - timedelta(days=5)
            db.session.add(event)
            event = Event(service, 'ok')
            event.logged = datetime.now() - timedelta(days=6)
            db.session.add(event)
            service = Service('mail backup rosanne', timedelta(days=1))
            event = Event(service, 'ok')
            event.logged = datetime.now()
            db.session.add(event)
            event = Event(service, 'ok')
            event.logged = datetime.now() - timedelta(days=1)
            db.session.add(event)
            event = Event(service, 'ok')
            event.logged = datetime.now() - timedelta(days=2)
            db.session.add(event)
            event = Event(service, 'ok')
            event.logged = datetime.now() - timedelta(days=3)
            db.session.add(event)
            event = Event(service, 'ok')
            event.logged = datetime.now() - timedelta(days=4)
            db.session.add(event)
            event = Event(service, 'ok')
            event.logged = datetime.now() - timedelta(days=5)
            db.session.add(event)
            service = Service('mail backup rosanne 2', timedelta(days=1))
            event = Event(service, 'ok')
            event.logged = datetime.now() - timedelta(days=2)
            db.session.add(event)
            event = Event(service, 'ok')
            event.logged = datetime.now() - timedelta(days=3)
            db.session.add(event)
            event = Event(service, 'ok')
            event.logged = datetime.now() - timedelta(days=4)
            db.session.add(event)
            db.session.commit()
    print 'Done setting up in-memory database'

app.run()
