import json

from next_gen_ui_agent.data_transform.data_transformer_utils import (
    fill_fields_with_array_data,
    fill_fields_with_simple_data,
    find_image,
    get_data_value_for_path,
    sanitize_data_path,
)
from next_gen_ui_agent.data_transform.types import (
    ComponentDataBaseWithArrayValueFileds,
    ComponentDataBaseWithSimpleValueFileds,
    DataFieldArrayValue,
    DataFieldSimpleValue,
)


def test_sanitize_data_path() -> None:
    # empty paths handling to None
    assert sanitize_data_path(None) is None
    assert sanitize_data_path("") is None
    assert sanitize_data_path(" ") is None
    assert sanitize_data_path("  ") is None

    # path stripping
    assert sanitize_data_path("$movie.title   ") == "$..movie.title"
    assert sanitize_data_path("   $movie.title") == "$..movie.title"
    assert sanitize_data_path(" $movie.title    ") == "$..movie.title"

    # $ and { } handling
    assert (
        sanitize_data_path("$") is None
    )  # $ only path leads to empty string so data are not obtained at all
    assert (
        sanitize_data_path("$..movie.title") == "$..movie.title"
    )  # in all other cases output must start with `$..`
    assert sanitize_data_path("$.movie.title") == "$..movie.title"
    assert sanitize_data_path("$movie.title") == "$..movie.title"
    assert (
        sanitize_data_path("$..{movie.title}") == "$..movie.title"
    )  # make sure `{` and `}` are removed
    assert sanitize_data_path("$.{movie.title}") == "$..movie.title"
    assert sanitize_data_path("${movie.title}") == "$..movie.title"
    assert sanitize_data_path("{movie.title}") == "$..movie.title"

    # [*] handling
    assert (
        sanitize_data_path("movie.title[*]") == "$..movie.title"
    )  # one `[*]` at the end is removed as it selects content of the array into main returned array
    assert (
        sanitize_data_path("movie.title[*].id") == "$..movie.title[*].id"
    )  # one `[*]` inside of the path is kept
    assert (
        sanitize_data_path("movie.title[].id") == "$..movie.title[*].id"
    )  # invalid `[]` is replaced with valid `[*]`
    assert (
        sanitize_data_path("movie[].title[].id") is None
    )  # multiple array accesses are not allowed
    assert sanitize_data_path("movie[*].title[].id") is None
    assert sanitize_data_path("movie[].title[*].id") is None
    assert sanitize_data_path("movie[*].title[*].id") is None
    assert (
        sanitize_data_path("movie[].title[]") == "$..movie[*].title"
    )  # this is the only case multiple `[]` are allowed as last one is removed
    assert sanitize_data_path("movie[*].title[*]") == "$..movie[*].title"

    assert (
        sanitize_data_path("[*].string") == "$..[*].string"
    )  # array in the root is allowed
    assert (
        sanitize_data_path("$[*].string") == "$..[*].string"
    )  # array in the root is allowed
    assert (
        sanitize_data_path("$.[*].string") == "$..[*].string"
    )  # array in the root is allowed
    assert (
        sanitize_data_path("[].string") == "$..[*].string"
    )  # array in the root is allowed
    assert (
        sanitize_data_path("$[].string") == "$..[*].string"
    )  # array in the root is allowed
    assert (
        sanitize_data_path("$.[].string") == "$..[*].string"
    )  # array in the root is allowed

    # Handle paths with descriptive content in brackets
    assert (
        sanitize_data_path("subscriptions[size up to 6].name")
        == "$..subscriptions[*].name"
    )  # descriptive content in brackets should be replaced with [*]
    assert (
        sanitize_data_path("users[first user].email") == "$..users[*].email"
    )  # descriptive content in brackets should be replaced with [*]
    assert (
        sanitize_data_path("items[0].title") == "$..items[0].title"
    )  # numeric indices should be preserved
    assert (
        sanitize_data_path("items[134].title") == "$..items[134].title"
    )  # numeric indices should be preserved
    assert (
        sanitize_data_path("products[0 best seller].price") == "$..products[*].price"
    )  # descriptive content should be replaced
    assert (
        sanitize_data_path("orders[latest order].items[0].name") is None
    )  # multiple array accesses are not allowed (descriptive + numeric)
    assert (
        sanitize_data_path("customers[active users][0].profile") is None
    )  # multiple array accesses are not allowed (descriptive + numeric)


