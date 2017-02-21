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


@manager.command
def render():
    """Test rendering pipeline for development."""
    import app

    test_dir = '_build'
    cache_dir = os.path.join(test_dir, '_cache')

    product_data = app.dashboard.loaders.load_dataset_with_caching(
        cache_dir, 'sqr-013', 'product')
    edition_data = app.dashboard.loaders.load_dataset_with_caching(
        cache_dir, 'sqr-013', 'editions')
    build_data = app.dashboard.loaders.load_dataset_with_caching(  # noqa: F841
        cache_dir, 'sqr-013', 'builds')

    page_data = app.dashboard.render.render_edition_dashboard(
        product_data, edition_data)
    app.dashboard.render.write_html(
        page_data,
        os.path.join(test_dir, 'v/index.html'))

    page_data = app.dashboard.render.render_build_dashboard(
        product_data, build_data)
    app.dashboard.render.write_html(
        page_data,
        os.path.join(test_dir, 'builds/index.html'))

    page_data = app.dashboard.render.render_development_index()
    app.dashboard.render.write_html(
        page_data,
        os.path.join(test_dir, 'index.html'))


@manager.command
def clean():
    """Delete development renderings and data caches in `_build/`."""
    import shutil
    shutil.rmtree('_build')


if __name__ == '__main__':
    manager.run()
