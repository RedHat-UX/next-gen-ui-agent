import json
import logging

from next_gen_ui_agent import NextGenUIAgent, UIComponentMetadata

test_component: UIComponentMetadata = {
    "title": "Toy Story",
    "reasonForTheComponentSelection": "One item available in the data",
    "confidenceScore": "100%",
    "component": "one-card",
    "fields": [
        {"name": "Title", "data_path": "movie.title", "data": "Toy Story"},
        {"name": "Year", "data_path": "movie.year", "data": "1900"},
        {"name": "IMDB Rating", "data_path": "movie.imdbRating", "data": "222"},
    ],
    "id": "test-id",
}


def test_design_system_handler_default_json() -> None:
    agent = NextGenUIAgent()
    agent.design_system_handler([test_component])
    json_str = test_component["rendition"]
    result: UIComponentMetadata = json.loads(json_str)
    assert result["title"] == "Toy Story"
    assert result["fields"][0]["data"] == "Toy Story"
    assert result["fields"][1]["data"] == "1900"


def test_design_system_handler_rhds() -> None:
    agent = NextGenUIAgent()
    agent.design_system_handler([test_component], "rhds")
    # TODO: This is failing. no plugins are registered because of:
    # DEBUG:stevedore.extension:found extension EntryPoint(name='rhds', value='next_gen_ui_rhds_renderer:RhdsStrategyFactory', group='next_gen_ui.agent.renderer_factory')
    # ERROR:stevedore.extension:Could not load 'rhds': No module named 'jinja2'

    # rendition = test_component["rendition"]
    # assert "" == rendition


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    test_design_system_handler_rhds()