def test_get_data_value_for_path_INVALID() -> None:
    data = json.loads(
        """
    {
        "movie":{
            "nested": {
                "title": "Toy Story 2"
            },
            "title": "Toy Story"
        }
    }
    """
    )
    assert get_data_value_for_path(None, data) is None
    assert get_data_value_for_path("", data) is None
    assert get_data_value_for_path("  ", data) is None


def test_get_data_value_for_path_NESTING_SIMPLE_OBJECT() -> None:
    data = json.loads(
        """
    {
        "movie":{
            "nested": {
                "title": "Toy Story 2"
            },
            "title": "Toy Story"
        }
    }
    """
    )
    assert get_data_value_for_path("$..title", data) == ["Toy Story"]
    assert get_data_value_for_path("$..nested.title", data) == ["Toy Story 2"]


def test_get_data_value_for_path_NESTING_ARRAY() -> None:
    data = json.loads(
        """
    {
        "movies": [
            {
                "nested": {
                    "title": "Toy Story 2"
                },
                "title": "Toy Story"
            },
            {
                "nested": {
                    "title": "Toy Story 4"
                },
                "title": "Toy Story 3"
            }
        ]
    }"""
    )
    assert get_data_value_for_path("$..[*].title", data) == ["Toy Story", "Toy Story 3"]
    assert get_data_value_for_path("$..nested.title", data) == [
        "Toy Story 2",
        "Toy Story 4",
    ]


def test_get_data_value_for_path_ARRAY_IN_ROOT() -> None:
    data = json.loads(
        """
     [
        {
            "nested": {
                "title": "Toy Story 2"
            },
            "title": "Toy Story"
        },
        {
            "title": "Toy Story 3",
            "nested": {
                "title": "Toy Story 4"
            }
        }
    ]"""
    )
    assert get_data_value_for_path("$..[*].title", data) == ["Toy Story", "Toy Story 3"]
    assert get_data_value_for_path("$..[*].nested.title", data) == [
        "Toy Story 2",
        "Toy Story 4",
    ]


SIMPLE_OBJECT = json.loads(
    """
{
    "movie":{
      "arrayempty":[],
      "numberint":1995,
      "nested": {
        "string":"0114709",
        "numberfloat":8.3,
        "numberint":591836
      },
      "arrayonestring":["USA"],
      "string":"Toy Story",
      "boolean": true,
      "url":"https://themoviedb.org/movie/862",
      "date":"1995-11-22",
      "arrayofstrings":[
        "Jim Varney",
        "Tim Allen",
        "Tom Hanks",
        "Don Rickles"
      ],
      "arrayofobjects":[
        {"id":1},
        {"id":2},
        {"id":3},
        {"id":4}
      ],
      "nullfield": null
    }
}
"""
)


