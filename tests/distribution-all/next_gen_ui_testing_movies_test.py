from next_gen_ui_testing import data_set_movies

def test_find_movie() -> None:
    result = data_set_movies.find_movie("Toy Story")
    m = result[0]["movie"]
    assert m["title"] == "Toy Story"
