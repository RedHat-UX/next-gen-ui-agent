# UI Components Spec

Specification of the json format (as JSON Schema) of the `Data UI Blocks` produced by the *UI Agent*. 
Mainly usefull to implement client-side renderers as they consume this format.

How relevant object types are generated to TypeScript then can be tested here: [https://transform.tools/json-schema-to-typescript](https://transform.tools/json-schema-to-typescript)

## One Card
[One Card JSON Schema](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/component/one-card.schema.json)

Example JSON output:
```json
{
  "component": "one-card",
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
  ],
  "id": "test-id",
  "image": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
  "title": "Toy Story Details"
}
```

## Image
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

## Video Player
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

## Hand Build Component

This output expects there is a hand build code implemented and registered in the UI renderer for `component` value, 
which is able to visualize/show JSON from the `data` field, which is simply input data into the UI Agent. 
How to register hand-build code for `component` depends on the renderer type, see renderers documentation please.

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
