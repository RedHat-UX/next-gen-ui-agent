from streamlit.testing.v1 import AppTest


def test_renderers_options():
    at = AppTest.from_file("dev_console.py").run()
    assert at.selectbox("renderer_select").options == ["rhds", "json", "patternfly"]


def test_rendering_json():
    at = AppTest.from_file("dev_console.py")
    at.session_state.renderer = "json"
    at.run()
    assert at.text[1].value == "Rendering DONE: json"
    # test that author value is in the agent output
    assert "Tom Hanks" in at.code[0].value


def test_rendering_rhds():
    at = AppTest.from_file("dev_console.py")
    at.session_state.renderer = "rhds"
    at.run()
    assert at.text[1].value == "Rendering DONE: rhds"
    # No way how to get custom component


def test_rendering_rhds_image():
    at = AppTest.from_file("dev_console.py")
    at.session_state.renderer = "rhds"
    at.session_state.example_code = "image"
    at.run()
    assert at.text[1].value == "Rendering DONE: rhds"
    # No way how to get custom component


def test_rendering_rhds_video():
    at = AppTest.from_file("dev_console.py")
    at.session_state.renderer = "rhds"
    at.session_state.example_code = "video-player"
    at.run()
    assert at.text[1].value == "Rendering DONE: rhds"
    # No way how to get custom component
