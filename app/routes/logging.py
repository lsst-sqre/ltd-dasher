"""Decorator for route logging with structlog."""

import uuid
from functools import wraps
from flask import request
from structlog import get_logger


def log_route(f):
    """Decorator for Flask API routes that configures a structlog logging
    context.

    This decorator also logs the entry and exit from the route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # new() creates a new logging context
        logger = get_logger().new()
        # bind information about request that appears in all
        logger = logger.bind(request_id=str(uuid.uuid4()),
                             method=request.method,
                             path=request.path)
        logger.info("new request")
        return_value = f(*args, **kwargs)
        logger.info("returned", status=return_value[1])
        return return_value
    return decorated_function
