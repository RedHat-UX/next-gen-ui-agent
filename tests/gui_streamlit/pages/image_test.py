from streamlit.testing.v1 import AppTest


def test_image():
    at = AppTest.from_file("image.py").run()
    assert at.subheader[0].value == "Image with title"
    assert at.subheader[1].value == "No Image"
    assert at.text[0].value == "Rendering DONE: rhds"
