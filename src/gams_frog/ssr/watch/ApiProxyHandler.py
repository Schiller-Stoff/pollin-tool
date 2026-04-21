import logging

import aiohttp
from aiohttp import ClientSession, web


class ApiProxyHandler:
    """
    Forwards /api/* requests from the gams-frog dev server to the configured upstream GAMS5 API.

    Purpose: eliminate cross-origin requests during local development. The gams_frog dev server
    acts as a same-origin API host from the browser's perspective; this handler transparently
    forwards matching paths to the real upstream.

    Scope (intentional):
      - GET requests only. Non-GET methods return 405 (Allow: GET).
      - No cookie forwarding. No auth passthrough.
      - This is a forcing function: if authenticated / state-changing requests from templates
        ever become a real need, that has to be an explicit design conversation (cookie
        rewriting, CSRF handling, Keycloak login flow) — not a quiet extension here.

    Lifecycle:
      The handler uses a single shared aiohttp.ClientSession for the lifetime of the dev
      server, created on application startup and closed on shutdown. Reusing the session
      preserves HTTP keep-alive to the upstream, which matters when a single page load
      fires many API calls.
    """

    PATH_PREFIX = "/api/"
    """Path prefix that triggers proxy forwarding."""

    CLIENT_SESSION_APP_KEY: web.AppKey[ClientSession] = web.AppKey(
        "pollin_proxy_client", ClientSession
    )
    """aiohttp Application key under which the shared ClientSession is stored."""

    # Headers we explicitly forward to the upstream. Everything else is dropped —
    # notably Host, Origin, Cookie, and any auth-related headers (by omission).
    _FORWARDED_REQUEST_HEADERS = frozenset({
        "accept",
        "accept-language",
        "accept-encoding",
        "if-none-match",
        "if-modified-since",
    })

    # Headers we pass through from the upstream response to the browser. Everything else is
    # dropped — notably Set-Cookie (out of scope for read-only proxy and prevents leaking
    # staging cookies to localhost) and upstream CORS headers (meaningless now that the
    # browser sees a same-origin response).
    _FORWARDED_RESPONSE_HEADERS = frozenset({
        "content-type",
        "content-length",
        "etag",
        "last-modified",
        "cache-control",
        "expires",
        "vary",
    })

    _DEFAULT_TIMEOUT_SECONDS = 30

    def __init__(self, upstream_origin: str):
        """
        :param upstream_origin: The real GAMS API origin to forward to,
                                e.g. "https://gams-staging.uni-graz.at".
                                Trailing slashes are stripped.
        """
        if not upstream_origin:
            raise ValueError("upstream_origin must be a non-empty string")
        self.upstream_origin = upstream_origin.rstrip("/")

    def register(self, app: web.Application) -> None:
        """
        Registers this proxy with an aiohttp Application:
          - on_startup:  creates the shared ClientSession
          - on_cleanup:  closes it
          - route:       matches any method under /api/* and dispatches to self.handle

        Must be called before any catch-all static route is added to the same Application,
        because aiohttp matches routes in registration order.
        """
        app.on_startup.append(self._on_startup)
        app.on_cleanup.append(self._on_cleanup)
        # "*" so that non-GET methods reach self.handle and receive the explicit 405.
        # Without this, aiohttp would answer them with its own default 405 and swallow
        # our custom message.
        app.router.add_route("*", f"{self.PATH_PREFIX}{{tail:.*}}", self.handle)

    async def handle(self, request: web.Request) -> web.StreamResponse:
        """
        aiohttp route handler. Forwards the incoming request to the upstream and
        streams the response back.
        """
        if request.method != "GET":
            return web.Response(
                status=405,
                text=(
                    f"GAMS_FROG PROXY: only GET requests are forwarded to the upstream GAMS API. "
                    f"Got {request.method}. If you need state-changing requests from templates, "
                    f"this needs an explicit design decision — see README (dev proxy scope)."
                ),
                headers={"Allow": "GET"},
                content_type="text/plain",
            )

        upstream_url = f"{self.upstream_origin}{request.path_qs}"
        forwarded_headers = self._select_forwarded_request_headers(request)

        client_session: ClientSession = request.app[self.CLIENT_SESSION_APP_KEY]

        logging.debug(f"Proxy forwarding: GET {request.path_qs} -> {upstream_url}")

        try:
            async with client_session.get(
                upstream_url,
                headers=forwarded_headers,
                allow_redirects=False,
                timeout=aiohttp.ClientTimeout(total=self._DEFAULT_TIMEOUT_SECONDS),
            ) as upstream_response:
                response = web.StreamResponse(
                    status=upstream_response.status,
                    headers=self._select_forwarded_response_headers(upstream_response),
                )
                await response.prepare(request)

                # Stream body as it arrives — no buffering. Matters for large datastreams
                # (images, PDFs, TEI-XML files can be multi-MB in GAMS projects).
                async for chunk in upstream_response.content.iter_any():
                    await response.write(chunk)

                await response.write_eof()
                return response

        except aiohttp.ClientError as e:
            msg = (
                f"GAMS_FROG PROXY ERROR: cannot reach upstream GAMS API at '{self.upstream_origin}'. "
                f"Check that the upstream is running and reachable. Original error: {e}"
            )
            logging.error(msg)
            return web.Response(status=502, text=msg, content_type="text/plain")

    def _select_forwarded_request_headers(self, request: web.Request) -> dict:
        """
        Returns the subset of request headers to forward to the upstream.
        Host, Origin, Cookie, and auth-related headers are dropped by omission.
        """
        return {
            name: value
            for name, value in request.headers.items()
            if name.lower() in self._FORWARDED_REQUEST_HEADERS
        }

    def _select_forwarded_response_headers(
        self, upstream_response: aiohttp.ClientResponse
    ) -> dict:
        """
        Returns the subset of upstream response headers that should pass through to the browser.
        Set-Cookie, CORS headers, and transfer-encoding (managed by aiohttp) are dropped.
        """
        return {
            name: value
            for name, value in upstream_response.headers.items()
            if name.lower() in self._FORWARDED_RESPONSE_HEADERS
        }

    async def _on_startup(self, app: web.Application) -> None:
        """aiohttp on_startup hook: create the shared ClientSession."""
        app[self.CLIENT_SESSION_APP_KEY] = ClientSession()
        logging.debug("Proxy ClientSession created")

    async def _on_cleanup(self, app: web.Application) -> None:
        """aiohttp on_cleanup hook: close the shared ClientSession."""
        session: ClientSession = app.get(self.CLIENT_SESSION_APP_KEY)
        if session is not None:
            await session.close()
            logging.debug("Proxy ClientSession closed")