def test_fill_fields_with_data_SIMPLE_OBJECT() -> None:
    fields: list[
        DataFieldSimpleValue
    ] = ComponentDataBaseWithSimpleValueFileds.model_validate(
        {
            "id": "1",
            "component": "one-card",
            "title": "Toy Story Details",
            "fields": [
                {"name": "String", "data_path": "movie.string"},
                {"name": "Number Int", "data_path": "movie.numberint"},
                {
                    "name": "Nested number float",
                    "data_path": "movie.nested.numberfloat",
                },
                {"name": "Boolean", "data_path": "movie.boolean"},
                {"name": "Date", "data_path": "movie.date"},
                {"name": "Array of strings", "data_path": "arrayofstrings[*]"},
                {"name": "Array of strings without [*]", "data_path": "arrayofstrings"},
                {"name": "Array one string", "data_path": "movie.arrayonestring[*]"},
                {"name": "Empty array", "data_path": "arrayempty[*]"},
                {"name": "Null Field", "data_path": "nullfield"},
                {"name": "Unknown Field", "data_path": "movie.unknownfield"},
                {
                    "name": "Unknown Array Field",
                    "data_path": "movie.nested.unknownarray[*]",
                },
                {
                    "name": "One subfield from array of objects",
                    "data_path": "arrayofobjects[*].id",
                },
                {"name": "Nested object", "data_path": "movie.nested"},
                {
                    "name": "Objects from array of objects",
                    "data_path": "arrayofobjects[*]",
                },
            ],
        }
    ).fields

    fill_fields_with_simple_data(fields, SIMPLE_OBJECT)

    assert fields[0].data == ["Toy Story"]  # String
    assert fields[1].data == [1995]  # Number Int
    assert fields[2].data == [8.3]  # Nested number float
    assert fields[3].data == [True]  # Boolean
    assert fields[4].data == ["1995-11-22"]  # Date
    assert fields[5].data == [
        "Jim Varney",
        "Tim Allen",
        "Tom Hanks",
        "Don Rickles",
    ]  # Array of strings
    assert fields[6].data == [
        "Jim Varney",
        "Tim Allen",
        "Tom Hanks",
        "Don Rickles",
    ]  # Array of strings from path without [*] - is updated by sanitization
    assert fields[7].data == ["USA"]  # Array one string
    assert fields[8].data == []  # Empty array in the field
    assert (
        fields[9].data == []
    )  # Null field leads to None from JSONPath, which is removed by sanitization
    assert (
        fields[10].data == []
    )  # Unknown field - this is not good for evaluations as we can't distinguish between fields with empty array and unknown field, but what to do :-(
    assert (
        fields[11].data == []
    )  # Unknown array field - this is not good for evaluations as we can't distinguish between fields with empty array and unknown field, but what to do :-(
    assert fields[12].data == [1, 2, 3, 4]  # One subfield from array of objects
    assert (
        fields[13].data == []
    )  # Nested object - is removed by sanitization so array stays empty
    assert (
        fields[14].data == []
    )  # Objects from array of objects - are removed by sanitization so array stays empty


ARRAY = json.loads(
    """
{ "movies":
  [
    {
      "arrayempty":[],
      "arrayemptyinoneitem":[],
      "numberint":1995,
      "nested": {
        "string":"0114709",
        "numberfloat":8.3,
        "numberint":591836
      },
      "arrayonestring":["USA"],
      "string":"Toy Story",
      "boolean": true,
      "url":"https://themoviedb.org/movie/862",
      "date":"1995-11-22",
      "arrayofstrings":[
        "Jim Varney",
        "Tim Allen",
        "Tom Hanks",
        "Don Rickles"
      ],
      "arrayofobjects":[
        {"id":1},
        {"id":2},
        {"id":3},
        {"id":4}
      ],
      "nullfield": null,
      "nullfieldinoneonly": null
    },
    {
      "arrayempty":[],
      "arrayemptyinoneitem":["EMPTY_ARRAY_HAS_VALUE_IN_2"],
      "numberint":1996,
      "nested": {
        "string":"0114710",
        "numberfloat":8.4,
        "numberint":591838
      },
      "arrayonestring":["CZE"],
      "string":"Toy Story 2",
      "boolean": false,
      "url":"https://themoviedb.org/movie/870",
      "date":"1995-11-23",
      "arrayofstrings":["John Doe"],
      "arrayofobjects":[
        {"id":10},
        {"id":20},
        {"id":30},
        {"id":40}
      ],
      "nullfield": null,
      "nullfieldinoneonly": "aser",
      "fieldinsecondonly": "FIELD_IN_SECOND_ONLY"
    }
  ]
}
"""
)


