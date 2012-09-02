"""
Montana, a simple event monitor.

.. moduleauthor:: Martijn Vermaat <martijn@vermaat.name>

.. Licensed under the MIT license, see the LICENSE file.
"""


from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy


# On the event of a new release, we update the __version_info__ and __date__
# package globals and set RELEASE to True.
# Before a release, a development version is denoted by a __version_info__
# ending with a 'dev' item. Also, RELEASE is set to False (indicating that
# the __date__ value is to be ignored).
#
# We follow a versioning scheme compatible with setuptools [1] where the
# __version_info__ variable always contains the version of the upcomming
# release (and not that of the previous release), post-fixed with a 'dev'
# item. Only in a release commit, this 'dev' item is removed (and added
# again in the next commit).
#
# [1] http://peak.telecommunity.com/DevCenter/setuptools#specifying-your-project-s-version

RELEASE = False

__version_info__ = ('0', '1', 'dev')
__date__ = '2 Sep 2012'


__version__ = '.'.join(__version_info__)
__author__ = 'Martijn Vermaat'
__contact__ = 'martijn@vermaat.name'
__homepage__ = 'http://martijn.vermaat.name'


db = SQLAlchemy()


def create_app(settings=None):
    """
    Create a Flask instance for Montana. Configuration settings are read from
    a file specified by the ``MONTANA_SETTINGS`` environment variable, if it
    exists.

    :kwarg settings: Dictionary of configuration settings. These take
        precedence over settings read from the file pointed to by the
        ``MONTANA_SETTINGS`` environment variable.
    :type settings: dict

    :return: Flask application instance.
    """
    app = Flask(__name__)

    app.config.from_object('montana.default_settings')
    app.config.from_envvar('MONTANA_SETTINGS', silent=True)
    if settings:
        app.config.update(settings)
    db.init_app(app)

    from .api import api
    app.register_blueprint(api, url_prefix='/api')

    # There's really no need for the frontend to go through Flask, it's just
    # static files. But to ease deployment we have it in here for the moment.
    @app.route('/')
    def index():
        return render_template('index.html')

    return app
