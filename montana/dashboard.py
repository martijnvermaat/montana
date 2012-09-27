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
    return render_template('index.html')
