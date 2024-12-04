import time

from watchdog.observers import Observer

from pollin.System.init.ApplicationContext import ApplicationContext
from pollin.System.ApplicationEventController import ApplicationEventController


class ApplicationViewFileWatcher:
    """
    Watches the application files src-folder for changes and triggers the generation of new output files,
    based on defined event handler.
    """

    @staticmethod
    def start(app_context: ApplicationContext):
        """
        Watches the filesystem for changes and triggers the generation of new output files
        :param app_context : ApplicationContext : The application context to be passed down to the event controller
        """
        view_template_folder = app_context.get_config().project_src_dir
        # passing application context to the event controller (based on filewatching)
        event_handler = ApplicationEventController(app_context)
        observer = Observer()
        observer.schedule(event_handler, path=view_template_folder, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
