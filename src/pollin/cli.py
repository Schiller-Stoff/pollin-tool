import logging
import shutil

import click
import multiprocessing

from pollin.System.load.DigitalObjectService import DigitalObjectService
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
def cli(host: str, directory: str, project: str):
    """
    Init command / start routine of application
    Sets up the application context for the entire application.
    :param host: The host of the GAMS5 instance
    :param directory: Path of the view template directory
    :param project: Abbreviation of the project
    """
    logging.basicConfig( encoding='utf-8', level=logging.INFO)

    # setting up the application context
    (AppInitializer(app_context)
     .configure(project, host, directory)
     .init_context_beans()
     )


@cli.command(name="start", help="Starts the development web server")
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


@cli.command(name="init", help="Initializes the project structure for GAMS5")
def init():
    """
    Initializes the project structure for GAMS5
    :return:
    """
    ApplicationFileTemplater(app_context).setup()



@cli.command(name="gen", help="Generates the output files for the web server")
def gen():
    """

    :return:
    """
    # TODO this method here is somewhat outdated! (need to check at start command how to trigger the rendering)

    # TODO where to place this?
    # init public project folder structure
    if not app_context.get_config().project_public_dir.exists():
        app_context.get_config().project_public_dir.mkdir(parents=True)

    ApplicationDataLoader.load(app_context)

    # TODO where to put this logic? (package structure)
    DigitalObjectService.aggregate_index_json(app_context.get_config().project_public_dir, app_context.get_app_data_store().get_objects())

    DigitalObjectViewRenderer(app_context).render()


cli.add_command(start)
cli.add_command(gen)
cli.add_command(init)
