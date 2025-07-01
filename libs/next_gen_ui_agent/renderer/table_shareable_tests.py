# Substantial portions of this file were generated with help of Cursor AI

from abc import ABC, abstractmethod

from next_gen_ui_agent.data_transform.types import ComponentDataTable
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory

SAMPLE_TABLE_DATA = {
    "id": "DUMMY_ID",
    "title": "DUMMY_MAIN_TITLE_VALUE",
    "component": "table",
    "fields": [
        {
            "name": "DUMMY_SIMPLE_FIELD_NAME",
            "data_path": "DUMMY_SIMPLE_FIELD_DATA_PATH",
            "data": ["DUMMY_VALUE_1", "DUMMY_VALUE_2"],
        },
        {
            "name": "DUMMY_ARRAY_FIELD_NAME",
            "data_path": "DUMMY_ARRAY_FIELD_DATA_PATH",
            "data": [
                ["DUMMY_NESTED_VALUE_1", "DUMMY_NESTED_VALUE_2"],
                ["DUMMY_NESTED_VALUE_3"],
            ],
        },
        {
            "name": "DUMMY_MIXED_FIELD_NAME",
            "data_path": "DUMMY_MIXED_FIELD_DATA_PATH",
            "data": [
                "DUMMY_SINGLE_VALUE",
                ["DUMMY_NESTED_VALUE_4", "DUMMY_NESTED_VALUE_5"],
            ],
        },
    ],
}


class BaseTableRendererTests(ABC):
    """Shareable table component tests.

    In order to have basic tests for your renderer, you can inherit from this class
    and implement the get_strategy_factory method. This class will then provide the
    basic tests for your renderer.

    Example:
        class TestTableJsonRendererWithShareableTests(BaseTableRendererTests):
            def get_strategy_factory(self) -> StrategyFactory:
                return JsonStrategyFactory()

    Note:
        If you intentionally want to omit one of the tests, you can override the test
        method with 'pass'.
    """

    @abstractmethod
    def get_strategy_factory(self) -> StrategyFactory:
        pass

    def _render_sample_table(self) -> str:
        c = ComponentDataTable.model_validate(SAMPLE_TABLE_DATA)
        strategy = self.get_strategy_factory().get_render_strategy(c)
        result = strategy.render(c)
        return result

    def test_renders_main_title_value(self):
        result = self._render_sample_table()
        assert "DUMMY_MAIN_TITLE_VALUE" in result

    def test_renders_simple_field_name(self):
        result = self._render_sample_table()
        assert "DUMMY_SIMPLE_FIELD_NAME" in result

    def test_renders_simple_field_values(self):
        result = self._render_sample_table()
        assert "DUMMY_VALUE_1" in result
        assert "DUMMY_VALUE_2" in result

    def test_renders_array_field_name(self):
        result = self._render_sample_table()
        assert "DUMMY_ARRAY_FIELD_NAME" in result

    def test_renders_array_field_values(self):
        result = self._render_sample_table()
        assert "DUMMY_NESTED_VALUE_1" in result
        assert "DUMMY_NESTED_VALUE_2" in result
        assert "DUMMY_NESTED_VALUE_3" in result

    def test_renders_mixed_field_name(self):
        result = self._render_sample_table()
        assert "DUMMY_MIXED_FIELD_NAME" in result

    def test_renders_mixed_field_values(self):
        result = self._render_sample_table()
        assert "DUMMY_SINGLE_VALUE" in result
        assert "DUMMY_NESTED_VALUE_4" in result
        assert "DUMMY_NESTED_VALUE_5" in result
