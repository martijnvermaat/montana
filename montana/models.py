"""
Models backed by SQL using SQLAlchemy.

.. moduleauthor:: Martijn Vermaat <martijn@vermaat.name>

.. Licensed under the MIT license, see the LICENSE file.
"""


from datetime import datetime

from . import db


STATUS_CHOICES = ('ok', 'error')


class Service(db.Model):
    """
    Service.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    interval = db.Column(db.Interval)

    def __init__(self, name, interval=None):
        self.name = name
        self.interval = interval

    def __repr__(self):
        return 'Service(%r)' % self.name


class Event(db.Model):
    """
    Event.
    """
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    status = db.Column(db.Enum(*STATUS_CHOICES, name='status'))
    duration = db.Column(db.Interval)
    logged = db.Column(db.DateTime)

    service = db.relationship(Service, backref=db.backref('events', lazy='dynamic'))

    def __init__(self, service, status='ok', duration=None):
        self.service = service
        self.status = status
        self.duration = duration
        self.logged = datetime.now()

    def __repr__(self):
        return 'Event(%r, %r)' % (self.service, self.status)
