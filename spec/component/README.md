# UI Components Spec

Specification of the json format (as JSON Schema) of the `Data UI Blocks` produced by the *UI Agent* json UI renderer.
Mainly usefull to implement client-side renderers as they consume this format.

How relevant object types are generated to TypeScript then can be tested here: [https://transform.tools/json-schema-to-typescript](https://transform.tools/json-schema-to-typescript)

## Dynamic components for one `Object` input data

[Dynamic Components Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/data_ui_blocks/dynamic_components/)  
[One Object input data Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/input_data/structure/#one-object-input-data)

### One Card
[One Card JSON Schema](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/component/one-card.schema.json)

Example JSON output:
```json
{
  "component": "one-card",
  "id": "test-id",
  "title": "Toy Story Details",
  "image": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
  "fields": [
    {
      "data": [
        "Toy Story"
      ],
      "data_path": "movie.title",
      "name": "Title"
    },
    {
      "data": [
        1995
      ],
      "data_path": "movie.year",
      "name": "Year"
    },
    {
      "data": [
        8.3
      ],
      "data_path": "movie.imdbRating",
      "name": "IMDB Rating"
    },
    {
      "data": [
        "2022-11-02 00:00:00"
      ],
      "data_path": "movie.released",
      "name": "Release Date"
    },
    {
      "data": [
        "Jim Varney",
        "Tim Allen",
        "Tom Hanks",
        "Don Rickles"
      ],
      "data_path": "actors[*]",
      "name": "Actors"
    }
  ]
}
```

### Image
[JSON Schema](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/component/image.schema.json)

Example JSON output:
```json
{
  "component": "image",
  "id": "test-id",
  "image": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
  "title": "Toy Story Poster"
}
```

### Video Player
[JSON Schema](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/component/video-player.schema.json)

Example JSON output:
```json
{
  "component": "video-player",
  "id": "test-id",
  "title": "Toy Story Trailer",
  "video": "https://www.youtube.com/embed/v-PjgYDrg70",
  "video_img": "https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg"
}
```

## Dynamic components for `Array of objects` input data

[Dynamic Components Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/data_ui_blocks/dynamic_components/)  
[Array of objects input data Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/input_data/structure/#array-of-objects-input-data)

### Set Of Cards

[JSON Schema](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/component/set-of-cards.schema.json)

Example JSON output:
```json
{
  "component": "set-of-cards",
  "id": "test-id",
  "title": "My Favorite Movies",
  "fields": [
    {
      "data": [
        "Toy Story",
        "My Name is Khan"
      ],
      "data_path": "movie.title",
      "name": "Title"
    },
    {
      "data": [
        1995,
        2003
      ],
      "data_path": "movie.year",
      "name": "Year"
    },
    {
      "data": [
        8.3,
        8.5
      ],
      "data_path": "movie.imdbRating",
      "name": "IMDB Rating"
    },
    {
      "data": [
        [
          "Jim Varney",
          "Tim Allen",
          "Tom Hanks",
          "Don Rickles"
        ],[
          "Shah Rukh Khan",
          "Kajol Devgan"
        ]
      ],
      "data_path": "actors[*]",
      "name": "Actors"
    }
  ]
}
```

### Table

[JSON Schema](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/component/table.schema.json)

Example JSON output:
```json
{
  "component": "table",
  "id": "test-id",
  "title": "My Favorite Movies",
  "fields": [
    {
      "data": [
        "Toy Story",
        "My Name is Khan"
      ],
      "data_path": "movie.title",
      "name": "Title"
    },
    {
      "data": [
        1995,
        2003
      ],
      "data_path": "movie.year",
      "name": "Year"
    },
    {
      "data": [
        8.3,
        8.5
      ],
      "data_path": "movie.imdbRating",
      "name": "IMDB Rating"
    },
    {
      "data": [
        [
          "Jim Varney",
          "Tim Allen",
          "Tom Hanks",
          "Don Rickles"
        ],[
          "Shah Rukh Khan",
          "Kajol Devgan"
        ]
      ],
      "data_path": "actors[*]",
      "name": "Actors"
    }
  ]
}
```
### Chart
[JSON Schema](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/component/chart.schema.json)

Chart components support multiple visualization types:

- `chart-bar` - Bar charts for comparing metrics across categories
- `chart-line` - Line charts for trends over time
- `chart-pie` - Pie charts for showing proportions
- `chart-donut` - Donut charts for showing proportions with a central metric
- `chart-mirrored-bar` - Mirrored bar charts for comparing two metrics side-by-side

Example JSON output (bar chart):

```json
{
  "component": "chart-bar",
  "id": "test-id",
  "title": "Sales Data",
  "data": [
    {
      "name": "Q1",
      "data": [
        {"x": "Jan", "y": 100},
        {"x": "Feb", "y": 150},
        {"x": "Mar", "y": 200}
      ]
    },
    {
      "name": "Q2",
      "data": [
        {"x": "Apr", "y": 180},
        {"x": "May", "y": 220},
        {"x": "Jun", "y": 250}
      ]
    }
  ]
}
```

Data for chart can be represented as one or more named *data series* in the `data` array, containing array of *data points*. 
*Data point* contains `x` (`string` or `number`) and `y` (`number`) values.

Exact data requirements for individual chart types, and how are they converted from the *UI Agent* input data structures,
is described in [this documentation guide](https://redhat-ux.github.io/next-gen-ui-agent/guide/input_data/charts/).

## Hand Build Component (aka HBC)

[Hand Build Component (HBC) Documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/data_ui_blocks/hand_build_components/)

HBC expects there is a hand build code implemented and registered in the UI renderer for `component` value, 
which is able to visualize/show JSON from the `data` field, which is simply input data into the UI Agent (transformed to JSON if necessary).
How to register hand-build code for the `component` depends on the UI renderer type, see
[renderers documentation](https://redhat-ux.github.io/next-gen-ui-agent/guide/renderer/) please.

[JSON Schema](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/component/hand-build-component.schema.json)

Example JSON output:
```json
{
  "id": "test-id",
  "component": "movies:movie-detail",
  "data": {
    "movie": {
      "title": "Toy Story",
      "trailer": "https://www.youtube.com/embed/v-PjgYDrg70",
      "poster": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
    }
  }
}
```
