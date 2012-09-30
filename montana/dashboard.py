"""
Dashboard views for browsers.

.. moduleauthor:: Martijn Vermaat <martijn@vermaat.name>

.. Licensed under the MIT license, see the LICENSE file.
"""


from datetime import datetime, timedelta

from flask import Blueprint, render_template
from sqlalchemy.orm.exc import NoResultFound

from . import db
from .models import Event, Service, STATUS_CHOICES


dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/')
def index():
    def get_events(service):
        return [dict(logged=event.logged, status=event.status)
                for event in service.events.order_by(Event.logged.desc()).limit(10)]
    services = [dict(name=service.name, description=service.description, events=get_events(service))
                for service in Service.query.all()]
    return render_template('dashboard.html', services=services)
