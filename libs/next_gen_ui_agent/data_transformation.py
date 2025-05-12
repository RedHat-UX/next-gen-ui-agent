import json
import logging

from jsonpath_ng import parse  # type: ignore
from next_gen_ui_agent.types import InputData, UIComponentMetadata

logger = logging.getLogger(__name__)


def enhance_component_by_input_data(
    input_data: list[InputData], components: list[UIComponentMetadata]
):
    """Enhance component fields by values to be shown, taken from the data."""
    for component in components:
        for data in input_data:
            if data["id"] != component.id:
                continue
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
                    field.data = [match.value for match in je.find(json_data)]
                except Exception:
                    logger.exception(
                        "Cannot match data and component JSONPath dp=%s data=%s",
                        dp,
                        data_content,
                    )
                    break
