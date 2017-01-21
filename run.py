#!/usr/bin/env python
"""Run the ltd-dasher app in development or production mode.

To run in development mode::

   ./run.py runserver

In production::

   export LTD_DASHER_PROFILE=production
   ./run.py run.py runserver

(Though in the Kubernetes deploy this should be run in uwsgi instead)

will run LTD Dasher with production configurations.

Other commands
--------------

./run.py shell
   A Python REPL with `dasher_app` available.

See config.py for associated configuration.
"""

import os

from flask_script import Manager

from app import create_app

environment = os.getenv('LTD_DASHER_PROFILE', 'development')
dasher_app = create_app(profile=environment)
manager = Manager(dasher_app)


@manager.shell
def make_shell_context():
    """Pre-populate the shell environment when running run.py shell."""
    return dict(app=dasher_app)


if __name__ == '__main__':
    manager.run()
