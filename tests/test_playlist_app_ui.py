"""Smoke tests ensuring the GUI app can be instantiated."""

from apps.backend.EdenOS_EchoShare.echoplay_prequel_complete_build import PlaylistApp


def _build_app():
    app = PlaylistApp()
    root = app.build()
    assert root is not None
    return app


def test_build_exposes_core_widgets():
    app = _build_app()

    assert hasattr(app, "topic_input")
    assert hasattr(app, "playlist_list")
    assert hasattr(app, "loading_container")
    assert hasattr(app, "loading_spinner")
    assert hasattr(app, "loading_label")


def test_loading_indicator_methods():
    app = _build_app()

    app.show_loading("Working...")
    assert app.loading_label.text == "Working..."
    assert app.loading_spinner.active is True
    assert app.loading_container.opacity == 1
    assert app.loading_container.height == app._loading_height

    app.hide_loading()
    assert app.loading_spinner.active is False
    assert app.loading_container.opacity == 0
    assert app.loading_container.height == 0
    assert app.loading_label.text == ""
