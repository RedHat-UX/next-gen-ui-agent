import copy
import json
import logging
from typing import Any

from jsonpath_ng import parse  # type: ignore
from next_gen_ui_agent.data_transform.audio import AudioPlayerDataTransformer
from next_gen_ui_agent.data_transform.chart_line import LineChartDataTransformer
from next_gen_ui_agent.data_transform.chart_pie import PieChartDataTransformer
from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.image import ImageDataTransformer
from next_gen_ui_agent.data_transform.one_card import OneCardDataTransformer
from next_gen_ui_agent.data_transform.set_of_cards import SetOfCardsDataTransformer
from next_gen_ui_agent.data_transform.table import TableDataTransformer
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.data_transform.video import VideoPlayerDataTransformer
from next_gen_ui_agent.types import DataFieldDataType, InputData, UIComponentMetadata

logger = logging.getLogger(__name__)

COMPONENT_TRANSFORMERS_REGISTRY: dict[str, DataTransformerBase] = {
    OneCardDataTransformer.COMPONENT_NAME: OneCardDataTransformer(),
    ImageDataTransformer.COMPONENT_NAME: ImageDataTransformer(),
    VideoPlayerDataTransformer.COMPONENT_NAME: VideoPlayerDataTransformer(),
    AudioPlayerDataTransformer.COMPONENT_NAME: AudioPlayerDataTransformer(),
    TableDataTransformer.COMPONENT_NAME: TableDataTransformer(),
    SetOfCardsDataTransformer.COMPONENT_NAME: SetOfCardsDataTransformer(),
    LineChartDataTransformer.COMPONENT_NAME: LineChartDataTransformer(),
    PieChartDataTransformer.COMPONENT_NAME: PieChartDataTransformer(),
}


def get_data_transformer(component: str) -> DataTransformerBase:
    """Get data transformer for UI component"""
    # TODO improve this by use of FactoryPattern instead of instance copy
    data_transformer = COMPONENT_TRANSFORMERS_REGISTRY.get(component)
    if data_transformer:
        data_transformer = copy.deepcopy(data_transformer)
        return data_transformer
    else:
        raise Exception(f"No data transformer found for component {component}")


def enhance_component_by_input_data(
    input_data: list[InputData], components: list[UIComponentMetadata]
) -> list[ComponentDataBase]:
    """Enhance component fields by values to be shown, taken from the data."""
    ret: list[ComponentDataBase] = []

    for component in components:
        for data in input_data:
            if data["id"] != component.id:
                continue

            # TODO call migrate data obtaining code into transformers

            # TODO some system error should be thrown if no data are found for the component["id"]
            data_content = data["data"]
            # TODO: Investigate why is problem with \n in content
            json_data = json.loads(data_content.replace("\n", ""))

            for field in component.fields:
                dp = field.data_path

                # patch occasional LLM errors
                if dp == "$":
                    dp = ""
                # TODO solve also case where path is like `$.fieldName`, simply remove that `$.` part
                # TODO solve paths like `$[*].id` for array component, it selects all id multiple times - this is why array in the data root doesn't work most the time!
                dp = (
                    dp
                    if not dp.startswith("$.{")
                    else dp.replace("$.{", "$..").replace("}", "")
                )

                # make sure data are picked
                dp = dp if dp.startswith("$.") else f"$..{dp}"
                je = None
                try:
                    je = parse(dp)
                except Exception:
                    logger.exception("Failed JSONPath expression parsing for %s", dp)
                    break

                try:
                    # TODO empty array is put into the field["data"] even if `data_path`` is invalid. Shouldn't it be `None` to distinguish from data field with empty array? Has consequence into `tests/ai_eval_components/eval.py`!
                    # TODO array seems to be put into the field["data"] even if `data_path`` is pointing to simple value
                    matched_data = [match.value for match in je.find(json_data)]
                    field.data = sanitize_matched_data(matched_data)
                except Exception:
                    logger.exception(
                        "Cannot match data and component JSONPath dp=%s data=%s",
                        dp,
                        data_content,
                    )
                    break

            data_transformer: DataTransformerBase = get_data_transformer(
                component.component
            )
            ret.append(data_transformer.process(component, data))

    return ret


def sanitize_matched_data(matched_data_list: list[Any]) -> list[DataFieldDataType]:
    """Check matched data if they match the expected layout and types"""
    result = matched_data_list

    # Array of array (NGUI-129)
    if len(matched_data_list) == 1 and isinstance(matched_data_list[0], list):
        result = matched_data_list[0]

    for index, matched_item in enumerate(result):
        if isinstance(matched_item, dict):
            result[index] = ", ".join(f"{k}: {v}" for k, v in matched_item.items())
        elif not isinstance(matched_item, DataFieldDataType):
            result[index] = str(matched_item)
        # TODO: Handle date, datetime

    return result
