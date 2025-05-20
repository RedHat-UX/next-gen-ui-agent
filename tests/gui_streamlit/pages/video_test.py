from streamlit.testing.v1 import AppTest


def test_video():
    at = AppTest.from_file("video.py").run()
    assert at.subheader[0].value == "Video from YouTube"
    assert at.subheader[1].value == "No Video"
    assert at.text[0].value == "Rendering DONE: rhds"
