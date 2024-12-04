
from pollin.System.init.ApplicationConfiguration import ApplicationConfiguration
from pollin.System.load.ApplicationScriptImporter import ApplicationScriptImporter
from pollin.System.load.utils.Pyrilo import Pyrilo
from pollin.System.load.ApplicationDatastore import ApplicationDatastore


class ApplicationContext:
    """
    Holds references to important objects and provides them to other classes
    Should be assigned at startup of the main application.
    """

    config: ApplicationConfiguration
    pyrilo: Pyrilo
    app_data_store: ApplicationDatastore
    app_script_importer: ApplicationScriptImporter

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

    def set_app_script_importer(self, app_script_importer: ApplicationScriptImporter):
        self.app_script_importer = app_script_importer

    def get_app_script_importer(self) -> ApplicationScriptImporter:
        return self.app_script_importer