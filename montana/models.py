"""
Models backed by SQL using SQLAlchemy.

.. moduleauthor:: Martijn Vermaat <martijn@vermaat.name>

.. Licensed under the MIT license, see the LICENSE file.
"""


from datetime import datetime
import json

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


def load_fixture(handle):
    """
    Load json fixture from open filehandle.

    For an examples, see the 'fixtures' directory in the project root.
    """
    model_classes = {'montana.models.Service': Service,
                     'montana.models.Event': Event}

    # Evaluate 'special' string values. Currently the following patterns are
    # supported:
    # - 'instance:<model_class>:<primary_key>' is resolved to a model
    #   instance.
    # - 'date:<YYY>-<MM>-<DD>' is converted to a datetime.datetime instance.
    def evaluate(value):
        if isinstance(value, (str, unicode)):
            if value.startswith('instance:'):
                _, model, primary_key = value.split(':')
                return model_classes[model].query.get(primary_key)
            if value.startswith('date:'):
                return datetime.strptime(value.split(':')[1], '%Y-%m-%d')
        return value

    fixture = json.load(handle)
    model = model_classes[fixture['model']]

    for instance in fixture['instances']:
        args = [evaluate(arg) for arg in instance.get('args', [])]
        kwargs = dict((key, evaluate(value))
                      for key, value in instance.get('kwargs', {}).items())
        i = model(*args, **kwargs)
        for key, value in instance.get('props', {}).items():
            setattr(i, key, evaluate(value))
        db.session.add(i)

    db.session.commit()
