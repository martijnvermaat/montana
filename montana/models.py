"""
Models backed by SQL using SQLAlchemy.

.. moduleauthor:: Martijn Vermaat <martijn@vermaat.name>

.. Licensed under the MIT license, see the LICENSE file.
"""


from datetime import datetime

from . import db


STATUS_CHOICES = {'ok', 'error'}


class Activity(db.Model):
    """
    Activity.
    """
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(200))
    status = db.Column(db.Enum(*STATUS_CHOICES, name='status'))
    host = db.Column(db.String(200))
    logged = db.Column(db.DateTime)

    def __init__(self, service, status='ok', host=None):
        self.service = service
        self.status = status
        self.host = host
        self.logged = datetime.now()

    def __repr__(self):
        return 'Activity(%r, %r, %r)' % (self.service, self.status, self.host)
