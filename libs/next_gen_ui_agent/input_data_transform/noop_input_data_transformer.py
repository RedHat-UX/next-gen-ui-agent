from typing import Any, Literal

from next_gen_ui_agent.types import InputDataTransformerBase


class NoopInputDataTransformer(InputDataTransformerBase):
    """Noop Input Data transformer - keeps data as a `string`.
    Suitable for large data like parts of logs.

    Mostly for use with Hand Built Components, if LLM processing is necessary on this data,
    the `string` must be shortened and wrapped into JSON object.
    """

    TRANSFORMER_NAME = "noop"

    TRANSFORMER_NAME_LITERAL = Literal["noop"]

    def transform(self, input_data: str) -> Any:
        """
        This transformer is a no-op and returns the input data as is - as `string`.

        Args:
            input_data: Input data string to transform.
        Returns:
            The input data as is.
        """
        return input_data
