# Input data

This chapter contains rules for the format of the `Structured data` provided as an input to the *UI Agent*.
*Controlling assistant* or *Data providing agent* must provide data conforming to these rules to get good results from the *UI Agent*.
Non conforming data may work still to get reasonable `Data UI Block`, but results are not guaranteed.

## Data must be relevant for the User prompt

*UI Agent* expects that provided data are relevant to the current `User prompt`, as it generates UI which shows that data regarding to the user prompt. 
Results for unrelated data are not guaranteed.

## `InputData` fields

* `data` - string with structured backend data to be processed to UI component
* `type` - optional string identifier of the data piece type eg. `movies.movie-detail`, `movies.movies-list`, `movies.actor-detail`. It is up to *Controlling assistant*
   to define and use these types, but it might be a good idea to use tree like hierarchy here, and descriebe business meaning of the data. Other option is 
   to use name of the LLM tool used to load backend data, as implemented in some of our AI framework bindings.
   It is used to identify data type for multiple features like configurable component selection, input data transformation, input data JSON wrapping etc.

## JSON format

*UI Agent* expects [JSON formatted](https://datatracker.ietf.org/doc/html/rfc8259) input data. 
[JSONPath](https://www.rfc-editor.org/rfc/rfc9535.html) is used to get values from the data during the UI component rendering. 
So input data **MUST BE** in the JSON format.

## Field names

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

LLM used in the *UI Agent* struggles sometimes to generate correct paths pointing to the data values if they are stored directly in the root Object. 
*UI Agent* works correctly if there is an JSON Object in the data root, containing exactly one field, which name describes business nature of the data. 
This helps LLM to better understand the data, match them with the user prompt, and generate correct paths pointing to the data values. This field can then contain `Object` or `Array of objects`.

### Automatic JSON wrapping

If `InputData.type` field is provided, UI Agent automatically wraps problematic JSON structures the LLM struggles with ([see above](#data-root)). 
Data are wrapped into new root JSON object with `InputData.type` value used as a field name (after sanitization),
where the original JSON data are put into. 
It expects that type contains reasonable value, ideally describing the business meaning of the data, [see above](#inputdata-fields).

JSON wrapping is enabled by default, but can be disabled in the [UI Agent configuration](configuration.md#input_data_json_wrapping-bool-optional) if it causes some problems.

For example, input data with `type`=`movie.detail` and content:

```json
{
  "title": "Toy Story",
  "year": 2005
}
```

are wrapped as:

```json
{
  "movie_detail": {
    "title": "Toy Story",
    "year": 2005
  }
}
```

## One `Object` input data

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
Putting this structure into top level array (with one object only) is mostly interpreted as one `Object` with relevant UI component selected and generally works well.

Potentially problematic `Object` input data:
```json
{
  "id": 254,
  "orderDate": "2025-03-17",
  "price": "568",
  ...
}
```
Why not to use this structure? LLM is typically looking at the field name to understand what are the data about. 
And because this object is not stored in any field, LLM do not know so well what is this object about.

As of UI Agent `0.3.0`, [automatic JSON wrapping](#automatic-json-wrapping) is applied if enabled and data `type` is provided to prevent problems with this kind of data.

## `Array of objects` input data

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

Problematic `Array of objects` input data:
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
Why not to use this structure? We have to shorten arrays in input data before putting in into the LLM context, 
and in this case there is not a room where to put original array size necessary for correct UI compoennt selection, 
as we put it into name of the field the array is stored in.

As of UI Agent `0.3.0`, [automatic JSON wrapping](#automatic-json-wrapping) is applied if enabled and data `type` is provided to prevent problems with this kind of data.

!!! warning
    Array with one object only is typically interpreted as a single `Object` and relevant UI component is used to show it's values.

## Structure of objects in the `Array of objects`

In the `Array of objects` input data type, structure of all objects must be the same. The same fields MUST be present in all the objects (data pickup by JSONPath can be broken if not),
every field's value must be the same type in all the objects, but it can be `null` in some of them. 

It's because JSONPath is used to extract data values.


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

!!! warning
    Nesting `Array of objects` in the `Object` (except documented root) may be sometimes interpreted correctly, but it is not guaranteed and should be avoided.
    *UI Agent* can sometimes select specific UI component to render this `Array of objects` only, but fields from the parent object are not rendered then. 
    But in many cases LLM of the *UI Agent* generates nonsense paths pointing to the values of this array.
    It is always better to provide this `Array of objects` as a separate input data, so two `Data UI Blocks` are shown, one for the parent `Object`, and one for the `Array of objects`.


## Data value types

Data value type is important for formating during visualization. Details depend on used frontend technology etc. 
Some data value types are also important for specific UI components as they may form heart of their functionality, e.g "Image URL" for `image` component.

Data field value can be `null` also in JSON.

### String

Data field value is interpreted as plain `string` until any other type applies.

### Number

[Number value](https://datatracker.ietf.org/doc/html/rfc8259#section-6) in the JSON data. Can be either Integer or Floating point number.

**ToDo** detection/conversion from JSON string value?

### Logic/Boolean value

[`true`/`false` value](https://datatracker.ietf.org/doc/html/rfc8259#section-3) in the JSON data.

**ToDo** detection/conversion from JSON string value?

### Date and time values

**ToDo** detection/conversion from JSON string value with different formats?

### Image URL

To interpret data field as an url pointing to the image, it must match any of this:

* data field value must be http/s url pointing to the file with [image extension defined in `IMAGE_URL_SUFFIXES`](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_agent/data_transform/types.py)
* data field value must be http/s url and data field name must end with [extension defined in `IMAGE_DATA_PATH_SUFFIXES`](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_agent/data_transform/types.py)

Field with Image URL is important for [`image`](data_ui_blocks/dynamic_components.md#image) component, but is used also in [`one-card`](data_ui_blocks/dynamic_components.md#card) to show optional main image.

### Audio URL

**ToDo** `audio-player` component impl

### Video URL

**ToDo** [`video-player`](data_ui_blocks/dynamic_components.md#video-player) component impl

### Other URL

Other URL's are treated as a normal data values. UI components can render url as a link or action button.

### Enum value

**ToDo** implementation of value formating with "Data hints" for enums


## Data hints using metadata

**ToDo** this feature is not implemented yet, but it is necessary eg. to show nicely enum values etc. Stay tuned.
