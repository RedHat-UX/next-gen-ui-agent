This chapter contains rules for the format of the `Structured data` provided as an input to the *UI Agent*.
*Controlling assistant* or *Data providing agent* must provide data conforming to these rules to get good results from the *UI Agent*.
Non conforming data may work still to get reasonable `Data UI Block`, but results are not guaranteed.

## Data must be relevant for the User prompt

*UI Agent* expects that provided data are relevant to the current `User prompt`, as it generates UI which shows that data regarding to the user prompt. 
Results for unrelated data are not guaranteed.

## JSON format

*UI Agent* expects [JSON formatted](https://datatracker.ietf.org/doc/html/rfc8259) input data. 
[JSONPath](https://www.rfc-editor.org/rfc/rfc9535.html) is used to get values from the data during the UI component rendering. 
So input data **MUST BE** in the JSON format.

## Data field names

LLM used in the *UI Agent* relies on the data field names heavily to understand what is the field value about, to use it correctly.
So descriptive field names explaining business reason of the value are crucial to get good results out of the *UI Agent*.

Do not use too abstract field names. Also try to avoid names with these terms (both singular and plural), as they are used in the system prompt and can confuse LLM:

* component
* item
* array
* data
* user query
* field
* path

You can use both camel case and sneak case field names.

## Data root

Type of the input data, [`Object`](https://datatracker.ietf.org/doc/html/rfc8259#section-4) or [`Array of objects`](https://datatracker.ietf.org/doc/html/rfc8259#section-5), is very important for the UI component selection. 
For `Object`, UI component rendering one item is selected, like `one-card`, `image`, `video-player`, `audio-player` etc. 
`Array of objects` is rendered by UI component like `set-of-card`, `table`, `chart`, `image-gallery`.

But LLM used in the *UI Agent* struggles to generate correct paths pointing to the data values if they are stored directly in the root Object. *UI Agent* works correctly if there is an JSON Object in the data root, containing exactly one field, which name describes business nature of the data. This helps LLM to better understand the data, match them with the user prompt, and generate correct paths pointing to the data values. This field can then contain `Object` or `Array of objects`.

### `Object` input data

Correct `Object` input data:
```json
{
  "order": {
    "id": 254,
    "orderDate": "2025-03-17",
    "price": "568USD",
    ...
  }
}
```

Incorrect `Object` input data:
```json
{
  "id": 254,
  "orderDate": "2025-03-17",
  "price": "568",
  ...
}
```

### `Array of objects` input data

Correct `Array of objects` input data:
```json
{
  "orders": [
    {
      "id": 254,
      "orderDate": "2025-03-17",
      "price": "568",
      ...
    },
    {
      "id": 2585,
      "orderDate": "2025-03-18",
      "price": "4628",
       ...
    }  
  ]
}
```

Incorrect `Array of objects` input data:
```json
[
  {
    "id": 254,
    "orderDate": "2025-03-17",
    "price": "568",
    ...
  },
  {
    "id": 2585,
    "orderDate": "2025-03-18",
    "price": "4628",
     ...
  }     
]
```

## Values nesting

Nesting `Object` in another `Object` is generally OK, LLM can generate correct paths pointing to the values.
```json
{
  "order": {
    "id": "ORT-4578",
    "product": {
      "name": "Good Bood",
      "brand": "Master Blaster",
      "price": "10"
    },
    ...
  }
}
```

You can also nest `Array of simple values` in the `Object` (even if the `Object` is an item in the `Array`), our rendering is capable to render them correctly.
```json
{
  "movie": {
    "languages": [ "English", "German" ],
    "year": 1995,
    ...
  }
}
```

Nesting `Array of objects` in the `Object` (except documented root) may be sometimes interpreted correctly, but it is not guaranteed and should be avoided.
*UI Agent* can sometimes select specific UI component to render this `Array of objects` only, but fields from the parent object are not rendered then. 
But in many cases LLM of the *UI Agent* generates nonsense paths pointing to the values of this array.
It is always better to provide this `Array of objects` as a separate input data, so two `Data UI Blocks` are shown, one for the parent `Object`, and one for the `Array of objects`.

## Data hints using metadata

**ToDo** this feature is not implemented yet, but it is necessary eg. to show nicely enum values etc. Stay tuned.
