import logging

import click
import multiprocessing
from pollin.watch.ApplicationViewFileEventController import ApplicationViewFileEventController
from pollin.init.ApplicationContext import ApplicationContext
from pollin.load.ApplicationDataLoader import ApplicationDataLoader
from pollin.watch.ApplicationViewFileWatcher import ApplicationViewFileWatcher
from pollin.watch.ApplicationWebServer import ApplicationWebServer
from pollin.init.AppInitializer import AppInitializer

# global application context
app_context = ApplicationContext()

@click.group()
@click.option("--log", "-l", default="INFO", help="log level, default is INFO")
def cli(log: str):
    """
    Init command / start routine of application
    Sets up the application context for the entire application.
    """
    logging.basicConfig( encoding='utf-8', level=logging.getLevelName(log))

@cli.command(name="stage", help="Builds output files once.")
@click.argument("directory", required=True)
def stage(directory: str):
    """
    Builds the static site generator output files to the specified location with staging config.
    :param directory: Path of the view template directory
    :param output_path: Path to where the output files should be placed. By default, the output files are placed in the project directory.
    """

    # setting up the application context
    (AppInitializer(app_context)
     .configure(
        directory=directory,
        mode="stage"
    )
     .init_context_beans()
     .setup()
     )

    # encapsulates loading of project data and digital objects
    (ApplicationDataLoader(app_context)
        .load())

    # render all views (and handle related files etc.)
    (ApplicationViewFileEventController(app_context)
        .render_views())


@cli.command(name="build", help="Builds output files once.")
@click.argument("directory", required=True)
def build(directory: str):
    """
    Builds the static site generator output files to the specified location.
    :param directory: Path of the view template directory
    :param output_path: Path to where the output files should be placed. By default, the output files are placed in the project directory.
    """

    # setting up the application context
    (AppInitializer(app_context)
     .configure(
        directory=directory,
        mode="build"
    )
     .init_context_beans()
     .setup()
     )

    # encapsulates loading of project data and digital objects
    (ApplicationDataLoader(app_context)
        .load())

    # render all views (and handle related files etc.)
    (ApplicationViewFileEventController(app_context)
        .render_views())

@cli.command(name="dev", help="Starts the development process of the pollin tool.")
@click.argument("directory", required=True)
@click.option("--port", "-p", default=18090, help="The port to run the development server on")
def dev(directory: str, port: int):
    """
    Starts the static site generator (web server with rendering of views and initial data loading etc.)
    """

    # setting up the application context
    (AppInitializer(app_context)
     .configure(
        directory=directory,
        mode="dev"
    )
     .init_context_beans()
     .setup()
     )

    # encapsulates loading of project data and digital objects
    (ApplicationDataLoader(app_context)
        .load())

    web_dir = app_context.get_config().public_dir
    dev_server_process = multiprocessing.Process(target=ApplicationWebServer.start, args=(web_dir, port,))

    try:
        logging.info(f"*** Starting web server at port {port}")
        dev_server_process.start()
        logging.info("*** Starting view file watcher now")
        ApplicationViewFileWatcher.start(
            app_context
        )
        dev_server_process.join()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Stopping processes")
        dev_server_process.terminate()
        dev_server_process.join()


cli.add_command(dev)
cli.add_command(build)
cli.add_command(stage)
