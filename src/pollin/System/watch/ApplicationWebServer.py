from http.server import HTTPServer as BaseHTTPServer, SimpleHTTPRequestHandler
import os
import logging

class ApplicationWebServer:
    """This class is responsible for starting the development web server"""

    @staticmethod
    def start(web_dir: str, port: int):
        """
        Starts the development web server
        :param web_dir:  The directory to serve
        :param port: The port to serve on
        """
        httpd = HTTPServer(web_dir, ("", port))
        httpd.serve_forever()


class HTTPHandler(SimpleHTTPRequestHandler):
    """This handler uses server.base_path instead of always using os.getcwd()"""

    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath

    def end_headers(self):
        # disables CORS for local dev server
        self.send_header("Access-Control-Allow-Origin", "*")
        SimpleHTTPRequestHandler.end_headers(self)

    def handle_one_request(self):
        """
        Improves logging when handling singular requests
        """
        try:
            return SimpleHTTPRequestHandler.handle_one_request(self)
        except ConnectionAbortedError:
            # TODO needs the logger instance passed and not global module!
            print("Connection was aborted - this is normal if the client closes the connection")
            return
        except Exception as e:
            # TODO needs the logger instance passed and not global module!
            print(f"Error handling request: {e}")
            return


class HTTPServer(BaseHTTPServer):
    """The main server, you pass in base_path which is the path you want to serve requests from"""

    def __init__(self, base_path, server_address, RequestHandlerClass=HTTPHandler):
        self.base_path = base_path
        BaseHTTPServer.__init__(self, server_address, RequestHandlerClass)