def test_fill_fields_with_data_ARRAY() -> None:
    fields: list[
        DataFieldArrayValue
    ] = ComponentDataBaseWithArrayValueFileds.model_validate(
        {
            "id": "1",
            "component": "set-of-card",
            "title": "Toy Story Details",
            "fields": [
                {"name": "String", "data_path": "movies[*].string"},
                {"name": "Number Int", "data_path": "movies[*].numberint"},
                {
                    "name": "Nested number float",
                    "data_path": "movies[*].nested.numberfloat",
                },
                {"name": "Boolean", "data_path": "movies[*].boolean"},
                {"name": "Date", "data_path": "movies[*].date"},
                {"name": "Array of strings", "data_path": "movies[*].arrayofstrings"},
                {
                    "name": "Array of strings with [*]",
                    "data_path": "movies[*].arrayofstrings[*]",
                },
                {"name": "Array one string", "data_path": "movies[*].arrayonestring"},
                {"name": "Empty array", "data_path": "movies[*].arrayempty"},
                {"name": "Null Field", "data_path": "movies[*].nullfield"},
                {
                    "name": "Null Field in one only",
                    "data_path": "movies[*].nullfieldinoneonly",
                },
                {"name": "Unknown Field", "data_path": "movies[*].unknownfield"},
                {
                    "name": "Field in second only",
                    "data_path": "movies[*].fieldinsecondonly",
                },
                {
                    "name": "Unknown Array Field",
                    "data_path": "movies[*].nested.unknownarray[*]",
                },
                {"name": "Array of objects", "data_path": "movies[*].arrayofobjects"},
                {
                    "name": "Array of strings with []",
                    "data_path": "movies[*].arrayofstrings[*]",
                },
                {
                    "name": "One subfield from array of objects",
                    "data_path": "movies[*].arrayofobjects[*].id",
                },
            ],
        }
    ).fields

    fill_fields_with_array_data(fields, ARRAY)

    assert fields[0].data == ["Toy Story", "Toy Story 2"]  # String
    assert fields[1].data == [1995, 1996]  # Number Int
    assert fields[2].data == [8.3, 8.4]  # Nested number float
    assert fields[3].data == [True, False]  # Boolean
    assert fields[4].data == ["1995-11-22", "1995-11-23"]  # Date
    assert fields[5].data == [
        ["Jim Varney", "Tim Allen", "Tom Hanks", "Don Rickles"],
        ["John Doe"],
    ]  # Array of strings
    assert fields[6].data == [
        ["Jim Varney", "Tim Allen", "Tom Hanks", "Don Rickles"],
        ["John Doe"],
    ]  # Array of strings with [*] at the end of path - patched by JSONPath sanitization
    assert fields[7].data == [["USA"], ["CZE"]]  # Array one string
    assert fields[8].data == [
        None,
        None,
    ]  # field with Empty array - patched in sanitization to None
    assert fields[9].data == [None, None]  # Null Field
    assert fields[10].data == [None, "aser"]  # Null Field in one only
    assert fields[11].data == []  # Unknown Field leads to empty array
    assert fields[12].data == [
        "FIELD_IN_SECOND_ONLY"
    ]  # Field in second object only - mentioned in input data requirements as not allowed as it completelly breaks data consistency
    assert fields[13].data == []  # Unknown Array Field leads to an empty array
    assert fields[14].data == [
        None,
        None,
    ]  # array of objects - patched in sanitization to None
    assert fields[15].data == [
        ["Jim Varney", "Tim Allen", "Tom Hanks", "Don Rickles"],
        ["John Doe"],
    ]  # Array of strings with [*] at the end of path - patched in JSONPath sanitization
    assert (
        fields[16].data == []
    )  # one subfield from array of objects - patched in JSONPath sanitization to retun empty array so we can detect the error


