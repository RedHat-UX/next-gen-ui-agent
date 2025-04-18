from abc import ABC, abstractmethod

from next_gen_ui_agent.renderer.renderer_base import StrategyFactory
from next_gen_ui_agent.renderer.renderer_json import JsonStrategyFactory
from next_gen_ui_agent.types import UIComponentMetadata
from pytest import fixture

@fixture
def strategy_factory():
    return JsonStrategyFactory()

def test_fields(strategy_factory):
    c = UIComponentMetadata(
        {
            "id": "test_id_1",
            "title": "Toy Story Details",
            "reasonForTheComponentSelection": "One item available in the data",
            "confidenceScore": "100%",
            "component": "one-card",
            "fields": [
                {"name": "DUMMY_NAME_VALUE", "data_path": "movie.title", "data": ["DUMMY_MOVIE_TITLE"]},
                {
                    "name": "DUMMY_POSTER_NAME",
                    "data_path": "movie.posterUrl",
                    "data": [
                        "DUMMY_IMG_URL"
                    ],
                },
            ],
        }
    )
    strategy = strategy_factory.get_render_strategy(c)
    result = strategy.render(c)
    assert "DUMMY_MOVIE_TITLE" in result
    assert "DUMMY_IMG_URL" in result
    assert "DUMMY_NAME_VALUE" in result
    assert "DUMMY_POSTER_NAME" in result

