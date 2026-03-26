import logging
import sys

import click
import multiprocessing

from importlib.metadata import version, PackageNotFoundError
# makes sure that the version is set correctly
try:
    __version__ = version("pollin-tool")
except PackageNotFoundError:
    __version__ = "dev"

from pollin.deploy.GamsAuthClient import GamsAuthClient
from pollin.ssr.watch.ApplicationViewFileEventController import ApplicationViewFileEventController
from pollin.ssr.init.ApplicationContext import ApplicationContext
from pollin.ssr.load.ApplicationDataLoader import ApplicationDataLoader
from pollin.ssr.watch.ApplicationViewFileWatcher import ApplicationViewFileWatcher
from pollin.ssr.watch.ApplicationWebServer import ApplicationWebServer
from pollin.ssr.init.AppInitializer import AppInitializer
from pollin.validation.JinjaTemplateValidator import JinjaTemplateValidator
from pollin.validation.StaticFileValidator import StaticFileValidator

# global application context
app_context = ApplicationContext()

def run_validation_or_exit(context: ApplicationContext):
    # 1. Validate Templates (AST)
    template_validator = JinjaTemplateValidator(context)
    templates_ok = template_validator.validate()

    # 2. Validate Static Files (Regex)
    static_validator = StaticFileValidator(context)
    static_ok = static_validator.validate()

    if not (templates_ok and static_ok):
        logging.error("Build aborted due to quality gate violations.")
        sys.exit(1)


def run_deploy(context: ApplicationContext, username: str | None, password: str | None):
    """
    Performs authentication and deployment to the GAMS5 API.

    :param context: The application context
    :param username: GAMS API username (prompted if not provided)
    :param password: GAMS API password (prompted if not provided)
    """
    from pollin.deploy.DeployService import DeployService

    mode = context.get_config().mode
    target_host = context.get_config().gams_host

    # Safety confirmation for production deployments
    if mode == "build":
        click.echo("\n*** PRODUCTION DEPLOYMENT ***")
        click.echo(f"Target: {target_host}")
        click.echo(f"Project: {context.get_config().project}")
        if not click.confirm("Deploy to PRODUCTION environment?", default=False):
            click.echo("Deployment cancelled.")
            return

    # Prompt for credentials if not provided via options
    if not username:
        username = click.prompt("GAMS API username")
    if not password:
        password = click.prompt("GAMS API password", hide_input=True)

    # Authenticate
    logging.info(f"Authenticating with GAMS API at {target_host}...")
    auth_gams_client = GamsAuthClient(target_host)
    try:
        from pollin.deploy.AuthorizationService import AuthorizationService
        # TODO using a separte client seems weird
        auth_service = AuthorizationService(auth_gams_client)
        auth_service.login(username=username, password=password)
    except PermissionError as e:
        logging.error(f"Authentication failed: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Authentication error: {e}")
        sys.exit(1)

    # Deploy
    try:
        deploy_service = DeployService(context, auth_gams_client)
        result = deploy_service.deploy()
        click.echo("\nDeployment successful!")
        click.echo(f"  Project:    {result.get('projectAbbr', 'N/A')}")
        click.echo(f"  Files:      {result.get('fileCount', 'N/A')}")
        click.echo(f"  Total size: {result.get('totalSize', 'N/A')} bytes")
        click.echo(f"  Deployed at: {result.get('deployedAt', 'N/A')}")
    except (FileNotFoundError, ValueError) as e:
        logging.error(f"Deployment failed: {e}")
        sys.exit(1)
    except (ConnectionError, PermissionError) as e:
        logging.error(f"Deployment failed: {e}")
        sys.exit(1)


@click.group()
@click.version_option(version=version("pollin-tool"), prog_name="pollin-tool")
@click.option("--log", "-l", default="INFO", help="log level, default is INFO")
def cli(log: str):
    """
    Init command / start routine of application
    Sets up the application context for the entire application.
    """
    logging.basicConfig( encoding='utf-8', level=logging.getLevelName(log))

@cli.command(name="stage", help="Builds output files once with staging configuration.")
@click.argument("directory", default=".", required=False)
@click.option("--deploy", "-d", is_flag=True, default=False, help="Deploy the built files to the staging GAMS API after build.")
@click.option("--username", "-u", default=None, help="GAMS API username for deployment.")
@click.option("--password", "-p", default=None, help="GAMS API password for deployment.")
def stage(directory: str, deploy: bool, username: str, password: str):
    """
    Builds the static site generator output files with staging config.
    Use --deploy to upload the result to the staging GAMS API.
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

    # validate template files first
    run_validation_or_exit(app_context)

    # encapsulates loading of project data and digital objects
    (ApplicationDataLoader(app_context)
        .load())

    # render all views (and handle related files etc.)
    (ApplicationViewFileEventController(app_context)
        .render_views())

    # deploy if requested
    if deploy:
        run_deploy(app_context, username, password)


@cli.command(name="build", help="Builds production output files.")
@click.argument("directory", default=".", required=False)
@click.option("--deploy", "-d", is_flag=True, default=False, help="Deploy the built files to the production GAMS API after build.")
@click.option("--username", "-u", default=None, help="GAMS API username for deployment.")
@click.option("--password", "-p", default=None, help="GAMS API password for deployment.")
def build(directory: str, deploy: bool, username: str, password: str):
    """
    Builds the static site generator production output files.
    Use --deploy to upload the result to the production GAMS API.
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

    # validate template files first
    run_validation_or_exit(app_context)

    # encapsulates loading of project data and digital objects
    (ApplicationDataLoader(app_context)
        .load())

    # render all views (and handle related files etc.)
    (ApplicationViewFileEventController(app_context)
        .render_views())

    # deploy if requested
    if deploy:
        run_deploy(app_context, username, password)


@cli.command(name="dev", help="Starts the development process of the pollin tool.")
@click.argument("directory", default=".", required=False)
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

    # first run validation
    run_validation_or_exit(app_context)

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