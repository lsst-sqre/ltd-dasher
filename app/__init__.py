"""Application initialization.

Applies configurations, creates the DB schema (if necessary) and registers
all HTTP routes.

Copyright 2016-2017 Association of Universities for Research in Astronomy, Inc.
Copyright 2014 Miguel Grinberg.
"""

from flask import Flask
from structlog import get_logger

from .config import config
from . import dashboard  # noqa: F401


# Application version; should match Git tags and docker tags
__version__ = '0.1.0-rc.1'


def create_app(profile='production'):
    """Create a Flask application instance.

    This is called by a runner script, such as /run.py.
    """
    app = Flask(__name__)

    # apply configuration
    app.config.from_object(config[profile])
    # init_app configuration hook is used for logging/structlog setup
    config[profile].init_app(app)

    logger = get_logger()
    logger.debug('Starting LTD Dasher')

    # register blueprints
    from .routes import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix=None)

    return app
