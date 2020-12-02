"""Error handling functions.

Flask calls these functions when different HTTP error codes or Python
exceptions are emitted. These handlers provide a JSON response rather
than the default HMTL header response.
"""

from flask import jsonify
from structlog import get_logger
from ..exceptions import ValidationError
from . import api


__all__ = ['bad_request', 'not_found', 'method_not_supported',
           'internal_server_error']


@api.errorhandler(ValidationError)
def bad_request(e):
    """Handler for ValidationError exceptions."""
    response = jsonify({'status': 400, 'error': 'bad request',
                        'message': e.args[0]})
    logger = get_logger("ltddasher")
    logger.warn(e.args[0], status=400)
    response.status_code = 400
    return response


@api.app_errorhandler(404)
def not_found(e):
    """App-wide handler for HTTP 404 errors."""
    response = jsonify({'status': 404, 'error': 'not found',
                        'message': 'invalid resource URI'})
    logger = get_logger("ltddasher")
    logger.warn('not found', status=404)
    response.status_code = 404
    return response


@api.errorhandler(405)
def method_not_supported(e):
    """Handler for HTTP 405 exceptions."""
    response = jsonify({'status': 405, 'error': 'method not supported',
                        'message': 'the method is not supported'})
    logger = get_logger("ltddasher")
    logger.warn(e.args[0], status=405)
    response.status_code = 405
    return response


@api.app_errorhandler(500)
def internal_server_error(e):
    """App-wide handler for HTTP 500 errors."""
    response = jsonify({'status': 500, 'error': 'internal server error',
                        'message': e.args[0]})
    logger = get_logger("ltddasher")
    logger.error(e.args[0], status=500)
    response.status_code = 500
    return response
