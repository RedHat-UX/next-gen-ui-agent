# Agent Spec

This folder contains agent's spec files.

How types are then generated to e.g. TS you can test here: https://transform.tools/json-schema-to-typescript

## UI Components

### One Card
[One Card JSON Schema](./component/one-card.schema.json)

Example JSON
```json
{
  "component": "one-card",
  "data_length": 4,
  "field_names": [
    "Title",
    "Year",
    "IMDB Rating",
    "Release Date",
    "Actors"
  ],
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

### Image
[JSON Schema](./component/image.schema.json)

Example:
```json
{
  "component": "image",
  "id": "test-id",
  "image": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
  "title": "Toy Story Poster"
}
```
