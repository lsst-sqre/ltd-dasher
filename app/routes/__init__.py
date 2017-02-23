"""Application routes as a Flask Blueprint."""

from flask import Blueprint

# Create api before importing modules because they need it.
api = Blueprint('api', __name__)

from .errorhandlers import *  # noqa: F401,F403,E402
from . import build  # noqa: F401,E402
from . import healthz  # noqa: F401,E402
from . import root  # noqa: F401,E402
