
from pollin.ssr.init.config.ApplicationConfiguration import ApplicationConfiguration
from pollin.ssr.load.utils.Pyrilo import Pyrilo
from pollin.ssr.load.ApplicationDatastore import ApplicationDatastore


class ApplicationContext:
    """
    Holds references to important objects and provides them to other classes
    Should be assigned at startup of the main application.
    """

    config: ApplicationConfiguration
    pyrilo: Pyrilo
    app_data_store: ApplicationDatastore

    def __init__(self):
        pass

    def set_config(self, config: ApplicationConfiguration):
        self.config = config

    def get_config(self) -> ApplicationConfiguration:
        return self.config

    def set_pyrilo(self, pyrilo: Pyrilo):
        self.pyrilo = pyrilo

    def get_pyrilo(self) -> Pyrilo:
        return self.pyrilo

    def set_app_data_store(self, app_data_store: ApplicationDatastore):
        self.app_data_store = app_data_store

    def get_app_data_store(self) -> ApplicationDatastore:
        return self.app_data_store