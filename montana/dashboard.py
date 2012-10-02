"""
Dashboard views for browsers.

.. moduleauthor:: Martijn Vermaat <martijn@vermaat.name>

.. Licensed under the MIT license, see the LICENSE file.
"""


from datetime import datetime

from flask import Blueprint, render_template
from sqlalchemy.orm.exc import NoResultFound

from . import db
from .models import Event, Service, STATUS_CHOICES


dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/')
def index():
    def get_events(service):
        return
    services = []
    for service in Service.query.all():
        events = [dict(logged=event.logged, status=event.status)
                  for event in service.events.order_by(Event.logged.desc()).limit(10)]
        try:
            last_event = events[0]['logged']
        except IndexError:
            last_event = 'never'
        services.append(dict(name=service.name,
                             description=service.description,
                             events=events,
                             last_event=last_event))
    return render_template('dashboard.html', services=services)


@dashboard.app_template_filter('datetime')
def format_datetime(dt, format='full'):
    if format == 'full':
        format = '%A, %B {day:d} at %H:%M'.format(day=dt.day)
    elif format == 'medium':
        format = '%A, %B {day:d} %Y at %H:%M'.format(day=dt.day)
    return dt.strftime(format)


@dashboard.app_template_filter('timedelta')
def format_timedelta(dt, now=None):
    # Based on http://code.activestate.com/recipes/576880-convert-datetime-in-python-to-user-friendly-repres/#c1
    if not now:
        now = datetime.now()
    delta = now - dt

    years = delta.days // 365
    months = delta.days // 30 - (12 * years)
    if years > 0:
        days = 0
    else:
        days = delta.days % 30
    hours = delta.seconds // 3600
    minutes = delta.seconds // 60 - (60 * hours)
    if hours > 0:
        seconds = 0
    else:
        seconds = delta.seconds % 60

    for period, value in zip(('year', 'month', 'day', 'hour', 'minute', 'second'),
                             (years, months, days, hours, minutes, seconds)):
        if value:
            if value > 1:
                period += 's'
            return '%s %s ago' % (value, period)

    return 'just now'
