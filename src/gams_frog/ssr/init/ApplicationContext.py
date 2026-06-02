
from gams_frog.ssr.init.config.ApplicationConfiguration import ApplicationConfiguration
from gams_frog.ssr.init.config.ApplicationRenderContext import ApplicationRenderContext
from gams_frog.ssr.load.utils.Pyrilo import Pyrilo
from gams_frog.ssr.load.ApplicationDatastore import ApplicationDatastore


class ApplicationContext:
    """
    Holds references to important objects and provides them to other classes
    Should be assigned at startup of the main application.
    """

    config: ApplicationConfiguration
    pyrilo: Pyrilo
    app_data_store: ApplicationDatastore

    application_render_context: ApplicationRenderContext | None
    """
    Application rendering context - holds data about the rendering process.
    Not initialized before the watch phase of the static site application
    """

    def __init__(self):
        pass

    def set_application_render_context(self, app_render_context: ApplicationRenderContext):
        self.application_render_context = app_render_context

    def get_application_render_context(self) -> ApplicationRenderContext:
        if self.application_render_context is None:
            raise RuntimeError("Rendering context is None - has not been set at the current ssr stage. The rendering context is only available after and during rendering.")
        return self.application_render_context

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