"""
Models backed by SQL using SQLAlchemy.

.. moduleauthor:: Martijn Vermaat <martijn@vermaat.name>

.. Licensed under the MIT license, see the LICENSE file.
"""


from datetime import datetime

from . import db


STATUS_CHOICES = ('success', 'failure')


class Service(db.Model):
    """
    Service.
    """
    name = db.Column(db.String(50), primary_key=True)
    description = db.Column(db.String(200))

    def __init__(self, name, description=None):
        self.name = name
        self.description = description or name

    def __repr__(self):
        return '<Service %s>' % self.name


class Event(db.Model):
    """
    Event.
    """
    service_name = db.Column(db.Integer, db.ForeignKey('service.name'), primary_key=True)
    logged = db.Column(db.DateTime, primary_key=True)
    status = db.Column(db.Enum(*STATUS_CHOICES, name='status'))

    service = db.relationship(Service, backref=db.backref('events', lazy='dynamic'))

    def __init__(self, service, status='success'):
        self.service = service
        self.logged = datetime.now()
        self.status = status

    def __repr__(self):
        return '<Event %s, %s, %s>' % (self.service_name, self.status, self.logged)
