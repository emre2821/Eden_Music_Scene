from EdenOS_EchoShare.echoplay_prequel_complete_build import GUI_AVAILABLE, PlaylistApp


def test_playlist_app_build_and_loading_controls():
    app = PlaylistApp()

    screen = app.build()

    assert screen is not None
    assert hasattr(app, "topic_input")
    assert hasattr(app, "playlist_list")
    assert hasattr(app, "loading_container")

    app.show_loading("Uploading playlist")
    assert app.loading_container.opacity == 1
    assert app.loading_spinner.active is True
    assert app.loading_label.text == "Uploading playlist"

    app.hide_loading()
    assert app.loading_container.opacity == 0
    assert app.loading_spinner.active is False
    assert app.loading_label.text == ""
