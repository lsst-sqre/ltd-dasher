"""Routes at ``/build`` that implement dashboard builds."""

from flask import jsonify, request, current_app
from . import api
from ..worker import build_dashboard_for_product


@api.route('/build', methods=['POST'])
def build_dashboards():
    """Build dashboard(s).

    :statuscode 202: Dashboard rebuild trigger sent.
    """
    for product_resource_url in request.json['product_urls']:
        build_dashboard_for_product(product_resource_url, current_app.config)

    # Ideally we'd provide a status endpoint, and put that URL in the header
    return jsonify({}), 202, {}