ARRAY_IN_ROOT = json.loads(
    """
[
    {
      "arrayempty":[],
      "arrayemptyinoneitem":[],
      "numberint":1995,
      "nested": {
        "stringf":"0114709",
        "numberint":591836
      },
      "arrayonestring":["USA"],
      "stringf":"Toy Story",
      "boolean": true,
      "url":"https://themoviedb.org/movie/862",
      "date":"1995-11-22",
      "arrayofstrings":[
        "Jim Varney",
        "Tim Allen",
        "Tom Hanks",
        "Don Rickles"
      ],
      "arrayofobjects":[
        {"id":1},
        {"id":2},
        {"id":3},
        {"id":4}
      ],
      "nullfield": null,
      "nullfieldinoneonly": null
    },
    {
      "arrayempty":[],
      "arrayemptyinoneitem":["EMPTY_ARRAY_HAS_VALUE_IN_2"],
      "numberint":1996,
      "nested": {
        "stringf":"0114710",
        "numberint":591838
      },
      "arrayonestring":["CZE"],
      "stringf":"Toy Story 2",
      "boolean": false,
      "url":"https://themoviedb.org/movie/870",
      "date":"1995-11-23",
      "arrayofstrings":["John Doe"],
      "arrayofobjects":[
        {"id":10},
        {"id":20},
        {"id":30},
        {"id":40}
      ],
      "nullfield": null,
      "nullfieldinoneonly": "aser",
      "fieldinsecondonly": "FIELD_IN_SECOND_ONLY"
    }
]
"""
)


def test_fill_fields_with_data_ARRAY_IN_ROOT() -> None:
    fields: list[
        DataFieldArrayValue
    ] = ComponentDataBaseWithArrayValueFileds.model_validate(
        {
            "id": "1",
            "component": "set-of-card",
            "title": "Toy Story Details",
            "fields": [
                {"name": "String", "data_path": "[*].stringf"},
                {"name": "Number Int", "data_path": "$..[*].numberint"},
                {
                    "name": "Nested number float",
                    "data_path": "[*].nested.numberfloat",
                },
                {"name": "Boolean", "data_path": "[*].boolean"},
                {"name": "Date", "data_path": "[*].date"},
                {"name": "Array of strings", "data_path": "[*].arrayofstrings"},
                {
                    "name": "Array of strings with [*]",
                    "data_path": "[*].arrayofstrings[*]",
                },
                {"name": "Array one string", "data_path": "[*].arrayonestring"},
                {"name": "Empty array", "data_path": "[*].arrayempty"},
                {"name": "Null Field", "data_path": "[*].nullfield"},
                {
                    "name": "Null Field in one only",
                    "data_path": "[*].nullfieldinoneonly",
                },
                {"name": "Unknown Field", "data_path": "[*].unknownfield"},
                {
                    "name": "Field in second only",
                    "data_path": "[*].fieldinsecondonly",
                },
                {
                    "name": "Unknown Array Field",
                    "data_path": "[*].nested.unknownarray[*]",
                },
                {"name": "Array of objects", "data_path": "[*].arrayofobjects"},
                {
                    "name": "Array of strings with []",
                    "data_path": "[*].arrayofstrings[*]",
                },
                {
                    "name": "One subfield from array of objects",
                    "data_path": "[*].arrayofobjects[*].id",
                },
            ],
        }
    ).fields

    fill_fields_with_array_data(fields, ARRAY_IN_ROOT)

    assert fields[0].data == ["Toy Story", "Toy Story 2"]  # String
    assert fields[1].data == [1995, 1996]  # Number Int
    assert (
        fields[2].data == []
    )  # Nested number float - not in data anymore as they cause Exception in JSONPath data pickup
    assert fields[3].data == [True, False]  # Boolean
    assert fields[4].data == ["1995-11-22", "1995-11-23"]  # Date
    assert fields[5].data == [
        ["Jim Varney", "Tim Allen", "Tom Hanks", "Don Rickles"],
        ["John Doe"],
    ]  # Array of strings
    assert fields[6].data == [
        ["Jim Varney", "Tim Allen", "Tom Hanks", "Don Rickles"],
        ["John Doe"],
    ]  # Array of strings with [*] at the end of path - patched by JSONPath sanitization
    assert fields[7].data == [["USA"], ["CZE"]]  # Array one string
    assert fields[8].data == [
        None,
        None,
    ]  # field with Empty array - patched in sanitization to None
    assert fields[9].data == [None, None]  # Null Field
    assert fields[10].data == [None, "aser"]  # Null Field in one only
    assert fields[11].data == []  # Unknown Field leads to empty array
    assert fields[12].data == [
        "FIELD_IN_SECOND_ONLY"
    ]  # Field in second object only - mentioned in input data requirements as not allowed as it completelly breaks data consistency
    assert fields[13].data == []  # Unknown Array Field leads to an empty array
    assert fields[14].data == [
        None,
        None,
    ]  # array of objects - patched in sanitization to None
    assert fields[15].data == [
        ["Jim Varney", "Tim Allen", "Tom Hanks", "Don Rickles"],
        ["John Doe"],
    ]  # Array of strings with [*] at the end of path - patched in JSONPath sanitization
    assert (
        fields[16].data == []
    )  # one subfield from array of objects - patched in JSONPath sanitization to retun empty array so we can detect the error


