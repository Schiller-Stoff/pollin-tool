import os
import logging
import asyncio
from aiohttp import web

from gams_frog.ssr.watch.ApiProxyHandler import ApiProxyHandler


class ApplicationWebServer:
    """This class is responsible for starting the development web server"""

    @staticmethod
    @web.middleware
    async def directory_index_middleware(request, handler):
        """
        Intercepts directory requests and serves their index.html files directly.
        Passes regular file requests through to aiohttp's optimized static handler.
        """
        # Let API proxy or other exact non-static routes pass through untouched
        if request.path.startswith("/api/"):
            return await handler(request)

        web_dir = request.app['web_dir']
        relative_path = request.path.lstrip('/')
        full_path = os.path.join(web_dir, relative_path)

        # Non-blocking check to see if the target is a directory
        is_dir = await asyncio.to_thread(os.path.isdir, full_path)

        if is_dir:
            # Enforce the trailing slash to prevent broken relative asset links
            if not request.path.endswith("/"):
                msg = (
                    f"GAMS_FROG ERROR: The URL path '{request.path}' points to a directory "
                    "but is missing a trailing slash '/'. Relative paths will fail to resolve."
                )
                return web.Response(text=msg, status=400)

            index_path = os.path.join(full_path, "index.html")

            # Verify index.html exists before attempting to serve it
            if await asyncio.to_thread(os.path.exists, index_path):
                # FileResponse natively handles ETag, Last-Modified, and 304 Not Modified!
                return web.FileResponse(index_path)

        # If it's a file (like iconoir.css), hand it over to the native static router
        return await handler(request)

    @staticmethod
    def build_app(web_dir: str, proxy_target_origin: str | None = None) -> web.Application:
        """
        Builds and configures the aiohttp Application used by the dev server.
        Separated from `start()` so the wiring can be exercised in tests without running
        an actual event loop.

        Route registration order matters: the /api proxy (if enabled) is registered first
        so it wins over the static catch-all for matching paths.

        :param web_dir: The directory to serve as static content
        :param proxy_target_origin: Upstream GAMS API origin for /api/* forwarding, or None
                                    to disable the proxy. See ApiProxyHandler.
        :return: A configured aiohttp Application ready to be run or tested.
        """
        app = web.Application(middlewares=[ApplicationWebServer.directory_index_middleware])
        app['web_dir'] = web_dir

        if proxy_target_origin:
            proxy_handler = ApiProxyHandler(proxy_target_origin)
            proxy_handler.register(app)
            logging.info(f"*** Dev proxy enabled: {ApiProxyHandler.PATH_PREFIX}* -> {proxy_target_origin}")

        # This will now safely handle all CSS, JS, images, and explicit file requests
        app.router.add_static('/', path=web_dir)

        return app

    @staticmethod
    def start(web_dir: str, port: int, proxy_target_origin: str | None = None):
        """Starts the development web server."""
        app = ApplicationWebServer.build_app(web_dir, proxy_target_origin)
        # Pass print=None to silence the default aiohttp stdout banner.
        web.run_app(app, port=port, print=None)