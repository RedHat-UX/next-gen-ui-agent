from streamlit.testing.v1 import AppTest


def test_renderers_options():
    at = AppTest.from_file("app.py").run()
    assert at.selectbox[0].options == ["json", "rhds", "patternfly"]


def test_rendering_json():
    """A user increments the number input, then clicks Add"""
    at = AppTest.from_file("app.py").run()
    assert at.text[1].value == "Rendering DONE"
    # test that author value is in the agent output
    assert "Tom Hanks" in at.code[2].value
