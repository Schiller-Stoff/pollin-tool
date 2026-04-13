import os
from aiohttp import web

class ApplicationWebServer:
    """This class is responsible for starting the development web server"""

    @staticmethod
    def create_handle_directory_index(web_dir: str, port: int):
        """
        Higher Order function that allows to pass in arguments to created function (being called as lambda).
        (Check docstring of built function)
        """
        def handle_directory_index(request):
            """
            Checks if incoming request url points to a directory or file.
            Enforces trailing slashes for directory requests to ensure relative path integrity.
            """
            # TODO add logging

            requested_path = request.path

            # Remove leading slash and normalize
            relative_path = requested_path.lstrip('/')

            # Check if directory exists and has index.html
            full_path = os.path.join(web_dir, relative_path)

            # Check if path is a directory
            if os.path.isdir(full_path):
                # Pollin-Tool logic: Directory URLs must end with a slash for relative linking to work
                if not requested_path.endswith("/"):
                    msg = (f"POLLIN ERROR: The URL path '{requested_path}' points to a directory (trying to resolve the nested index.html) but is missing a trailing slash '/'. "
                           "This hinders relative paths (like 'root_path') in the static site from resolving correctly.")
                    return web.Response(text=msg, status=400)

                index_path = os.path.join(full_path, "index.html")
                if os.path.exists(index_path):
                    return web.FileResponse(index_path)

            # Check if path is a file
            elif os.path.exists(full_path) and os.path.isfile(full_path):
                return web.FileResponse(full_path)

            # Fall back to regular static file handling
            raise web.HTTPNotFound()

        return handle_directory_index

    @staticmethod
    def start(web_dir: str, port: int):
        """
        Starts the development web server
        :param web_dir:  The directory to serve
        :param port: The port to serve on
        """

        app = web.Application()

        # next lines make sure that under /dirpath --> by default /dirpath/index.html is being served
        handle_directory_index = ApplicationWebServer.create_handle_directory_index(web_dir, port)
        # Handle directory index requests first
        app.router.add_get(r'/{path:.*}', handle_directory_index)

        # Serve static files from the current directory
        app.router.add_static('/', path=web_dir, show_index=True)
        web.run_app(app, port=port)