import shutil
import sys
from pathlib import Path
import click
from importlib.resources import files, as_file


def initialize_project(target_dir: str):
    target_path = Path(target_dir).resolve()

    # Create target directory if it doesn't exist
    target_path.mkdir(parents=True, exist_ok=True)

    # Check if the directory is empty. We don't want to blindly overwrite existing projects.
    if any(target_path.iterdir()):
        click.echo(f"Warning: The directory '{target_path}' is not empty.", err=True)
        if not click.confirm("Do you want to initialize the project here anyway? Existing files might be overwritten."):
            click.echo("Initialization aborted.")
            sys.exit(0)

    try:
        # 'files' gives us a Traversable object pointing to the package directory inside the installation/wheel
        scaffold_pkg_path = files('gams_frog.resources').joinpath('scaffold')

        # We can't directly pass Traversable to shutil.copytree in all cases,
        # so we resolve it or use a custom recursive copy if it's inside a zipped egg/wheel.
        # However, for standard modern setups (and development), copytree on a Traversable's string representation works well
        # if the package is installed unzipped, OR we can implement a safe traverser.
        # Python 3.12+ `importlib.resources.as_file` handles zip safety:

        with as_file(scaffold_pkg_path) as scaffold_path:
            # dirs_exist_ok=True allows us to merge into an existing directory if the user confirmed
            shutil.copytree(scaffold_path, target_path, dirs_exist_ok=True)

        click.echo(click.style(f"\n✅ Successfully initialized gams-frog project in {target_path}", fg="green"))
        click.echo("You can now run 'frog dev' to start the development server.")

    except Exception as e:
        click.echo(f"Fatal error initializing project: {e}", err=True)
        sys.exit(1)