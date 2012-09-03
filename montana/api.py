"""
REST server views.

.. moduleauthor:: Martijn Vermaat <martijn@vermaat.name>

.. Licensed under the MIT license, see the LICENSE file.
"""


from datetime import date, timedelta

from flask import abort, Blueprint, current_app, jsonify, request, url_for

from . import db
from .models import Event, STATUS_CHOICES


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
    api = {'status':  'ok',
           'version': API_VERSION,
           'events':  url_for('.list_events')}
    return jsonify(api=api)


@api.route('/events', methods=['GET'])
def list_events():
    """
    List recent events per service/host.

    Example usage::

        curl -i http://127.0.0.1:5000/events
    """
    oldest = date.today() - timedelta(days=10)
    services = [{'service': service,
                 'host':    host,
                 'events':  [{'service':  event.service,
                              'status':   event.status,
                              'host':     event.host,
                              'duration': str(event.duration),
                              'logged':   str(event.logged)}
                           for event in Event.query.filter_by(service=service, host=host).filter(Event.logged >= oldest).order_by(Event.logged.desc())]}
              for service, host in Event.query.with_entities(Event.service, Event.host).distinct()]
    return jsonify(services=services, start=str(oldest), end=str(date.today()))


@api.route('/events/<int:event_id>', methods=['GET'])
def view_event(event_id):
    """
    View event.

    Example usage::

        curl -i http://127.0.0.1:5000/events/2
    """
    event = Event.query.get_or_404(event_id)
    return jsonify(event={'service':  event.service,
                          'status':   event.status,
                          'host':     event.host,
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
    try:
        service = data['service']
    except KeyError:
        abort(400)
    status = data.get('status', 'ok')
    host = data.get('host')
    try:
        duration = timedelta(seconds=int(data['seconds']))
    except KeyError, ValueError:
        duration = None
    key = data.get('key')
    if status not in STATUS_CHOICES:
        abort(400)
    if key != current_app.config['API_KEY']:
        abort(403)
    event = Event(service, status, host, duration)
    db.session.add(event)
    db.session.commit()
    uri = url_for('.view_event', event_id=event.id)
    response = jsonify(event=uri)
    response.location = uri
    return response, 201
