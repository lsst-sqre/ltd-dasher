"""Routes at "/"."""

from flask import jsonify
from . import api
from .. import __version__


@api.route('/', methods=['GET'])
def get_metadata():
    """Root endpoint for metadata.

    :statuscode 200: OK.
    """
    message = {
        'dasher_version': __version__,
        'repo': 'https://github.com/lsst-sqre/ltd-dasher'
    }
    return jsonify(message), 200
