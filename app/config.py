"""ltd-dasher configuration and environment profiles."""

import abc
import os


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
        pass


class DevelopmentConfig(Config):
    """Local development configuration."""

    DEBUG = True

    @classmethod
    def init_app(cls, app):
        """Initialization hook called during create_app."""
        pass


class TestConfig(Config):
    """Test configuration (for py.test harness)."""

    @classmethod
    def init_app(cls, app):
        """Initialization hook called during create_app."""
        pass


class ProductionConfig(Config):
    """Production configuration."""

    @classmethod
    def init_app(cls, app):
        """Initialization hook called during create_app."""
        pass


config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
