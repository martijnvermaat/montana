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
    return jsonify(services=[{'uri':      url_for('.view_service', service_id=service.id),
                              'service':  service.name,
                              'interval': str(service.interval),
                              'events':   url_for('.list_events', service_id=service.id)}
                             for service in Service.query])


@api.route('/services/<int:service_id>', methods=['GET'])
def view_service(service_id):
    """
    View service.

    Example usage::

        curl -i http://127.0.0.1:5000/services/2
    """
    service = Service.query.get_or_404(service_id)
    return jsonify(service={'uri':      url_for('.view_service', service_id=service.id),
                            'service':  service.name,
                            'interval': str(service.interval),
                            'events':   url_for('.list_events', service_id=service.id)})


@api.route('/services/<int:service_id>/events', methods=['GET'])
def list_events(service_id):
    """
    List recent events per service.

    Example usage::

        curl -i http://127.0.0.1:5000/services/2/events
    """
    service = Service.query.get_or_404(service_id)
    oldest = datetime.now() - timedelta(days=10)
    events = [{'uri':      url_for('.view_event', event_id=event.id),
               'service':  url_for('.view_service', service_id=service.id),
               'status':   event.status,
               'duration': str(event.duration),
               'logged':   str(event.logged)}
              for event in Event.query.filter_by(service=service).filter(Event.logged >= oldest).order_by(Event.logged.desc())]
    return jsonify(events=events, start=str(oldest), end=str(datetime.now()))


@api.route('/events/<int:event_id>', methods=['GET'])
def view_event(event_id):
    """
    View event.

    Example usage::

        curl -i http://127.0.0.1:5000/events/2
    """
    event = Event.query.get_or_404(event_id)
    return jsonify(event={'uri':      url_for('.view_event', event_id=event.id),
                          'service':  url_for('.view_service', service_id=event.service_id),
                          'status':   event.status,
                          'duration': str(event.duration),
                          'logged':   str(event.logged)})


@api.route('/events', methods=['POST'])
def add_event():
    """
    Add event.

    Example usage::

        curl -i -d 'service=database backup' -d 'key=XXXXX' http://127.0.0.1:5000/events
    """
    data = request.json or request.form

    key = data.get('key')
    if key != current_app.config['API_KEY']:
        abort(403)

    try:
        service_name = data['service']
    except KeyError:
        abort(400)

    status = data.get('status', 'ok')
    if status not in STATUS_CHOICES:
        abort(400)

    try:
        duration = timedelta(seconds=int(data['duration']))
    except KeyError, ValueError:
        duration = None

    try:
        interval = timedelta(seconds=int(data['interval']))
    except KeyError, ValueError:
        interval = None

    try:
        service = Service.query.filter_by(name=service_name).one()
        service.interval = interval
    except NoResultFound:
        service = Service(service_name, interval)
        db.session.add(service)

    event = Event(service, status, duration)
    db.session.add(event)
    db.session.commit()

    service_uri = url_for('.view_service', service_id=service.id)
    event_uri = url_for('.view_event', event_id=event.id)
    response = jsonify(service=service_uri, event=event_uri)
    response.location = event_uri
    return response, 201
