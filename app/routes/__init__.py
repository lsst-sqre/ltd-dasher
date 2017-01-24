"""Application routes as a Flask Blueprint."""

from flask import Blueprint

# Create api before importing modules because they need it.
api = Blueprint('api', __name__)

from . import build  # noqa: F401,E402
from . import healthz  # noqa: F401,E402
