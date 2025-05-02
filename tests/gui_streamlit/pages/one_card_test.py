from streamlit.testing.v1 import AppTest


def test_case_fields():
    at = AppTest.from_file("one_card.py").run()
    assert at.subheader[0].value == "Multiple facts with no image"
    assert at.text[0].value == "Rendering DONE: rhds"


def test_case_one_field():
    at = AppTest.from_file("one_card.py").run()
    assert at.subheader[1].value == "One Fact"
    assert at.text[0].value == "Rendering DONE: rhds"


def test_case_image():
    at = AppTest.from_file("one_card.py").run()
    assert at.subheader[2].value == "Facts with image"
    assert at.text[0].value == "Rendering DONE: rhds"
