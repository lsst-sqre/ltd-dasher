"""Application initialization.

Applies configurations, creates the DB schema (if necessary) and registers
all HTTP routes.

Copyright 2016-2017 Association of Universities for Research in Astronomy, Inc.
Copyright 2014 Miguel Grinberg.
"""

from flask import Flask

from .config import config


def create_app(profile='production'):
    """Create a Flask application instance.

    This is called by a runner script, such as /run.py.
    """
    app = Flask(__name__)

    # apply configuration
    app.config.from_object(config[profile])
    config[profile].init_app(app)

    # register blueprints
    from .routes import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix=None)

    return app
