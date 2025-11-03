import copy
import logging
from typing import cast

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


def get_data_transformer(component: str) -> DataTransformerBase[ComponentDataBase]:
    """Get data transformer for UI component"""
    # TODO improve this by use of FactoryPattern instead of instance copy?
    data_transformer = COMPONENT_TRANSFORMERS_REGISTRY.get(component)
    if data_transformer:
        data_transformer = copy.deepcopy(data_transformer)
        return cast(DataTransformerBase[ComponentDataBase], data_transformer)
    else:
        raise Exception(f"No data transformer found for component {component}")


def generate_component_data(
    input_data: InputData, component: UIComponentMetadata
) -> ComponentDataBase:
    """Generate component data from input data and component metadata"""
    data_transformer: DataTransformerBase[ComponentDataBase] = get_data_transformer(
        component.component
    )
    return data_transformer.process(component, input_data)
