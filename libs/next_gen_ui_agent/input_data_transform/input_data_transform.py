import logging
from typing import Any

from next_gen_ui_agent.input_data_transform.csv_input_data_transformer import (
    CsvCommaInputDataTransformer,
    CsvSemicolonInputDataTransformer,
    CsvTabInputDataTransformer,
)
from next_gen_ui_agent.input_data_transform.fwctable_input_data_transformer import (
    FwctableInputDataTransformer,
)
from next_gen_ui_agent.input_data_transform.json_input_data_transformer import (
    JsonInputDataTransformer,
)
from next_gen_ui_agent.input_data_transform.noop_input_data_transformer import (
    NoopInputDataTransformer,
)
from next_gen_ui_agent.input_data_transform.yaml_input_data_transformer import (
    YamlInputDataTransformer,
)
from next_gen_ui_agent.types import AgentConfig, InputData, InputDataTransformerBase
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
    NoopInputDataTransformer.TRANSFORMER_NAME: NoopInputDataTransformer(),
    FwctableInputDataTransformer.TRANSFORMER_NAME: FwctableInputDataTransformer(),
}


class InputDataTransformersConfig:
    default_data_transformer: str
    per_type_data_transformers: dict[str, str] = {}


c = InputDataTransformersConfig()
""" Global variable with data transformation configuration.
Filled from init_input_data_transformers function """


def init_input_data_transformers(config: AgentConfig) -> None:
    """Initialize the input data transformers."""

    # validate default data transformer
    tr = (
        config.data_transformer
        if config.data_transformer
        else JsonInputDataTransformer.TRANSFORMER_NAME
    )
    get_input_data_transformer(tr)
    c.default_data_transformer = tr

    c.per_type_data_transformers.clear()
    # parse and validate per type data transformers
    if config.data_types:
        for type, type_config in config.data_types.items():
            if type_config.data_transformer:
                get_input_data_transformer(type_config.data_transformer)
                c.per_type_data_transformers[type] = type_config.data_transformer


def get_input_data_transformer_name(input_data: InputData) -> str:
    """Get input data transformer name based on input data type."""
    if (
        c.per_type_data_transformers
        and input_data.get("type")
        and input_data["type"] in c.per_type_data_transformers
    ):
        transformer_name = c.per_type_data_transformers[input_data["type"]]
        if transformer_name:
            return transformer_name
    return c.default_data_transformer


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


def perform_input_data_transformation(input_data: InputData) -> tuple[Any, str]:
    """Perform the input data transformation with configured transformer - InputData.type or default transformer.
    Args:
        input_data: Input data to transform. Must contain InputData.data and optionally InputData.type`.
    Returns:
        * Object tree matching parsed JSON format produced by the transformer.
        * Transformer name used for the transformation.
    Raises:
        ValueError if InputData.data is None
        KeyError if configuredtransformer name is not found
    """

    if input_data.get("data") is None:
        raise ValueError("Input data not provided")

    transformer_name = get_input_data_transformer_name(input_data)
    transformer = get_input_data_transformer(transformer_name)
    return transformer.transform_input_data(input_data), transformer_name


def perform_input_data_transformation_with_transformer_name(
    input_data: InputData, transformer_name: str
) -> Any:
    """Perform the input data transformation with provided transformer name.
    Args:
        input_data: Input data to transform. Must contain InputData.data and optionally InputData.type if given transformer requires it (typically not).
        transformer_name: Transformer name to use for the transformation.
    Returns: Object tree matching parsed JSON format produced by the transformer.
    Raises:
        ValueError if InputData.data is None
        KeyError if provided transformer name is not found
    """

    if input_data.get("data") is None:
        raise ValueError("Input data not provided")

    transformer = get_input_data_transformer(transformer_name)
    return transformer.transform_input_data(input_data)
