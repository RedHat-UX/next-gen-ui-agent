import json

from jsonpath_ng import parse  # type: ignore

from .datamodel import InputData, UIComponentMetadata


def enhance_component_by_input_data(
    input_data: list[InputData], components: list[UIComponentMetadata]
):
    """Enhance component by input data."""
    for component in components:
        for field in component.fields:
            print(field)
            dp = field.data_path
            dp = dp if dp.startswith("$.") else f"$..{dp}"
            je = None
            try:
                je = parse(dp)
            except Exception as e:
                print(
                    f"Failed JSONPath expression parsing for {field.data_path} exception={e}"
                )
                break
            for data in input_data:
                if data.id != component.id:
                    continue
                # TODO: Investigate why is problem with \n in content
                try:
                    json_data = json.loads(data.data.replace("\n", ""))
                    field.data = [match.value for match in je.find(json_data)]
                    if field.data != []:
                        break
                except Exception as e:
                    print(
                        f"Cannot match data and component JSONPath dp={dp} data={data.data} exception={e}"
                    )
                    break
