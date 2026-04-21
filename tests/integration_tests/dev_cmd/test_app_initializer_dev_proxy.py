"""
Tests the semantic shift introduced by the dev proxy in AppInitializer.configure:
  - dev mode with a port: GAMS_API_ORIGIN from config becomes proxy_target_origin,
    and ENV.GAMS_API_ORIGIN (template-visible) is rewritten to the local dev server.
  - build / stage modes: no proxy, ENV.GAMS_API_ORIGIN stays as the configured upstream.
"""
import os

from gams_frog.ssr.init.ApplicationContext import ApplicationContext
from gams_frog.ssr.init.AppInitializer import AppInitializer
from utils.TestGamsFrogProject import TestGamsFrogProject


def _configure(project: TestGamsFrogProject, mode: str, dev_server_port: int | None = None):
    """Run AppInitializer.configure and return the resulting ApplicationConfiguration."""
    original_dir = os.getcwd()
    try:
        os.chdir(project.project_dir)
        context = ApplicationContext()
        AppInitializer(context).configure(
            directory=str(project.project_dir),
            mode=mode,
            dev_server_port=dev_server_port,
        )
        return context.get_config()
    finally:
        os.chdir(original_dir)


def test_dev_mode_with_port_sets_proxy_target_to_configured_upstream(test_gams_frog_project):
    config = _configure(test_gams_frog_project, mode="dev", dev_server_port=18090)

    # The configured GAMS_API_ORIGIN is promoted to the proxy target.
    assert config.proxy_target_origin == TestGamsFrogProject.GAMS_API_ORIGIN


def test_dev_mode_with_port_rewrites_env_gams_origin_to_localhost(test_gams_frog_project):
    config = _configure(test_gams_frog_project, mode="dev", dev_server_port=18090)

    # Templates see the local dev server — not the upstream — so browser calls are same-origin.
    assert config.ENV.GAMS_API_ORIGIN == "http://localhost:18090"


def test_dev_mode_keeps_gams_host_as_real_upstream(test_gams_frog_project):
    """
    gams_host (server-side, used by Pyrilo + cache keys) must remain the real upstream
    regardless of dev proxy. Otherwise Pyrilo would pointlessly round-trip through
    localhost, and cache keys would shift when the dev port changes.
    """
    config = _configure(test_gams_frog_project, mode="dev", dev_server_port=18090)

    assert config.gams_host == TestGamsFrogProject.GAMS_API_ORIGIN


def test_dev_mode_without_port_does_not_activate_proxy(test_gams_frog_project):
    """Legacy behavior for dev without a port: no proxy, templates see the raw upstream."""
    config = _configure(test_gams_frog_project, mode="dev", dev_server_port=None)

    assert config.proxy_target_origin is None
    assert config.ENV.GAMS_API_ORIGIN == TestGamsFrogProject.GAMS_API_ORIGIN


def test_build_mode_does_not_set_proxy_target(test_gams_frog_project):
    config = _configure(test_gams_frog_project, mode="build")

    assert config.proxy_target_origin is None
    # Templates see the real upstream in build mode — deployed sites are same-origin
    # with the API anyway.
    assert config.ENV.GAMS_API_ORIGIN == TestGamsFrogProject.GAMS_API_ORIGIN


def test_stage_mode_does_not_set_proxy_target(test_gams_frog_project):
    config = _configure(test_gams_frog_project, mode="stage")

    assert config.proxy_target_origin is None
    assert config.ENV.GAMS_API_ORIGIN == TestGamsFrogProject.GAMS_API_ORIGIN


def test_dev_port_in_env_origin_matches_port_arg(test_gams_frog_project):
    """The port plumbed into configure must be the one templates see."""
    config = _configure(test_gams_frog_project, mode="dev", dev_server_port=3000)

    assert config.ENV.GAMS_API_ORIGIN == "http://localhost:3000"