"""
REST server views.

.. moduleauthor:: Martijn Vermaat <martijn@vermaat.name>

.. Licensed under the MIT license, see the LICENSE file.
"""


from flask import Blueprint, current_app, jsonify, request, url_for

from . import db
from .models import Activity, STATUS_CHOICES


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
@api.app_errorhandler(404)
def error_not_found(error):
    return jsonify(error={
            'code': 'not_found',
            'message': 'The requested entity could not be found'}), 404


@api.route('/')
def apiroot():
    api = {'status':     'ok',
           'version':    API_VERSION,
           'activities': url_for('.list_activities')}
    return jsonify(api=api)


@api.route('/activities', methods=['GET'])
def list_activities():
    """
    List activities.

    Example usage::

        curl -i http://127.0.0.1:5000/activities
    """
    return jsonify(activities=[{'service': activity.service,
                                'status':  activity.status,
                                'host':    activity.host,
                                'logged':  str(activity.logged)}
                               for activity in Activity.query])


@api.route('/activities/<int:activity_id>', methods=['GET'])
def view_activity(activity_id):
    """
    View activity.

    Example usage::

        curl -i http://127.0.0.1:5000/activities/2
    """
    activity = Activity.query.get_or_404(activity_id)
    return jsonify(activity={'service': activity.service,
                             'status':  activity.status,
                             'host':    activity.host,
                             'logged':  str(activity.logged)})


@api.route('/activities', methods=['POST'])
def add_activity():
    """
    Add activity.

    Example usage::

        curl -i -d 'service=database backup' -d 'key=XXXXX' http://127.0.0.1:5000/activities
    """
    data = request.json or request.form
    try:
        service = data['service']
    except KeyError:
        abort(400)
    status = data.get('status', 'ok')
    host = data.get('host')
    key = data.get('key')
    if status not in STATUS_CHOICES:
        abort(400)
    if key != current_app.config['API_KEY']:
        abort(403)
    activity = Activity(service, status, host)
    db.session.add(activity)
    db.session.commit()
    uri = url_for('.view_activity', activity_id=activity.id)
    response = jsonify(activity=uri)
    response.location = uri
    return response, 201
