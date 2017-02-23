#####################
LSST the Docs: Dasher
#####################

**Versioning** is a core feature of LSST the Docs.
By default, the documentation of every branch and tag of a Git repository is available through separate URLs.
LTD Dasher creates lightweight dashboards, available at `(product).lsst.io/v` and `(product).lsst.io/builds`, that help users find the right version of project's documentation.
For more information about LSST the Docs' versioned documentation, see `SQR-006`_.

LTD Dasher is a Kubernetes-deployed microservice that works with `LTD Keeper`_.

Local development
=================

In a Python 3.5 virtual environment, install requirements::

   pip install -r requirements.txt

Installing ``npm`` and ``gulp`` if they're not already installed.
For example::

   brew install node
   npm install -g gulp

And install LTD Dasher's node.js dependencies::

   npm install

Generate a dashboard for development (written to ``_build``)::

   ./run.py render

Clean up the development render::

   ./run.py clean

Run a development server::

   ./run.py runserver

Run unit tests::

   py.test --flake8 --cov=app

Making Docker images
====================

Prepare assets::

   gulp assets -env=deploy

Build the image::

   docker build -t lsstsqre/ltd-dasher:tag .

**Note:** for *releases*, the image's **tag** should match both the Git tag and ``app.__version__``.
We need to work out the continuous delivery pipeline.

Push to `lsstsqre/ltd-dasher <https://hub.docker.com/r/lsstsqre/ltd-dasher/>`_ on Docker Hub::

   docker push lsstsqre/ltd-dasher:tag

Kubernetes deployment
=====================

LTD Dasher needs to be deployed in the same Kubernetes cluster as `LTD Keeper`_; Dasher isn't meant to have a world-facing endpoint.
The basic deployment is::

   cd kubernetes
   kubectl apply -f dasher-service.yaml
   kubectl apply -f dasher-deployment.yaml

Through the ``dasher`` service, the application is available in the cluster at::

   http://dasher:3031/

HTTP API reference
==================

GET /
-----

Returns basic metadata about the service.
Example::

   HTTP/1.0 200 OK
   Content-Length: 91
   Content-Type: application/json
   Date: Tue, 24 Jan 2017 17:32:47 GMT
   Server: Werkzeug/0.11.15 Python/3.5.2

   {
       "dasher_version": "0.1.0-rc.1",
       "repo": "https://github.com/lsst-sqre/ltd-dasher"
   }

GET /healthz
------------

Endpoint for a readiness probe (see ``kubernetes/dasher-deployment.yaml``).
Example::

   HTTP/1.0 200 OK
   Content-Length: 21
   Content-Type: application/json
   Date: Tue, 24 Jan 2017 17:34:30 GMT
   Server: Werkzeug/0.11.15 Python/3.5.2

   {
       "status": "ok"
   }

POST /build
-----------

Triggers a dashboard build on one or more LTD Keeper-managed products.

Example request with HTTPie_::

   http post http://localhost:3031/build \
       product_urls:='["https://keeper.lsst.codes/products/developer", "https://keeper.lsst.codes/products/pipelines"]'

Expected response status: ``202``.

****

Copyright 2017 Association of Universities for Research in Astronomy, Inc.

MIT licensed open source.

.. _LTD Keeper: https://ltd-keeper.lsst.io
.. _SQR-006: https://sqr-006.lsst.io/#versioned-documentation-urls
.. _HTTPie: https://httpie.org
