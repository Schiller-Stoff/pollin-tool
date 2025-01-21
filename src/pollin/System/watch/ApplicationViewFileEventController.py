import logging

from watchdog.events import FileSystemEventHandler
from pollin.System.watch.render.DigitalObjectViewRenderer import DigitalObjectViewRenderer
from pollin.System.init.ApplicationContext import ApplicationContext
from pollin.System.watch.render.ApplicationStaticFileRenderer import ApplicationStaticFileRenderer
from pollin.System.watch.render.ApplicationViewTemplateRenderer import ApplicationViewTemplateRenderer

class ApplicationViewFileEventController(FileSystemEventHandler):
    """
    Listens to file system events and triggers the rendering of views
    """

    app_context: ApplicationContext

    digital_object_view_renderer: DigitalObjectViewRenderer

    application_view_template_render: ApplicationViewTemplateRenderer

    application_static_file_refresher: ApplicationStaticFileRenderer

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context

        # for digital objects
        self.digital_object_view_renderer = DigitalObjectViewRenderer(app_context)
        self.digital_object_view_renderer.render()

        # for about.html etc.
        self.application_view_template_render = ApplicationViewTemplateRenderer(app_context)
        self.application_view_template_render.render()

        # for static files (remove and add if something changes)
        self.application_static_file_refresher = ApplicationStaticFileRenderer(app_context)
        self.application_static_file_refresher.refresh()

        logging.info(f"Successfully rendered views. Init event of {self.__class__.__name__}")

    def on_modified(self, event):
        self.application_view_template_render.render()
        self.digital_object_view_renderer.render()
        self.application_static_file_refresher.refresh()
        logging.info("Successfully rendered views - on_modified event")

    def on_created(self, event):
        self.application_view_template_render.render()
        self.digital_object_view_renderer.render()
        self.application_static_file_refresher.refresh()
        logging.info("Successfully rendered views - on_created event")

    def on_deleted(self, event):
        self.application_view_template_render.render()
        self.digital_object_view_renderer.render()
        self.application_static_file_refresher.refresh()
        logging.info("Successfully rendered views - on_deleted event")

