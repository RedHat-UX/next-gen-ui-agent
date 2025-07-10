# Substantial portions of this file were generated with help of Cursor AI

from collections.abc import Iterable
from typing import Any

MAX_ITEMS_IN_ARRAY = 2


def reduce_arrays(data: Any, size_boundary: int = 0) -> Any:
    """
    Recursively traverse the input data structure, reduce all iterables size to `MAX_ITEMS_IN_ARRAY` items,
    and rename the field to:
    * `field_name[size: x]` if `size_boundary` is 0, where `x` is the original iterable size.
    * `field_name[size over b]` if `size_boundary` is greater than 0 and original size is greater than `size_boundary`, where `b` is the `size_boundary`.
    * `field_name[size up to b]` if `size_boundary` is greater than 0 and original size is less than or equal to `size_boundary`, where `b` is the `size_boundary`.

    Returns:
        The processed data structure with iterables reduced and renamed. Data structure is copied inside, input structure stays unaltered.
    """
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            if isinstance(v, Iterable) and not isinstance(
                v, (str, bytes, bytearray, dict)
            ):
                # Convert to list to get length and slice
                iterable_list = list(v)
                original_size = len(iterable_list)
                inbracket = ""
                if size_boundary < 1:
                    inbracket = f"size: {original_size}"
                else:
                    if original_size > size_boundary:
                        inbracket = f"size over {size_boundary}"
                    else:
                        inbracket = f"size up to {size_boundary}"

                new_key = f"{k}[{inbracket}]"
                # Reduce each element in the iterable if they are dicts/iterables
                reduced_items = [
                    reduce_arrays(item) for item in iterable_list[:MAX_ITEMS_IN_ARRAY]
                ]
                new_dict[new_key] = reduced_items
            else:
                new_dict[k] = reduce_arrays(v, size_boundary)
        return new_dict
    elif isinstance(data, Iterable) and not isinstance(
        data, (str, bytes, bytearray, dict)
    ):
        # For iterables not directly under a dict key, reduce and process elements also
        iterable_list = list(data)
        return [
            reduce_arrays(item, size_boundary)
            for item in iterable_list[:MAX_ITEMS_IN_ARRAY]
        ]
    else:
        return data
