from abc import ABC, abstractmethod

from next_gen_ui_agent.data_transform.types import ComponentDataDataView
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory

SAMPLE_DATA_VIEW_DATA = {
    "id": "DUMMY_ID",
    "title": "DUMMY_MAIN_TITLE_VALUE",
    "component": "data-view",
    "fields": [
        {
            "id": "DUMMY_FIELD1_DATA_PATH",
            "name": "DUMMY_FIELD1_NAME",
            "data_path": "DUMMY_FIELD1_DATA_PATH",
            "data": ["DUMMY_FIELD1_VALUE1", "DUMMY_FIELD1_VALUE2"],
        },
        {
            "id": "DUMMY_FIELD2_DATA_PATH",
            "name": "DUMMY_FIELD2_NAME",
            "data_path": "DUMMY_FIELD2_DATA_PATH",
            "data": ["DUMMY_FIELD2_VALUE1", "DUMMY_FIELD2_VALUE2"],
        },
    ],
}


class BaseDataViewRendererTests(ABC):
    """Shareable data-view component tests.

    In order to have basic tests for your renderer, you can inherit from this class
    and implement the get_strategy_factory method. This class will then provide the
    basic tests for your renderer.

    Example:
        class TestDataViewJsonRendererWithShareableTests(BaseDataViewRendererTests):
            def get_strategy_factory(self) -> StrategyFactory:
                return JsonStrategyFactory()

    Note:
        If you intentionally want to omit one of the tests, you can override the test
        method with 'pass'.
    """

    @abstractmethod
    def get_strategy_factory(self) -> StrategyFactory:
        pass

    def _render_sample_data_view(self) -> str:
        c = ComponentDataDataView.model_validate(SAMPLE_DATA_VIEW_DATA)
        strategy = self.get_strategy_factory().get_render_strategy(c)
        result = strategy.render(c)
        return result

    def test_renders_main_title_value(self):
        """Test that the component title is rendered."""
        result = self._render_sample_data_view()
        assert "DUMMY_MAIN_TITLE_VALUE" in result

    def test_renders_field1_name(self):
        """Test that the first field name is rendered."""
        result = self._render_sample_data_view()
        assert "DUMMY_FIELD1_NAME" in result

    def test_renders_field1_values(self):
        """Test that all values from the first field are rendered."""
        result = self._render_sample_data_view()
        assert "DUMMY_FIELD1_VALUE1" in result
        assert "DUMMY_FIELD1_VALUE2" in result

    def test_renders_field2_name(self):
        """Test that the second field name is rendered."""
        result = self._render_sample_data_view()
        assert "DUMMY_FIELD2_NAME" in result

    def test_renders_field2_values(self):
        """Test that all values from the second field are rendered."""
        result = self._render_sample_data_view()
        assert "DUMMY_FIELD2_VALUE1" in result
        assert "DUMMY_FIELD2_VALUE2" in result

    def test_renders_all_fields(self):
        """Test that all field names are present in the output."""
        result = self._render_sample_data_view()
        assert "DUMMY_FIELD1_NAME" in result
        assert "DUMMY_FIELD2_NAME" in result

    def test_renders_all_data_values(self):
        """Test that all data values from all fields are rendered."""
        result = self._render_sample_data_view()
        # Check all values are present
        assert "DUMMY_FIELD1_VALUE1" in result
        assert "DUMMY_FIELD1_VALUE2" in result
        assert "DUMMY_FIELD2_VALUE1" in result
        assert "DUMMY_FIELD2_VALUE2" in result
