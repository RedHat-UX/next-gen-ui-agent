from next_gen_ui_agent.component_selection_llm_strategy import trim_to_json


class TestTrimToJson:
    """Test cases for trim_to_json method."""

    def test_trim_to_json_basic_object(self):
        text = '{"name": "John", "age": 30}'
        result = trim_to_json(text)
        assert result == '{"name": "John", "age": 30}'

    def test_trim_to_json_basic_array(self):
        text = '["item1", "item2", "item3"]'
        result = trim_to_json(text)
        assert result == '["item1", "item2", "item3"]'

    def test_trim_to_json_around_object(self):
        text = 'Prefix {"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}} suffix'
        result = trim_to_json(text)
        assert (
            result
            == '{"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}}'
        )

    def test_trim_to_json_around_array(self):
        text = 'Prefix [ {"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}} ] suffix'
        result = trim_to_json(text)
        assert (
            result
            == '[ {"user": {"name": "John", "details": {"age": 30, "city": "NYC"}}} ]'
        )

    def test_trim_to_json_textonly(self):
        text = "Prefix suffix"
        result = trim_to_json(text)
        assert result == "Prefix suffix"

    def test_trim_to_json_text_with_think(self):
        text = 'Prefix </think> other text { "name": "John" } suffix'
        result = trim_to_json(text)
        assert result == '{ "name": "John" }'
