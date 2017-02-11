"""ltd-dasher configuration and environment profiles."""

import abc
import os
import logging
import sys

import structlog


BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Configuration baseclass."""

    __metaclass__ = abc.ABCMeta

    DEBUG = False

    AWS_ID = os.getenv('LTD_DASHER_AWS_ID')
    AWS_SECRET = os.getenv('LTD_DASHER_AWS_SECRET')
    FASTLY_KEY = os.getenv('LTD_DASHER_FASTLY_KEY')
    FASTLY_SERVICE_ID = os.getenv('LTD_DASHER_FASTLY_ID')

    @abc.abstractclassmethod
    def init_app(cls, app):
        """Initialization hook called during create_app that subclasses
        can implement.
        """
        # Implements structured logging to stdout with key-value formatting
        handler = logging.StreamHandler(sys.stdout)
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.DEBUG)

        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt='iso'),
                structlog.processors.KeyValueRenderer(
                    key_order=['method', 'path', 'event', 'request_id'],
                ),
                # structlog.dev.ConsoleRenderer()  # needs PyPI structlog[dev]
            ],
            # Maintains context dictionary across request
            context_class=structlog.threadlocal.wrap_dict(dict),
            # Use the standard library logger
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )


class DevelopmentConfig(Config):
    """Local development configuration."""

    DEBUG = True

    @classmethod
    def init_app(cls, app):
        """Initialization hook called during create_app."""
        super().init_app(app)


class TestConfig(Config):
    """Test configuration (for py.test harness)."""

    @classmethod
    def init_app(cls, app):
        """Initialization hook called during create_app."""
        super().init_app(app)


class ProductionConfig(Config):
    """Production configuration."""

    @classmethod
    def init_app(cls, app):
        """Initialization hook called during create_app."""
        # Same as default logging config, except we use JSON and
        # stick to INFO log levels.
        handler = logging.StreamHandler(sys.stdout)
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt='iso'),
                structlog.processors.JSONRenderer(),
            ],
            # Maintains context dictionary across request
            context_class=structlog.threadlocal.wrap_dict(dict),
            # Use the standard library logger
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )


config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
