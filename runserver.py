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
        db.session.commit()
    print 'Done setting up in-memory database'

app.run()