def test_find_image_BY_image_url_suffix() -> None:
    # add some non-image url fields and mixed case to test correct selection
    fields: list[
        DataFieldSimpleValue
    ] = ComponentDataBaseWithSimpleValueFileds.model_validate(
        {
            "id": "1",
            "component": "set-of-card",
            "title": "Toy Story Details",
            "fields": [
                {
                    "name": "String",
                    "data_path": "movies[*].string",
                    "data": ["https://image.tmdb.org/"],
                },
                {"name": "tLink", "data_path": "movies[*].stLink", "data": ["sdas"]},
                {
                    "name": "testLink",
                    "data_path": "movies[*].stringLink",
                    "data": ["https://image.tmdb.org/aajpg"],
                },
                {
                    "name": "Image",
                    "data_path": "movies[*].image",
                    "data": ["https://image.tmdb.org/test_path.jPg"],
                },
                {
                    "name": "Image URL",
                    "data_path": "movies[*].imageUrl",
                    "data": ["https://image.tmdb.org/test_path.svg"],
                },
                {
                    "name": "Image Link",
                    "data_path": "movies[*].imageLink",
                    "data": ["https://image.tmdb.org/test_path.png"],
                },
            ],
        }
    ).fields

    image, field = find_image(fields)
    assert image == "https://image.tmdb.org/test_path.jPg"
    assert field is not None
    assert field.name == "Image"


def test_find_image_BY_field_name_suffix_link() -> None:
    # add some non-image url fields and mixed case to test correct selection
    fields: list[
        DataFieldSimpleValue
    ] = ComponentDataBaseWithSimpleValueFileds.model_validate(
        {
            "id": "1",
            "component": "set-of-card",
            "title": "Toy Story Details",
            "fields": [
                {
                    "name": "String",
                    "data_path": "movies[*].string",
                    "data": ["https://image.tmdb.org/"],
                },
                {
                    "name": "Test",
                    "data_path": "movies[*].string_image_LINk",
                    "data": ["https://image.tmdb.org/aa"],
                },
                {
                    "name": "ImageLink",
                    "data_path": "movies[*].image",
                    "data": ["https://image.tmdb.org/test_path.jp"],
                },
            ],
        }
    ).fields

    image, field = find_image(fields)
    assert image == "https://image.tmdb.org/aa"
    assert field is not None
    assert field.name == "Test"


def test_find_image_BY_field_name_suffix_url() -> None:
    # add some non-image url fields and mixed case to test correct selection
    fields: list[
        DataFieldSimpleValue
    ] = ComponentDataBaseWithSimpleValueFileds.model_validate(
        {
            "id": "1",
            "component": "set-of-card",
            "title": "Toy Story Details",
            "fields": [
                {
                    "name": "String",
                    "data_path": "movies[*].string",
                    "data": ["https://image.tmdb.org/"],
                },
                {
                    "name": "Test",
                    "data_path": "movies[*].posterUrL",
                    "data": ["https://image.tmdb.org/aa"],
                },
                {
                    "name": "ImageLink",
                    "data_path": "movies[*].image",
                    "data": ["https://image.tmdb.org/test_path.jp"],
                },
            ],
        }
    ).fields

    image, field = find_image(fields)
    assert image == "https://image.tmdb.org/aa"
    assert field is not None
    assert field.name == "Test"
