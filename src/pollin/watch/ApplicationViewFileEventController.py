import logging

from watchdog.events import FileSystemEventHandler
from pollin.watch.render.DigitalObjectViewRenderer import DigitalObjectViewRenderer
from pollin.init.ApplicationContext import ApplicationContext
from pollin.watch.render.ApplicationStaticFileRenderer import ApplicationStaticFileRenderer
from pollin.watch.render.ApplicationViewTemplateRenderer import ApplicationViewTemplateRenderer

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

        # for about.html etc.
        self.application_view_template_render = ApplicationViewTemplateRenderer(app_context)

        # for static files (remove and add if something changes)
        self.application_static_file_refresher = ApplicationStaticFileRenderer(app_context)

    def on_modified(self, event):
        self.render_views()
        logging.info("on_modified event")

    def on_created(self, event):
        self.render_views()
        logging.info("on_created event")

    def on_deleted(self, event):
        # deletes correspondent file
        self.application_view_template_render.delete_output_file(event.src_path)

        # deletion only performed at startup
        self.digital_object_view_renderer.render()

        # will delete everything and copy again (no delete necessary)
        self.application_static_file_refresher.refresh()
        logging.info("on_deleted event")


    def render_views(self):
        """
        Renders the views
        """
        self.application_view_template_render.render()
        self.digital_object_view_renderer.render()
        self.application_static_file_refresher.refresh()
        logging.info(f"Successfully rendered views. {self.__class__.__name__}")