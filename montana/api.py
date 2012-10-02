"""
REST server views.

.. moduleauthor:: Martijn Vermaat <martijn@vermaat.name>

.. Licensed under the MIT license, see the LICENSE file.
"""


from datetime import datetime, timedelta

from flask import abort, Blueprint, current_app, jsonify, request, url_for
from sqlalchemy.orm.exc import NoResultFound

from . import db
from .models import Event, Service, STATUS_CHOICES


API_VERSION = 1


api = Blueprint('api', __name__)


@api.errorhandler(400)
def error_bad_request(error):
    return jsonify(error={
            'code': 'bad_request',
            'message': 'The request could not be understood due to malformed syntax'}), 400


@api.errorhandler(403)
def error_forbidden(error):
    return jsonify(error={
            'code': 'forbidden',
            'message': 'Not allowed to make this request'}), 403


@api.errorhandler(404)
def error_not_found(error):
    return jsonify(error={
            'code': 'not_found',
            'message': 'The requested entity could not be found'}), 404


@api.route('/')
def apiroot():
    api = {'status':   'ok',
           'version':  API_VERSION,
           'services': url_for('.list_services')}
    return jsonify(api=api)


@api.route('/services', methods=['GET'])
def list_services():
    """
    List services.

    Example usage::

        curl -i http://127.0.0.1:5000/services
    """
    return jsonify(services=[{'name':        service.name,
                              'description': service.description}
                             for service in Service.query])


@api.route('/services', methods=['POST'])
def add_service():
    """
    Add (or edit) service.

    Example usage::

        curl -i -d 'name=db-backup' -d 'description=Database backup' -d 'key=XXXXX' http://127.0.0.1:5000/services
    """
    data = request.json or request.form

    key = data.get('key') or None
    if key != current_app.config['API_KEY']:
        abort(403)

    try:
        name = data['name']
    except KeyError:
        abort(400)

    service = Service.query.get(name)
    if not service:
        service = Service(name)
        db.session.add(service)

    description = data.get('description')
    if description:
        service.description = description

    db.session.commit()

    response = jsonify(status='Successfully added service')
    return response, 201


@api.route('/events', methods=['POST'])
def add_event():
    """
    Add event.

    Example usage::

        curl -i -d 'service=db-backup' -d 'key=XXXXX' http://127.0.0.1:5000/events
    """
    data = request.json or request.form

    key = data.get('key')
    if key != current_app.config['API_KEY']:
        abort(403)

    try:
        service_name = data['service']
    except KeyError:
        abort(400)

    status = data.get('status', 'success')
    if status not in STATUS_CHOICES:
        abort(400)

    service = Service.query.get(service_name)
    if not service:
        service = Service(service_name)
        db.session.add(service)

    description = data.get('description')
    if description:
        service.description = description

    event = Event(service, status)
    db.session.add(event)
    db.session.commit()

    response = jsonify(status='Successfully added event')
    return response, 201
