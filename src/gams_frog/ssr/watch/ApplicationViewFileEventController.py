import logging

# Change import to PatternMatchingEventHandler
from watchdog.events import PatternMatchingEventHandler

from gams_frog.ssr.watch.BuildMetadataRenderer import BuildMetadataRenderer
from gams_frog.ssr.watch.render.DigitalObjectViewRenderer import DigitalObjectViewRenderer
from gams_frog.ssr.init.ApplicationContext import ApplicationContext
from gams_frog.ssr.watch.render.ApplicationStaticFileRenderer import ApplicationStaticFileRenderer
from gams_frog.ssr.watch.render.ApplicationViewTemplateRenderer import ApplicationViewTemplateRenderer


class ApplicationViewFileEventController(PatternMatchingEventHandler):
    """
    Listens to file system events and triggers the rendering of views.
    Configured to ignore system, temporary, and IDE files to prevent infinite loops.
    """

    app_context: ApplicationContext
    digital_object_view_renderer: DigitalObjectViewRenderer
    application_view_template_render: ApplicationViewTemplateRenderer
    application_static_file_refresher: ApplicationStaticFileRenderer
    build_metadata_renderer: BuildMetadataRenderer

    def __init__(self, app_context: ApplicationContext):
        self.app_context = app_context

        # Initialize with ignore patterns to filter out noise
        super().__init__(ignore_patterns=[
            "*/.git/*", "*/.idea/*", "*/.vscode/*", "*/__pycache__/*",
            "*.swp", "*.tmp", "*.DS_Store", "~*"
        ])

        # for digital objects
        self.digital_object_view_renderer = DigitalObjectViewRenderer(app_context)

        # for about.html etc.
        self.application_view_template_render = ApplicationViewTemplateRenderer(app_context)

        # for static files (remove and add if something changes)
        self.application_static_file_refresher = ApplicationStaticFileRenderer(app_context)

        # for build metadata
        self.build_metadata_renderer = BuildMetadataRenderer(app_context)

    def on_modified(self, event):
        # Ignore directory events to avoid double-triggering (file + folder update)
        if event.is_directory:
            return

        logging.info(f"File modified: {event.src_path}")
        self.render_views()

    def on_created(self, event):
        if event.is_directory:
            return

        logging.info(f"File created: {event.src_path}")
        self.render_views()

    def on_deleted(self, event):
        if event.is_directory:
            return

        logging.info(f"File deleted: {event.src_path}")
        # deletes correspondent file
        self.application_view_template_render.delete_output_file(event.src_path)

        # trigger re-render of dependent components
        self.digital_object_view_renderer.render()
        self.application_static_file_refresher.refresh()

    def render_views(self):
        """
        Renders the views
        """
        self.application_view_template_render.render()
        self.digital_object_view_renderer.render()
        self.application_static_file_refresher.refresh()
        # build metadata only for staging and production
        if self.app_context.get_config().mode != "dev":
            self.build_metadata_renderer.render()
        logging.info(f"Successfully rendered views. {self.__class__.__name__}")