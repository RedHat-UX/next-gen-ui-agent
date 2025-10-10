import logging
from typing import Any

from next_gen_ui_agent.input_data_transform.csv_input_data_transformer import (
    CsvCommaInputDataTransformer,
    CsvSemicolonInputDataTransformer,
    CsvTabInputDataTransformer,
)
from next_gen_ui_agent.input_data_transform.json_input_data_transformer import (
    JsonInputDataTransformer,
)
from next_gen_ui_agent.input_data_transform.types import InputDataTransformerBase
from next_gen_ui_agent.input_data_transform.yaml_input_data_transformer import (
    YamlInputDataTransformer,
)
from stevedore import ExtensionManager

logger = logging.getLogger(__name__)

PLUGGABLE_INPUT_DATA_TRANSFORMERS_NAMESPACE = (
    "next_gen_ui.agent.input_data_transformer_factory"
)
""" Stevedore namespace for the input data transformers."""

input_data_transformer_extension_manager = ExtensionManager(
    namespace=PLUGGABLE_INPUT_DATA_TRANSFORMERS_NAMESPACE,
    invoke_on_load=True,
)

logger.info(
    "Dynamically registered input data transformers: %s",
    input_data_transformer_extension_manager.names(),
)

# default transformers implemented in this module to be selected more efficiently
BUILTIN_INPUT_DATA_TRANSFORMERS: dict[str, InputDataTransformerBase] = {
    YamlInputDataTransformer.TRANSFORMER_NAME: YamlInputDataTransformer(),
    JsonInputDataTransformer.TRANSFORMER_NAME: JsonInputDataTransformer(),
    CsvCommaInputDataTransformer.TRANSFORMER_NAME: CsvCommaInputDataTransformer(),
    CsvSemicolonInputDataTransformer.TRANSFORMER_NAME: CsvSemicolonInputDataTransformer(),
    CsvTabInputDataTransformer.TRANSFORMER_NAME: CsvTabInputDataTransformer(),
}


def get_input_data_transformer(
    input_data_transformer_name: str,
) -> InputDataTransformerBase:
    """Get the input data transformer by name."""

    if input_data_transformer_name in BUILTIN_INPUT_DATA_TRANSFORMERS:
        return BUILTIN_INPUT_DATA_TRANSFORMERS[input_data_transformer_name]
    elif input_data_transformer_name in input_data_transformer_extension_manager:
        return input_data_transformer_extension_manager[  # type:ignore
            input_data_transformer_name
        ].obj
    else:
        raise KeyError(
            f"No input data transformer found for name: {input_data_transformer_name}"
        )


def perform_input_data_transformation(
    input_data_transformer_name: str, input_data: str | None
) -> Any:
    """Perform the input data transformation.
    Args:
        input_data_transformer_name: Name of the input data transformer to use.
        input_data: Input data string to transform.
    Returns:
        Object tree matching parsed JSON format.
    """

    if input_data is None:
        raise ValueError("Input data not provided")

    return get_input_data_transformer(input_data_transformer_name).transform(input_data)
