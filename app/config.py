"""ltd-dasher configuration and environment profiles."""

import abc
import os


BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Configuration baseclass."""

    __metaclass__ = abc.ABCMeta

    DEBUG = False

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
