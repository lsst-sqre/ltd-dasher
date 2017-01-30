"""Routes at ``/build`` that implement dashboard builds."""

from flask import jsonify
from . import api


@api.route('/build', methods=['POST'])
def build_dashboards():
    """Build dashboard(s), triggering one celery task per product.

    :statuscode 202: Dashboard rebuild trigger sent.
    """

    # TODO provide a status endpoint in the Location header
    return jsonify({}), 202, {}
