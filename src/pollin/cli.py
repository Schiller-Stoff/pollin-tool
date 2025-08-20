import logging
import shutil
from pathlib import Path

import click
import multiprocessing

from pollin.System.load.DigitalObjectService import DigitalObjectService
from pollin.System.watch.ApplicationViewFileEventController import ApplicationViewFileEventController
from pollin.System.watch.render.DigitalObjectViewRenderer import DigitalObjectViewRenderer
from pollin.System.init.ApplicationContext import ApplicationContext
from pollin.System.load.ApplicationDataLoader import ApplicationDataLoader
from pollin.System.setup.ApplicationFileTemplater import ApplicationFileTemplater
from pollin.System.watch.ApplicationViewFileWatcher import ApplicationViewFileWatcher
from pollin.System.watch.ApplicationWebServer import ApplicationWebServer
from pollin.System.init.AppInitializer import AppInitializer

# global application context
app_context = ApplicationContext()

@click.group()
@click.argument("project", required=True)
@click.argument("directory", required=True)
@click.option("--host", "-h", default="http://localhost:18085", help="The host of the GAMS5 instance")
@click.option("--output_path", "-o", default=None, help="Path to where the output = public files should be placed. By default, the output files are placed in the project directory.")
def cli(host: str, directory: str, project: str, output_path: str):
    """
    Init command / start routine of application
    Sets up the application context for the entire application.
    :param host: The host of the GAMS5 instance
    :param directory: Path of the view template directory
    :param project: Abbreviation of the project
    :param output_path: Path to where the output files should be placed. By default, the output files are placed in the project directory.
    """
    logging.basicConfig( encoding='utf-8', level=logging.INFO)

    # setting up the application context
    (AppInitializer(app_context)
     .configure(project, host, directory,output_path)
     .init_context_beans()
     )

@cli.command(name="build", help="Builds output files to the specified location.")
def build():
    """
    Builds the static site generator output files to the specified location.
    :param location: The location where the output files should be placed
    """

    # TODO where to place this? is in a complete wrong location?
    # (also inside the start cli call / remove existing public folder and fresh rebuild on startup)
    # if not public folder exist -> create
    if not app_context.get_config().project_public_dir.exists():
        app_context.get_config().project_public_dir.mkdir(parents=True)
    # else delete complete tree and recreate
    else:
        shutil.rmtree(app_context.get_config().project_public_dir)
        app_context.get_config().project_public_dir.mkdir(parents=True)

    # encapsulates loading of project data and digital objects# encapsulates loading of project data and digital objects
    (ApplicationDataLoader(app_context)
        .load())

    # TODO instransparent call - maybe providing some kind of method here?
    # init should render output already
    ApplicationViewFileEventController(app_context)




@cli.command(name="start", help="Starts the development process of the static site generator.")
@click.argument("port", required=False, default=18090)
def start(port: int):
    """
    Starts the static site generator (web server with rerendering of views and initial data loading etc.)
    """
    # TODO where to place this?
    # if not public folder exist -> create
    if not app_context.get_config().project_public_dir.exists():
        app_context.get_config().project_public_dir.mkdir(parents=True)
    # else delete complete tree and recreate
    else:
        shutil.rmtree(app_context.get_config().project_public_dir)
        app_context.get_config().project_public_dir.mkdir(parents=True)

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


@cli.command(name="init", help="Initializes the project structure required for the pollin tool.")
def init():
    """
    Initializes the project structure for GAMS5
    :return:
    """
    ApplicationFileTemplater(app_context).setup()


cli.add_command(start)
cli.add_command(build)
cli.add_command(init)
