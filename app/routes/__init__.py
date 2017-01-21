"""Application routes as a Flask Blueprint."""

from flask import Blueprint

# Create api before importing modules because they need it.
api = Blueprint('api', __name__)
