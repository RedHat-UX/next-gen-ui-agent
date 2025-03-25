import json
import logging

from jsonpath_ng import parse  # type: ignore

from .types import InputData, UIComponentMetadata

logger = logging.getLogger(__name__)


def enhance_component_by_input_data(
    input_data: list[InputData], components: list[UIComponentMetadata]
):
    """Enhance component by input data."""
    for component in components:
        for field in component["fields"]:
            dp = field["data_path"]
            dp = dp if dp.startswith("$.") else f"$..{dp}"
            je = None
            try:
                je = parse(dp)
            except Exception:
                logger.exception("Failed JSONPath expression parsing for %s", dp)
                break
            for data in input_data:
                if data["id"] != component["id"]:
                    continue
                # TODO: Investigate why is problem with \n in content
                data_content = data["data"]
                try:
                    json_data = json.loads(data_content.replace("\n", ""))
                    field["data"] = [match.value for match in je.find(json_data)]
                    if field["data"] != []:
                        break
                except Exception:
                    logger.exception(
                        "Cannot match data and component JSONPath dp=%s data=%s",
                        dp,
                        data_content,
                    )
                    break
