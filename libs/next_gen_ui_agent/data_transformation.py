import copy
import logging

from next_gen_ui_agent.data_transform.audio import AudioPlayerDataTransformer
from next_gen_ui_agent.data_transform.data_transformer import DataTransformerBase
from next_gen_ui_agent.data_transform.hand_build_component import (
    HandBuildComponentDataTransformer,
)
from next_gen_ui_agent.data_transform.image import ImageDataTransformer
from next_gen_ui_agent.data_transform.one_card import OneCardDataTransformer
from next_gen_ui_agent.data_transform.set_of_cards import SetOfCardsDataTransformer
from next_gen_ui_agent.data_transform.table import TableDataTransformer
from next_gen_ui_agent.data_transform.types import ComponentDataBase
from next_gen_ui_agent.data_transform.video import VideoPlayerDataTransformer
from next_gen_ui_agent.types import InputData, UIComponentMetadata

logger = logging.getLogger(__name__)

COMPONENT_TRANSFORMERS_REGISTRY: dict[str, DataTransformerBase] = {
    OneCardDataTransformer.COMPONENT_NAME: OneCardDataTransformer(),
    ImageDataTransformer.COMPONENT_NAME: ImageDataTransformer(),
    VideoPlayerDataTransformer.COMPONENT_NAME: VideoPlayerDataTransformer(),
    AudioPlayerDataTransformer.COMPONENT_NAME: AudioPlayerDataTransformer(),
    TableDataTransformer.COMPONENT_NAME: TableDataTransformer(),
    SetOfCardsDataTransformer.COMPONENT_NAME: SetOfCardsDataTransformer(),
    HandBuildComponentDataTransformer.COMPONENT_NAME: HandBuildComponentDataTransformer(),
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
            # TODO ERRHANDLING system error should be returned if no data are found for the component["id"]

            data_transformer: DataTransformerBase = get_data_transformer(
                component.component
            )
            ret.append(data_transformer.process(component, data))

    return ret
