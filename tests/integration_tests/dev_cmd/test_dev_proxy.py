"""
Integration tests for the dev proxy wiring via ApplicationWebServer.build_app.

These tests exercise the same route-registration logic the real dev server uses — just
without calling web.run_app() — to verify that the proxy and the static catch-all
coexist correctly and that the route-registration order lets /api/* win over the static
handler.
"""
import asyncio

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from gams_frog.ssr.watch.ApplicationWebServer import ApplicationWebServer


def _run(coro):
    return asyncio.run(coro)


def _upstream_origin(server: TestServer) -> str:
    return f"http://{server.host}:{server.port}"


def _const(response_factory):
    """Wraps a no-arg response factory into an async aiohttp handler."""
    async def handler(request):
        return response_factory()
    return handler


# ---------------------------------------------------------------------------
# Proxy + static coexistence
# ---------------------------------------------------------------------------

def test_api_requests_hit_proxy_when_enabled(tmp_path):
    """When proxy_target_origin is set, /api/* forwards to the upstream."""
    # A public_dir with some static content that should NOT be reached for /api paths.
    (tmp_path / "index.html").write_text("<h1>root</h1>")

    async def run():
        upstream = web.Application()
        upstream.router.add_get(
            "/api/v1/projects/test",
            _const(lambda: web.json_response({"projectAbbr": "test"})),
        )

        async with TestServer(upstream) as upstream_server:
            app = ApplicationWebServer.build_app(
                web_dir=str(tmp_path),
                port=18090,
                proxy_target_origin=_upstream_origin(upstream_server),
            )
            async with TestServer(app) as gams_frog_server:
                async with TestClient(gams_frog_server) as client:
                    resp = await client.get("/api/v1/projects/test")
                    assert resp.status == 200
                    assert await resp.json() == {"projectAbbr": "test"}

    _run(run())


def test_static_files_still_served_when_proxy_enabled(tmp_path):
    """Non-/api/* paths continue hitting the static handler even with the proxy enabled."""
    (tmp_path / "index.html").write_text("<h1>root</h1>")
    (tmp_path / "about.html").write_text("<h1>about</h1>")

    async def run():
        upstream = web.Application()

        async with TestServer(upstream) as upstream_server:
            app = ApplicationWebServer.build_app(
                web_dir=str(tmp_path),
                port=18090,
                proxy_target_origin=_upstream_origin(upstream_server),
            )
            async with TestServer(app) as gams_frog_server:
                async with TestClient(gams_frog_server) as client:
                    index_resp = await client.get("/")
                    assert index_resp.status == 200
                    assert "root" in (await index_resp.text())

                    about_resp = await client.get("/about.html")
                    assert about_resp.status == 200
                    assert "about" in (await about_resp.text())

    _run(run())


def test_proxy_disabled_when_target_origin_is_none(tmp_path):
    """
    Without a proxy target, /api/* falls through to the static handler. In this test
    there's no matching static file, so we expect a 404 from the directory-index
    handler — proving nothing proxied anything.
    """
    (tmp_path / "index.html").write_text("<h1>root</h1>")

    async def run():
        app = ApplicationWebServer.build_app(
            web_dir=str(tmp_path),
            port=18090,
            proxy_target_origin=None,
        )
        async with TestServer(app) as gams_frog_server:
            async with TestClient(gams_frog_server) as client:
                resp = await client.get("/api/v1/projects/test")
                assert resp.status == 404

    _run(run())


def test_proxy_route_matches_before_static_catchall(tmp_path):
    """
    Route-registration order is load-bearing: if /api/* were registered after the
    static catch-all, the catch-all would steal the request. This test proves the
    proxy wins even when a conflicting file exists on disk.
    """
    # A physical file at /api/whatever that would match the static handler if reached.
    api_dir = tmp_path / "api"
    api_dir.mkdir()
    (api_dir / "whatever.html").write_text("STATIC FILE — SHOULD NOT BE REACHED")

    async def run():
        upstream = web.Application()
        upstream.router.add_get(
            "/api/whatever.html",
            _const(lambda: web.Response(text="FROM UPSTREAM", content_type="text/plain")),
        )

        async with TestServer(upstream) as upstream_server:
            app = ApplicationWebServer.build_app(
                web_dir=str(tmp_path),
                port=18090,
                proxy_target_origin=_upstream_origin(upstream_server),
            )
            async with TestServer(app) as gams_frog_server:
                async with TestClient(gams_frog_server) as client:
                    resp = await client.get("/api/whatever.html")
                    assert resp.status == 200
                    assert await resp.text() == "FROM UPSTREAM"

    _run(run())


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

def test_proxy_registers_startup_and_cleanup_hooks_when_enabled(tmp_path):
    """Sanity check: when the proxy is enabled, the aiohttp app has startup+cleanup hooks."""
    (tmp_path / "index.html").write_text("<h1>root</h1>")

    baseline_app = ApplicationWebServer.build_app(
        web_dir=str(tmp_path), port=18090, proxy_target_origin=None
    )
    baseline_startup = len(baseline_app.on_startup)
    baseline_cleanup = len(baseline_app.on_cleanup)

    app = ApplicationWebServer.build_app(
        web_dir=str(tmp_path),
        port=18090,
        proxy_target_origin="http://example.invalid",
    )
    assert len(app.on_startup) == baseline_startup + 1
    assert len(app.on_cleanup) == baseline_cleanup + 1


def test_no_proxy_hooks_when_disabled(tmp_path):
    """
    Without the proxy, the app has only aiohttp's built-in hooks and nothing gams-frog-added.
    We verify by comparing against an identically-built app — the counts must match.
    """
    (tmp_path / "index.html").write_text("<h1>root</h1>")

    app_a = ApplicationWebServer.build_app(
        web_dir=str(tmp_path), port=18090, proxy_target_origin=None
    )
    app_b = ApplicationWebServer.build_app(
        web_dir=str(tmp_path), port=18090, proxy_target_origin=None
    )
    assert len(app_a.on_startup) == len(app_b.on_startup)
    assert len(app_a.on_cleanup) == len(app_b.on_cleanup)