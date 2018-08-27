import os
import configparser
import functools


def singleton(cls):
    """
    Decorator allows you to create only one instance for the contents of configurations
    :param cls: instance
    :return: new singleton or None
    """
    instance = None

    @functools.wraps(cls)
    def inner(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance
    return inner


@singleton
class Config(object):
    """
    A configuration object that contains the settings for hosts and ports.
    """
    def __init__(self):
        self.elastic_host = "127.0.0.1"
        self.api_host = "0.0.0.0"
        self.elastic_port = 9200
        self.api_port = 5000
        self.get_config_for_es_api()

    def get_config_for_es_api(self):
        """
        Receiving host and port settings from the configuration file
        :return: None
        """
        config = configparser.ConfigParser()
        try:
            config.read(os.path.join(os.path.dirname(__file__), "config", "config_service.ini"))
            self.elastic_host = config.get("elasticsearch", "host")
            self.elastic_port = config.get("elasticsearch", "port")
            self.api_host = config.get("rest_api", "host")
            self.api_port = config.get("rest_api", "port")
        except configparser.Error as e:
            print(str(e))
