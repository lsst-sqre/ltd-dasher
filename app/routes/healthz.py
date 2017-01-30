"""Health check routes."""

from flask import jsonify
from . import api


@api.route('/healthz', methods=['GET'])
def healthz():
    """Liveness check.

    Use this route with `Kubernetes liveness probes <http://ls.st/90r>`_.

    :statuscode 200: OK.
    """
    return jsonify({'status': 'ok'}), 200
