// Inline datasets for testing the UI Agent
// This file is auto-generated from tests/ai_eval_components/dataset/ and dataset_k8s/
// To regenerate, run: pants run tests/ai_eval_components/sync_datasets_to_e2e.py

export interface InlineDataset {
  id: string;
  label: string;
  description: string;
  dataType: string;
  payload: any;
}

export const INLINE_DATASETS: InlineDataset[] = [
  {
    id: "table_array_subscription_direct_long",
    label: "Array Subscription Direct Long",
    description: "Example: 'What are my subscriptions?...'",
    dataType: "table.dataset",
    payload: [
      {
            "id": "EUS-101",
            "name": "RHEL",
            "endDate": "2024-12-24",
            "supported": true,
            "numOfRuntimes": 2,
            "viewUrl": "https://access.redhat.com/sub/EUS-101",
            "editLink": "https://access.redhat.com/sub/e/3ygrstg",
            "renewalLink": "https://access.redhat.com/sub/r/3ygrstg"
      },
      {
            "id": "EUS-112",
            "name": "Red Hat Developer",
            "endDate": "2025-04-13",
            "supported": false,
            "numOfRuntimes": 4,
            "viewUrl": "https://access.redhat.com/sub/EUS-112",
            "editLink": "https://access.redhat.com/sub/e/3ygrstg2",
            "renewalLink": "https://access.redhat.com/sub/r/3ygrstg2"
      },
      {
            "id": "EUS-254",
            "name": "EAP",
            "endDate": "2025-07-26",
            "supported": true,
            "numOfRuntimes": 3,
            "viewUrl": "https://access.redhat.com/sub/EUS-254",
            "editLink": "https://access.redhat.com/sub/e/3ygrst3",
            "renewalLink": "https://access.redhat.com/sub/r/3ygrst3"
      },
      {
            "id": "EUS-111",
            "name": "ACVR",
            "endDate": "2024-12-24",
            "supported": true,
            "numOfRuntimes": 5,
            "viewUrl": "https://access.redhat.com/sub/asdasdad",
            "editLink": "https://access.redhat.com/sub/e/asdasdad",
            "renewalLink": "https://access.redhat.com/sub/r/asdasdad"
      },
      {
            "id": "EUS-132",
            "name": "Red Hat SSS subscription",
            "endDate": "2025-04-13",
            "supported": false,
            "numOfRuntimes": 1,
            "viewUrl": "https://access.redhat.com/sub/45gdfge",
            "editLink": "https://access.redhat.com/sub/e/45gdfge",
            "renewalLink": "https://access.redhat.com/sub/r/45gdfge"
      },
      {
            "id": "EUS-354",
            "name": "OLP",
            "endDate": "2025-07-26",
            "supported": true,
            "numOfRuntimes": 2,
            "viewUrl": "https://access.redhat.com/sub/w4tgtedgsd",
            "editLink": "https://access.redhat.com/sub/e/w4tgtedgsd",
            "renewalLink": "https://access.redhat.com/sub/r/w4tgtedgsd"
      },
      {
            "id": "EUS-401",
            "name": "JSR subscription",
            "endDate": "2024-12-24",
            "supported": true,
            "numOfRuntimes": 2,
            "viewUrl": "https://access.redhat.com/sub/45tgedsweerf",
            "editLink": "https://access.redhat.com/sub/e/45tgedsweerf",
            "renewalLink": "https://access.redhat.com/sub/r/45tgedsweerf"
      },
      {
            "id": "EUS-412",
            "name": "MMM",
            "endDate": "2025-04-13",
            "supported": false,
            "numOfRuntimes": 3,
            "viewUrl": "https://access.redhat.com/sub/435tefvsd",
            "editLink": "https://access.redhat.com/sub/e/435tefvsd",
            "renewalLink": "https://access.redhat.com/sub/r/435tefvsd"
      },
      {
            "id": "EUS-554",
            "name": "KOLER subscription",
            "endDate": "2025-07-26",
            "supported": true,
            "numOfRuntimes": 2,
            "viewUrl": "https://access.redhat.com/sub/4w5tgeagncj",
            "editLink": "https://access.redhat.com/sub/e/4w5tgeagncj",
            "renewalLink": "https://access.redhat.com/sub/r/4w5tgeagncj"
      },
      {
            "id": "EUS-501",
            "name": "FEL subscription",
            "endDate": "2024-12-24",
            "supported": true,
            "numOfRuntimes": 4,
            "viewUrl": "https://access.redhat.com/sub/kj34w5ywh",
            "editLink": "https://access.redhat.com/sub/e/kj34w5ywh",
            "renewalLink": "https://access.redhat.com/sub/r/kj34w5ywh"
      },
      {
            "id": "EUS-512",
            "name": "OLPIC subscription",
            "endDate": "2025-04-13",
            "supported": false,
            "numOfRuntimes": 2,
            "viewUrl": "https://access.redhat.com/sub/2tgergsd",
            "editLink": "https://access.redhat.com/sub/e/2tgergsd",
            "renewalLink": "https://access.redhat.com/sub/r/2tgergsd"
      },
      {
            "id": "EUS-654",
            "name": "SAE subscription",
            "endDate": "2025-07-26",
            "supported": true,
            "numOfRuntimes": 3,
            "viewUrl": "https://access.redhat.com/sub/45tgesdf",
            "editLink": "https://access.redhat.com/sub/e/45tgesdf",
            "renewalLink": "https://access.redhat.com/sub/r/45tgesdf"
      },
      {
            "id": "EUS-601",
            "name": "MEKOL subscription",
            "endDate": "2024-12-24",
            "supported": true,
            "numOfRuntimes": 2,
            "viewUrl": "https://access.redhat.com/sub/45gsdf",
            "editLink": "https://access.redhat.com/sub/e/45gsdf",
            "renewalLink": "https://access.redhat.com/sub/r/45gsdf"
      },
      {
            "id": "EUS-612",
            "name": "Red Hat ORUL subscription",
            "endDate": "2025-04-13",
            "supported": false,
            "numOfRuntimes": 2,
            "viewUrl": "https://access.redhat.com/sub/543tgeasdvs",
            "editLink": "https://access.redhat.com/sub/e/543tgeasdvs",
            "renewalLink": "https://access.redhat.com/sub/r/543tgeasdvs"
      },
      {
            "id": "EUS-654",
            "name": "YOLO subscription",
            "endDate": "2025-07-26",
            "supported": true,
            "numOfRuntimes": 325,
            "viewUrl": "https://access.redhat.com/sub/08it7jrdntrfg",
            "editLink": "https://access.redhat.com/sub/e/08it7jrdntrfg",
            "renewalLink": "https://access.redhat.com/sub/r/08it7jrdntrfg"
      }
],
  },
  {
    id: "chart-line_chart_line_standard_revenue_expenses",
    label: "Chart Line Standard Revenue Expenses",
    description: "Example: 'Display revenue and expenses trends...'",
    dataType: "chart-line.dataset",
    payload: {
      "data": [
            {
                  "quarter": "Q1",
                  "revenue": 50000,
                  "expenses": 35000
            },
            {
                  "quarter": "Q2",
                  "revenue": 60000,
                  "expenses": 40000
            },
            {
                  "quarter": "Q3",
                  "revenue": 55000,
                  "expenses": 38000
            },
            {
                  "quarter": "Q4",
                  "revenue": 70000,
                  "expenses": 45000
            }
      ]
},
  },
  {
    id: "one-card_simple_subscription_direct",
    label: "Simple Subscription Direct",
    description: "Example: 'When does my RHEL subscription end?...'",
    dataType: "one-card.dataset",
    payload: {
      "id": "EUS-101",
      "name": "RHEL",
      "endDate": "2024-12-24",
      "supported": true,
      "numOfRuntimes": 2,
      "viewUrl": "https://access.redhat.com/sub/EUS-101",
      "editUrl": "https://access.redhat.com/sub/ed/EUS-101",
      "renewUrl": "https://access.redhat.com/sub/r/EUS-101"
},
  },
  {
    id: "chart-line_chart_line_standard_sales_profit",
    label: "Chart Line Standard Sales Profit",
    description: "Example: 'Show me sales and profit over time...'",
    dataType: "chart-line.dataset",
    payload: {
      "data": [
            {
                  "month": "Jan",
                  "sales": 100,
                  "profit": 20
            },
            {
                  "month": "Feb",
                  "sales": 150,
                  "profit": 35
            },
            {
                  "month": "Mar",
                  "sales": 120,
                  "profit": 25
            },
            {
                  "month": "Apr",
                  "sales": 180,
                  "profit": 45
            },
            {
                  "month": "May",
                  "sales": 200,
                  "profit": 50
            }
      ]
},
  },
  {
    id: "video-player_simple_movie_actorsNames_camelCase",
    label: "Simple Movie Actorsnames Camelcase",
    description: "Example: 'Show me Toy Story trailer....'",
    dataType: "video-player.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English",
                  "German",
                  "French"
            ],
            "year": 1995,
            "imdbId": "0114709",
            "pictureUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "imdbRating": 8.3,
            "movieId": "1",
            "countries": [
                  "USA"
            ],
            "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "imdbVotes": 591836,
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdbId": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            "Jim Varney",
            "Tim Allen",
            "Tom Hanks",
            "Don Rickles"
      ]
},
  },
  {
    id: "video-player_simple_movie_actorsNames_snakeCase",
    label: "Simple Movie Actorsnames Snakecase",
    description: "Example: 'Show me Toy Story trailer....'",
    dataType: "video-player.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English",
                  "German",
                  "French"
            ],
            "year": 1995,
            "imdb_id": "0114709",
            "picture_url": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "imdb_rating": 8.3,
            "movie_id": "1",
            "countries": [
                  "USA"
            ],
            "trailer_url": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "imdb_votes": 591836,
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdb_id": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            "Jim Varney",
            "Tim Allen",
            "Tom Hanks",
            "Don Rickles"
      ]
},
  },
  {
    id: "video-player_simple_movie_actorsObjects_camelCase",
    label: "Simple Movie Actorsobjects Camelcase",
    description: "Example: 'Show me Toy Story trailer....'",
    dataType: "video-player.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English"
            ],
            "year": 1995,
            "pictureUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "movieId": "1",
            "imdb": {
                  "votes": 591836,
                  "id": "0114709",
                  "rating": 8.3
            },
            "countries": [
                  "USA",
                  "Germany",
                  "Czech Republic"
            ],
            "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdbId": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            {
                  "name": "Jim Varney",
                  "role": "Slinky Dog",
                  "description": " A dachshund slinky toy and Woody's second-in-command."
            },
            {
                  "name": "Tim Allen",
                  "role": "Buzz Lightyear",
                  "description": "Action figure, Andy's second favorite toy, and Woody's rival, who later becomes his best friend."
            },
            {
                  "name": "Tom Hanks",
                  "role": "Woody",
                  "description": "A pullstring cowboy doll who is Andy's favorite toy"
            },
            {
                  "name": "Don Rickles",
                  "role": "Mr. Potato Head",
                  "description": "A cynical potato-shaped doll with put-together pieces on his body."
            }
      ]
},
  },
  {
    id: "video-player_simple_movie_actorsObjects_snakeCase",
    label: "Simple Movie Actorsobjects Snakecase",
    description: "Example: 'Show me Toy Story trailer....'",
    dataType: "video-player.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English"
            ],
            "year": 1995,
            "picture_url": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "movie_id": "1",
            "imdb": {
                  "votes": 591836,
                  "id": "0114709",
                  "rating": 8.3
            },
            "countries": [
                  "USA",
                  "Germany",
                  "Czech Republic"
            ],
            "trailer_url": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdb_id": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            {
                  "name": "Jim Varney",
                  "role": "Slinky Dog",
                  "description": " A dachshund slinky toy and Woody's second-in-command."
            },
            {
                  "name": "Tim Allen",
                  "role": "Buzz Lightyear",
                  "description": "Action figure, Andy's second favorite toy, and Woody's rival, who later becomes his best friend."
            },
            {
                  "name": "Tom Hanks",
                  "role": "Woody",
                  "description": "A pullstring cowboy doll who is Andy's favorite toy"
            },
            {
                  "name": "Don Rickles",
                  "role": "Mr. Potato Head",
                  "description": "A cynical potato-shaped doll with put-together pieces on his body."
            }
      ]
},
  },
  {
    id: "video-player_simple_movie_actorsNames_imdbNested_camelCase",
    label: "Simple Movie Actorsnames Imdbnested Camelcase",
    description: "Example: 'Show me Toy Story trailer....'",
    dataType: "video-player.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English"
            ],
            "year": 1995,
            "pictureUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "movieId": "1",
            "imdb": {
                  "votes": 591836,
                  "id": "0114709",
                  "rating": 8.3
            },
            "countries": [
                  "USA",
                  "Germany",
                  "Czech Republic"
            ],
            "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdbId": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            "Jim Varney",
            "Tim Allen",
            "Tom Hanks",
            "Don Rickles"
      ]
},
  },
  {
    id: "set-of-cards_array_subscription_inobject_short",
    label: "Array Subscription Inobject Short",
    description: "Example: 'What are my subscriptions?...'",
    dataType: "set-of-cards.dataset",
    payload: {
      "subscriptions": [
            {
                  "id": "EUS-101",
                  "name": "RHEL",
                  "endDate": "2024-12-24",
                  "supported": true,
                  "numOfRuntimes": 2,
                  "viewLink": "https://access.redhat.com/sub/3ygrstg",
                  "editLink": "https://access.redhat.com/sub/e/3ygrstg",
                  "renewalLink": "https://access.redhat.com/sub/r/3ygrstg"
            },
            {
                  "id": "EUS-112",
                  "name": "Red Hat Developer",
                  "endDate": "2025-04-13",
                  "supported": false,
                  "numOfRuntimes": 3,
                  "viewLink": "https://access.redhat.com/sub/3ygrs",
                  "editLink": "https://access.redhat.com/sub/e/3ygrs",
                  "renewalLink": "https://access.redhat.com/sub/r/3ygrs"
            },
            {
                  "id": "EUS-254",
                  "name": "EAP",
                  "endDate": "2025-07-26",
                  "supported": true,
                  "numOfRuntimes": 2,
                  "viewLink": "https://access.redhat.com/sub/45wgdf",
                  "editLink": "https://access.redhat.com/sub/e/45wgdf",
                  "renewalLink": "https://access.redhat.com/sub/r/45wgdf"
            }
      ]
},
  },
  {
    id: "set-of-cards_array_subscription_inobjectmore_short",
    label: "Array Subscription Inobjectmore Short",
    description: "Example: 'What are my subscriptions?...'",
    dataType: "set-of-cards.dataset",
    payload: {
      "username": "jdoe",
      "name": "John Doe",
      "createdAt": "2022-10-14",
      "subscriptions": [
            {
                  "id": "EUS-101",
                  "name": "RHEL",
                  "endDate": "2024-12-24",
                  "supported": true,
                  "numOfRuntimes": 2,
                  "viewLink": "https://access.redhat.com/sub/3ygrstg",
                  "editLink": "https://access.redhat.com/sub/e/3ygrstg",
                  "renewalLink": "https://access.redhat.com/sub/r/3ygrstg"
            },
            {
                  "id": "EUS-112",
                  "name": "Red Hat Developer",
                  "endDate": "2025-04-13",
                  "supported": false,
                  "numOfRuntimes": 3,
                  "viewLink": "https://access.redhat.com/sub/3ygrs",
                  "editLink": "https://access.redhat.com/sub/e/3ygrs",
                  "renewalLink": "https://access.redhat.com/sub/r/3ygrs"
            },
            {
                  "id": "EUS-254",
                  "name": "EAP",
                  "endDate": "2025-07-26",
                  "supported": true,
                  "numOfRuntimes": 2,
                  "viewLink": "https://access.redhat.com/sub/45wgdf",
                  "editLink": "https://access.redhat.com/sub/e/45wgdf",
                  "renewalLink": "https://access.redhat.com/sub/r/45wgdf"
            }
      ]
},
  },
  {
    id: "chart-line_chart_line_multiseries_regions",
    label: "Chart Line Multiseries Regions",
    description: "Example: 'Show user count for Region A and Region B by quarter...'",
    dataType: "chart-line.dataset",
    payload: {
      "regions": [
            {
                  "regionName": "Region A",
                  "quarterlyUsers": [
                        {
                              "quarter": "Q1",
                              "users": 5000
                        },
                        {
                              "quarter": "Q2",
                              "users": 6000
                        },
                        {
                              "quarter": "Q3",
                              "users": 5500
                        }
                  ]
            },
            {
                  "regionName": "Region B",
                  "quarterlyUsers": [
                        {
                              "quarter": "Q1",
                              "users": 3000
                        },
                        {
                              "quarter": "Q2",
                              "users": 4000
                        },
                        {
                              "quarter": "Q3",
                              "users": 3500
                        }
                  ]
            }
      ]
},
  },
  {
    id: "one-card_simple_subscription_direct_inarray",
    label: "Simple Subscription Direct Inarray",
    description: "Example: 'When does my RHEL subscription end?...'",
    dataType: "one-card.dataset",
    payload: [
      {
            "id": "EUS-101",
            "name": "RHEL",
            "endDate": "2024-12-24",
            "supported": true,
            "numOfRuntimes": 2,
            "viewUrl": "https://access.redhat.com/sub/EUS-101",
            "editUrl": "https://access.redhat.com/sub/ed/EUS-101",
            "renewUrl": "https://access.redhat.com/sub/r/EUS-101"
      }
],
  },
  {
    id: "one-card_simple_subscription_inobject_inarray",
    label: "Simple Subscription Inobject Inarray",
    description: "Example: 'When does my RHEL subscription end?...'",
    dataType: "one-card.dataset",
    payload: [
      {
            "subscription": {
                  "id": "EUS-101",
                  "name": "RHEL",
                  "endDate": "2024-12-24",
                  "supported": true,
                  "numOfRuntimes": 2,
                  "viewUrl": "https://access.redhat.com/sub/EUS-101",
                  "editUrl": "https://access.redhat.com/sub/ed/EUS-101",
                  "renewUrl": "https://access.redhat.com/sub/r/EUS-101"
            }
      }
],
  },
  {
    id: "chart-line_chart_line_multiseries_products",
    label: "Chart Line Multiseries Products",
    description: "Example: 'Display sales performance for Product X and Product Y over months...'",
    dataType: "chart-line.dataset",
    payload: {
      "products": [
            {
                  "name": "Product X",
                  "monthlySales": [
                        {
                              "month": "Jan",
                              "sales": 1000
                        },
                        {
                              "month": "Feb",
                              "sales": 1200
                        },
                        {
                              "month": "Mar",
                              "sales": 1100
                        }
                  ]
            },
            {
                  "name": "Product Y",
                  "monthlySales": [
                        {
                              "month": "Jan",
                              "sales": 800
                        },
                        {
                              "month": "Feb",
                              "sales": 950
                        },
                        {
                              "month": "Mar",
                              "sales": 900
                        }
                  ]
            }
      ]
},
  },
  {
    id: "one-card_simple_movie_actorsNames_camelCase",
    label: "Simple Movie Actorsnames Camelcase",
    description: "Example: 'Show me info about the Toy Story movie....'",
    dataType: "one-card.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English",
                  "German",
                  "French"
            ],
            "year": 1995,
            "imdbId": "0114709",
            "pictureUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "imdbRating": 8.3,
            "movieId": "1",
            "countries": [
                  "USA"
            ],
            "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "imdbVotes": 591836,
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdbId": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            "Jim Varney",
            "Tim Allen",
            "Tom Hanks",
            "Don Rickles"
      ]
},
  },
  {
    id: "one-card_simple_movie_actorsNames_snakeCase",
    label: "Simple Movie Actorsnames Snakecase",
    description: "Example: 'Show me info about the Toy Story movie....'",
    dataType: "one-card.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English",
                  "German",
                  "French"
            ],
            "year": 1995,
            "imdb_id": "0114709",
            "picture_url": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "imdb_rating": 8.3,
            "movie_id": "1",
            "countries": [
                  "USA"
            ],
            "trailer_url": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "imdb_votes": 591836,
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdb_id": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            "Jim Varney",
            "Tim Allen",
            "Tom Hanks",
            "Don Rickles"
      ]
},
  },
  {
    id: "one-card_simple_movie_actorsObjects_camelCase",
    label: "Simple Movie Actorsobjects Camelcase",
    description: "Example: 'Show me info about the Toy Story movie....'",
    dataType: "one-card.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English"
            ],
            "year": 1995,
            "pictureUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "movieId": "1",
            "imdb": {
                  "votes": 591836,
                  "id": "0114709",
                  "rating": 8.3
            },
            "countries": [
                  "USA",
                  "Germany",
                  "Czech Republic"
            ],
            "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdbId": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            {
                  "name": "Jim Varney",
                  "role": "Slinky Dog",
                  "description": " A dachshund slinky toy and Woody's second-in-command."
            },
            {
                  "name": "Tim Allen",
                  "role": "Buzz Lightyear",
                  "description": "Action figure, Andy's second favorite toy, and Woody's rival, who later becomes his best friend."
            },
            {
                  "name": "Tom Hanks",
                  "role": "Woody",
                  "description": "A pullstring cowboy doll who is Andy's favorite toy"
            },
            {
                  "name": "Don Rickles",
                  "role": "Mr. Potato Head",
                  "description": "A cynical potato-shaped doll with put-together pieces on his body."
            }
      ]
},
  },
  {
    id: "one-card_simple_movie_actorsObjects_snakeCase",
    label: "Simple Movie Actorsobjects Snakecase",
    description: "Example: 'Show me info about the Toy Story movie....'",
    dataType: "one-card.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English"
            ],
            "year": 1995,
            "picture_url": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "movie_id": "1",
            "imdb": {
                  "votes": 591836,
                  "id": "0114709",
                  "rating": 8.3
            },
            "countries": [
                  "USA",
                  "Germany",
                  "Czech Republic"
            ],
            "trailer_url": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdb_id": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            {
                  "name": "Jim Varney",
                  "role": "Slinky Dog",
                  "description": " A dachshund slinky toy and Woody's second-in-command."
            },
            {
                  "name": "Tim Allen",
                  "role": "Buzz Lightyear",
                  "description": "Action figure, Andy's second favorite toy, and Woody's rival, who later becomes his best friend."
            },
            {
                  "name": "Tom Hanks",
                  "role": "Woody",
                  "description": "A pullstring cowboy doll who is Andy's favorite toy"
            },
            {
                  "name": "Don Rickles",
                  "role": "Mr. Potato Head",
                  "description": "A cynical potato-shaped doll with put-together pieces on his body."
            }
      ]
},
  },
  {
    id: "one-card_simple_movie_actorsNames_imdbNested_camelCase",
    label: "Simple Movie Actorsnames Imdbnested Camelcase",
    description: "Example: 'Show me info about the Toy Story movie....'",
    dataType: "one-card.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English"
            ],
            "year": 1995,
            "pictureUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "movieId": "1",
            "imdb": {
                  "votes": 591836,
                  "id": "0114709",
                  "rating": 8.3
            },
            "countries": [
                  "USA",
                  "Germany",
                  "Czech Republic"
            ],
            "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdbId": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            "Jim Varney",
            "Tim Allen",
            "Tom Hanks",
            "Don Rickles"
      ]
},
  },
  {
    id: "chart-line_chart_line_multiseries_movies",
    label: "Chart Line Multiseries Movies",
    description: "Example: 'Show me weekly revenue for Movie A and Movie B...'",
    dataType: "chart-line.dataset",
    payload: {
      "movies": [
            {
                  "title": "Movie A",
                  "weeklyData": [
                        {
                              "week": "W1",
                              "revenue": 100
                        },
                        {
                              "week": "W2",
                              "revenue": 150
                        },
                        {
                              "week": "W3",
                              "revenue": 120
                        }
                  ]
            },
            {
                  "title": "Movie B",
                  "weeklyData": [
                        {
                              "week": "W1",
                              "revenue": 80
                        },
                        {
                              "week": "W2",
                              "revenue": 120
                        },
                        {
                              "week": "W3",
                              "revenue": 100
                        }
                  ]
            }
      ]
},
  },
  {
    id: "image_simple_movie_actorsNames_camelCase",
    label: "Simple Movie Actorsnames Camelcase",
    description: "Example: 'Show me Toy Story poster...'",
    dataType: "image.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English",
                  "German",
                  "French"
            ],
            "year": 1995,
            "imdbId": "0114709",
            "pictureUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "imdbRating": 8.3,
            "movieId": "1",
            "countries": [
                  "USA"
            ],
            "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "imdbVotes": 591836,
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdbId": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            "Jim Varney",
            "Tim Allen",
            "Tom Hanks",
            "Don Rickles"
      ]
},
  },
  {
    id: "image_simple_movie_actorsNames_snakeCase",
    label: "Simple Movie Actorsnames Snakecase",
    description: "Example: 'Show me Toy Story poster...'",
    dataType: "image.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English",
                  "German",
                  "French"
            ],
            "year": 1995,
            "imdb_id": "0114709",
            "picture_url": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "imdb_rating": 8.3,
            "movie_id": "1",
            "countries": [
                  "USA"
            ],
            "trailer_url": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "imdb_votes": 591836,
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdb_id": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            "Jim Varney",
            "Tim Allen",
            "Tom Hanks",
            "Don Rickles"
      ]
},
  },
  {
    id: "image_simple_movie_actorsObjects_camelCase",
    label: "Simple Movie Actorsobjects Camelcase",
    description: "Example: 'Show me Toy Story poster...'",
    dataType: "image.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English"
            ],
            "year": 1995,
            "pictureUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "movieId": "1",
            "imdb": {
                  "votes": 591836,
                  "id": "0114709",
                  "rating": 8.3
            },
            "countries": [
                  "USA",
                  "Germany",
                  "Czech Republic"
            ],
            "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdbId": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            {
                  "name": "Jim Varney",
                  "role": "Slinky Dog",
                  "description": " A dachshund slinky toy and Woody's second-in-command."
            },
            {
                  "name": "Tim Allen",
                  "role": "Buzz Lightyear",
                  "description": "Action figure, Andy's second favorite toy, and Woody's rival, who later becomes his best friend."
            },
            {
                  "name": "Tom Hanks",
                  "role": "Woody",
                  "description": "A pullstring cowboy doll who is Andy's favorite toy"
            },
            {
                  "name": "Don Rickles",
                  "role": "Mr. Potato Head",
                  "description": "A cynical potato-shaped doll with put-together pieces on his body."
            }
      ]
},
  },
  {
    id: "image_simple_movie_actorsObjects_snakeCase",
    label: "Simple Movie Actorsobjects Snakecase",
    description: "Example: 'Show me Toy Story poster...'",
    dataType: "image.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English"
            ],
            "year": 1995,
            "picture_url": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "movie_id": "1",
            "imdb": {
                  "votes": 591836,
                  "id": "0114709",
                  "rating": 8.3
            },
            "countries": [
                  "USA",
                  "Germany",
                  "Czech Republic"
            ],
            "trailer_url": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdb_id": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            {
                  "name": "Jim Varney",
                  "role": "Slinky Dog",
                  "description": " A dachshund slinky toy and Woody's second-in-command."
            },
            {
                  "name": "Tim Allen",
                  "role": "Buzz Lightyear",
                  "description": "Action figure, Andy's second favorite toy, and Woody's rival, who later becomes his best friend."
            },
            {
                  "name": "Tom Hanks",
                  "role": "Woody",
                  "description": "A pullstring cowboy doll who is Andy's favorite toy"
            },
            {
                  "name": "Don Rickles",
                  "role": "Mr. Potato Head",
                  "description": "A cynical potato-shaped doll with put-together pieces on his body."
            }
      ]
},
  },
  {
    id: "image_simple_movie_actorsNames_imdbNested_camelCase",
    label: "Simple Movie Actorsnames Imdbnested Camelcase",
    description: "Example: 'Show me Toy Story poster...'",
    dataType: "image.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English"
            ],
            "year": 1995,
            "pictureUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "movieId": "1",
            "imdb": {
                  "votes": 591836,
                  "id": "0114709",
                  "rating": 8.3
            },
            "countries": [
                  "USA",
                  "Germany",
                  "Czech Republic"
            ],
            "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdbId": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            "Jim Varney",
            "Tim Allen",
            "Tom Hanks",
            "Don Rickles"
      ]
},
  },
  {
    id: "set-of-cards_array_subscription_direct_short",
    label: "Array Subscription Direct Short",
    description: "Example: 'What are my subscriptions?...'",
    dataType: "set-of-cards.dataset",
    payload: [
      {
            "id": "EUS-101",
            "name": "RHEL",
            "endDate": "2024-12-24",
            "supported": true,
            "numOfRuntimes": 2,
            "viewLink": "https://access.redhat.com/sub/3ygrstg",
            "editLink": "https://access.redhat.com/sub/e/3ygrstg",
            "renewalLink": "https://access.redhat.com/sub/r/3ygrstg"
      },
      {
            "id": "EUS-112",
            "name": "Red Hat Developer",
            "endDate": "2025-04-13",
            "supported": false,
            "numOfRuntimes": 3,
            "viewLink": "https://access.redhat.com/sub/3ygrs",
            "editLink": "https://access.redhat.com/sub/e/3ygrs",
            "renewalLink": "https://access.redhat.com/sub/r/3ygrs"
      },
      {
            "id": "EUS-254",
            "name": "EAP",
            "endDate": "2025-07-26",
            "supported": true,
            "numOfRuntimes": 2,
            "viewLink": "https://access.redhat.com/sub/45wgdf",
            "editLink": "https://access.redhat.com/sub/e/45wgdf",
            "renewalLink": "https://access.redhat.com/sub/r/45wgdf"
      }
],
  },
  {
    id: "one-card_item1",
    label: "Item1",
    description: "Example: 'My latest order?...'",
    dataType: "one-card.dataset",
    payload: {
      "order": {
            "id": "ORT-4578",
            "product": {
                  "name": "Good Bood",
                  "brand": "Master Blaster",
                  "price": "10"
            },
            "date": "2024-03-12",
            "amount": "14",
            "price": "140",
            "paid": false
      }
},
  },
  {
    id: "set-of-cards_array_k8s_users",
    label: "Array K8S Users",
    description: "Example: 'List users from my cluster...'",
    dataType: "set-of-cards.dataset",
    payload: {
      "rbac_bindings": [
            {
                  "user": "admin@redhat.com",
                  "role": "cluster-admin",
                  "type": "ClusterRoleBinding",
                  "namespace": "*",
                  "permissions": [
                        "*"
                  ],
                  "last_login": "2024-10-03T08:30:00Z",
                  "mfa_enabled": true
            },
            {
                  "user": "developer@redhat.com",
                  "role": "edit",
                  "type": "RoleBinding",
                  "namespace": "development",
                  "permissions": [
                        "get",
                        "list",
                        "create",
                        "update",
                        "delete"
                  ],
                  "last_login": "2024-10-03T07:15:00Z",
                  "mfa_enabled": true
            },
            {
                  "user": "viewer@redhat.com",
                  "role": "view",
                  "type": "RoleBinding",
                  "namespace": "production-app",
                  "permissions": [
                        "get",
                        "list"
                  ],
                  "last_login": "2024-10-02T16:45:00Z",
                  "mfa_enabled": false
            }
      ]
},
  },
  {
    id: "set-of-cards_simple_movie_actorsObjects_camelCase",
    label: "Simple Movie Actorsobjects Camelcase",
    description: "Example: 'Who acted in the Toy Story?...'",
    dataType: "set-of-cards.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English"
            ],
            "year": 1995,
            "pictureUrl": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "movieId": "1",
            "imdb": {
                  "votes": 591836,
                  "id": "0114709",
                  "rating": 8.3
            },
            "countries": [
                  "USA",
                  "Germany",
                  "Czech Republic"
            ],
            "trailerUrl": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdbId": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            {
                  "name": "Jim Varney",
                  "role": "Slinky Dog",
                  "description": " A dachshund slinky toy and Woody's second-in-command."
            },
            {
                  "name": "Tim Allen",
                  "role": "Buzz Lightyear",
                  "description": "Action figure, Andy's second favorite toy, and Woody's rival, who later becomes his best friend."
            },
            {
                  "name": "Tom Hanks",
                  "role": "Woody",
                  "description": "A pullstring cowboy doll who is Andy's favorite toy"
            },
            {
                  "name": "Don Rickles",
                  "role": "Mr. Potato Head",
                  "description": "A cynical potato-shaped doll with put-together pieces on his body."
            }
      ]
},
  },
  {
    id: "set-of-cards_simple_movie_actorsObjects_snakeCase",
    label: "Simple Movie Actorsobjects Snakecase",
    description: "Example: 'Who acted in the Toy Story?...'",
    dataType: "set-of-cards.dataset",
    payload: {
      "movie": {
            "languages": [
                  "English"
            ],
            "year": 1995,
            "picture_url": "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
            "runtime": 81,
            "movie_id": "1",
            "imdb": {
                  "votes": 591836,
                  "id": "0114709",
                  "rating": 8.3
            },
            "countries": [
                  "USA",
                  "Germany",
                  "Czech Republic"
            ],
            "trailer_url": "https://www.youtube.com/watch?v=v-PjgYDrg70",
            "title": "Toy Story",
            "url": "https://themoviedb.org/movie/862",
            "revenue": 373554033,
            "tmdb_id": "862",
            "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy's room.",
            "released": "1995-11-22",
            "budget": 30000000
      },
      "actors": [
            {
                  "name": "Jim Varney",
                  "role": "Slinky Dog",
                  "description": " A dachshund slinky toy and Woody's second-in-command."
            },
            {
                  "name": "Tim Allen",
                  "role": "Buzz Lightyear",
                  "description": "Action figure, Andy's second favorite toy, and Woody's rival, who later becomes his best friend."
            },
            {
                  "name": "Tom Hanks",
                  "role": "Woody",
                  "description": "A pullstring cowboy doll who is Andy's favorite toy"
            },
            {
                  "name": "Don Rickles",
                  "role": "Mr. Potato Head",
                  "description": "A cynical potato-shaped doll with put-together pieces on his body."
            }
      ]
},
  },
  {
    id: "chart-line_chart_line_standard_temperature_humidity",
    label: "Chart Line Standard Temperature Humidity",
    description: "Example: 'Plot temperature and humidity over the day...'",
    dataType: "chart-line.dataset",
    payload: {
      "readings": [
            {
                  "time": "06:00",
                  "temperature": 15,
                  "humidity": 60
            },
            {
                  "time": "12:00",
                  "temperature": 25,
                  "humidity": 45
            },
            {
                  "time": "18:00",
                  "temperature": 22,
                  "humidity": 55
            },
            {
                  "time": "24:00",
                  "temperature": 18,
                  "humidity": 65
            }
      ]
},
  },
  {
    id: "one-card_simple_subscription_inobject",
    label: "Simple Subscription Inobject",
    description: "Example: 'When does my RHEL subscription end?...'",
    dataType: "one-card.dataset",
    payload: {
      "subscription": {
            "id": "EUS-101",
            "name": "RHEL",
            "endDate": "2024-12-24",
            "supported": true,
            "numOfRuntimes": 2,
            "viewUrl": "https://access.redhat.com/sub/EUS-101",
            "editUrl": "https://access.redhat.com/sub/ed/EUS-101",
            "renewUrl": "https://access.redhat.com/sub/r/EUS-101"
      }
},
  },
  {
    id: "table_array_subscription_inobject_long",
    label: "Array Subscription Inobject Long",
    description: "Example: 'What are my subscriptions?...'",
    dataType: "table.dataset",
    payload: {
      "subscriptions": [
            {
                  "id": "EUS-101",
                  "name": "RHEL",
                  "endDate": "2024-12-24",
                  "supported": true,
                  "numOfRuntimes": 2,
                  "viewUrl": "https://access.redhat.com/sub/EUS-101",
                  "editLink": "https://access.redhat.com/sub/e/3ygrstg",
                  "renewalLink": "https://access.redhat.com/sub/r/3ygrstg"
            },
            {
                  "id": "EUS-112",
                  "name": "Red Hat Developer",
                  "endDate": "2025-04-13",
                  "supported": false,
                  "numOfRuntimes": 4,
                  "viewUrl": "https://access.redhat.com/sub/EUS-112",
                  "editLink": "https://access.redhat.com/sub/e/3ygrstg2",
                  "renewalLink": "https://access.redhat.com/sub/r/3ygrstg2"
            },
            {
                  "id": "EUS-254",
                  "name": "EAP",
                  "endDate": "2025-07-26",
                  "supported": true,
                  "numOfRuntimes": 3,
                  "viewUrl": "https://access.redhat.com/sub/EUS-254",
                  "editLink": "https://access.redhat.com/sub/e/3ygrst3",
                  "renewalLink": "https://access.redhat.com/sub/r/3ygrst3"
            },
            {
                  "id": "EUS-111",
                  "name": "ACVR",
                  "endDate": "2024-12-24",
                  "supported": true,
                  "numOfRuntimes": 5,
                  "viewUrl": "https://access.redhat.com/sub/asdasdad",
                  "editLink": "https://access.redhat.com/sub/e/asdasdad",
                  "renewalLink": "https://access.redhat.com/sub/r/asdasdad"
            },
            {
                  "id": "EUS-132",
                  "name": "Red Hat SSS subscription",
                  "endDate": "2025-04-13",
                  "supported": false,
                  "numOfRuntimes": 1,
                  "viewUrl": "https://access.redhat.com/sub/45gdfge",
                  "editLink": "https://access.redhat.com/sub/e/45gdfge",
                  "renewalLink": "https://access.redhat.com/sub/r/45gdfge"
            },
            {
                  "id": "EUS-354",
                  "name": "OLP",
                  "endDate": "2025-07-26",
                  "supported": true,
                  "numOfRuntimes": 2,
                  "viewUrl": "https://access.redhat.com/sub/w4tgtedgsd",
                  "editLink": "https://access.redhat.com/sub/e/w4tgtedgsd",
                  "renewalLink": "https://access.redhat.com/sub/r/w4tgtedgsd"
            },
            {
                  "id": "EUS-401",
                  "name": "JSR subscription",
                  "endDate": "2024-12-24",
                  "supported": true,
                  "numOfRuntimes": 2,
                  "viewUrl": "https://access.redhat.com/sub/45tgedsweerf",
                  "editLink": "https://access.redhat.com/sub/e/45tgedsweerf",
                  "renewalLink": "https://access.redhat.com/sub/r/45tgedsweerf"
            },
            {
                  "id": "EUS-412",
                  "name": "MMM",
                  "endDate": "2025-04-13",
                  "supported": false,
                  "numOfRuntimes": 3,
                  "viewUrl": "https://access.redhat.com/sub/435tefvsd",
                  "editLink": "https://access.redhat.com/sub/e/435tefvsd",
                  "renewalLink": "https://access.redhat.com/sub/r/435tefvsd"
            },
            {
                  "id": "EUS-554",
                  "name": "KOLER subscription",
                  "endDate": "2025-07-26",
                  "supported": true,
                  "numOfRuntimes": 2,
                  "viewUrl": "https://access.redhat.com/sub/4w5tgeagncj",
                  "editLink": "https://access.redhat.com/sub/e/4w5tgeagncj",
                  "renewalLink": "https://access.redhat.com/sub/r/4w5tgeagncj"
            },
            {
                  "id": "EUS-501",
                  "name": "FEL subscription",
                  "endDate": "2024-12-24",
                  "supported": true,
                  "numOfRuntimes": 4,
                  "viewUrl": "https://access.redhat.com/sub/kj34w5ywh",
                  "editLink": "https://access.redhat.com/sub/e/kj34w5ywh",
                  "renewalLink": "https://access.redhat.com/sub/r/kj34w5ywh"
            },
            {
                  "id": "EUS-512",
                  "name": "OLPIC subscription",
                  "endDate": "2025-04-13",
                  "supported": false,
                  "numOfRuntimes": 2,
                  "viewUrl": "https://access.redhat.com/sub/2tgergsd",
                  "editLink": "https://access.redhat.com/sub/e/2tgergsd",
                  "renewalLink": "https://access.redhat.com/sub/r/2tgergsd"
            },
            {
                  "id": "EUS-654",
                  "name": "SAE subscription",
                  "endDate": "2025-07-26",
                  "supported": true,
                  "numOfRuntimes": 3,
                  "viewUrl": "https://access.redhat.com/sub/45tgesdf",
                  "editLink": "https://access.redhat.com/sub/e/45tgesdf",
                  "renewalLink": "https://access.redhat.com/sub/r/45tgesdf"
            },
            {
                  "id": "EUS-601",
                  "name": "MEKOL subscription",
                  "endDate": "2024-12-24",
                  "supported": true,
                  "numOfRuntimes": 2,
                  "viewUrl": "https://access.redhat.com/sub/45gsdf",
                  "editLink": "https://access.redhat.com/sub/e/45gsdf",
                  "renewalLink": "https://access.redhat.com/sub/r/45gsdf"
            },
            {
                  "id": "EUS-612",
                  "name": "Red Hat ORUL subscription",
                  "endDate": "2025-04-13",
                  "supported": false,
                  "numOfRuntimes": 2,
                  "viewUrl": "https://access.redhat.com/sub/543tgeasdvs",
                  "editLink": "https://access.redhat.com/sub/e/543tgeasdvs",
                  "renewalLink": "https://access.redhat.com/sub/r/543tgeasdvs"
            },
            {
                  "id": "EUS-654",
                  "name": "YOLO subscription",
                  "endDate": "2025-07-26",
                  "supported": true,
                  "numOfRuntimes": 325,
                  "viewUrl": "https://access.redhat.com/sub/08it7jrdntrfg",
                  "editLink": "https://access.redhat.com/sub/e/08it7jrdntrfg",
                  "renewalLink": "https://access.redhat.com/sub/r/08it7jrdntrfg"
            }
      ]
},
  },
  {
    id: "table_services",
    label: "Services",
    description: "Example: 'Why is api-gateway failing?...'",
    dataType: "table.dataset",
    payload: {
      "services": [
            {
                  "name": "payment-service",
                  "namespace": "production-app",
                  "type": "ClusterIP",
                  "cluster_ip": "10.128.45.23",
                  "ports": [
                        {
                              "port": 8080,
                              "target_port": 8080
                        }
                  ],
                  "endpoints": 3,
                  "healthy_endpoints": 2,
                  "dns_resolution": "healthy",
                  "ingress_url": "https://payments.apps.prod.example.com"
            },
            {
                  "name": "user-database",
                  "namespace": "production-app",
                  "type": "ClusterIP",
                  "cluster_ip": "10.128.67.89",
                  "ports": [
                        {
                              "port": 5432,
                              "target_port": 5432
                        }
                  ],
                  "endpoints": 1,
                  "healthy_endpoints": 1,
                  "dns_resolution": "healthy",
                  "ingress_url": null
            },
            {
                  "name": "api-gateway",
                  "namespace": "production-app",
                  "type": "LoadBalancer",
                  "cluster_ip": "10.128.12.45",
                  "external_ip": "34.123.45.67",
                  "ports": [
                        {
                              "port": 443,
                              "target_port": 8443
                        }
                  ],
                  "endpoints": 2,
                  "healthy_endpoints": 0,
                  "dns_resolution": "failed",
                  "ingress_url": "https://api.prod.example.com",
                  "error": "No healthy endpoints available"
            }
      ]
},
  },
  {
    id: "set-of-cards_services",
    label: "Services",
    description: "Example: 'Show me service status...'",
    dataType: "set-of-cards.dataset",
    payload: {
      "services": [
            {
                  "name": "payment-service",
                  "namespace": "production-app",
                  "type": "ClusterIP",
                  "cluster_ip": "10.128.45.23",
                  "ports": [
                        {
                              "port": 8080,
                              "target_port": 8080
                        }
                  ],
                  "endpoints": 3,
                  "healthy_endpoints": 2,
                  "dns_resolution": "healthy",
                  "ingress_url": "https://payments.apps.prod.example.com"
            },
            {
                  "name": "user-database",
                  "namespace": "production-app",
                  "type": "ClusterIP",
                  "cluster_ip": "10.128.67.89",
                  "ports": [
                        {
                              "port": 5432,
                              "target_port": 5432
                        }
                  ],
                  "endpoints": 1,
                  "healthy_endpoints": 1,
                  "dns_resolution": "healthy",
                  "ingress_url": null
            },
            {
                  "name": "api-gateway",
                  "namespace": "production-app",
                  "type": "LoadBalancer",
                  "cluster_ip": "10.128.12.45",
                  "external_ip": "34.123.45.67",
                  "ports": [
                        {
                              "port": 443,
                              "target_port": 8443
                        }
                  ],
                  "endpoints": 2,
                  "healthy_endpoints": 0,
                  "dns_resolution": "failed",
                  "ingress_url": "https://api.prod.example.com",
                  "error": "No healthy endpoints available"
            }
      ]
},
  },
  {
    id: "one-card_backup_status",
    label: "Backup Status",
    description: "Example: 'Show me backup status...'",
    dataType: "one-card.dataset",
    payload: {
      "backup_status": {
            "etcd_snapshots": {
                  "last_successful": "2024-10-03T02:30:00Z",
                  "frequency": "daily",
                  "retention_days": 30,
                  "storage_location": "s3://openshift-backups-prod",
                  "size_gb": 2.3,
                  "status": "healthy"
            },
            "velero_backups": {
                  "last_successful": "2024-10-03T01:00:00Z",
                  "frequency": "daily",
                  "retention_days": 90,
                  "storage_location": "s3://velero-backups-prod",
                  "applications_backed_up": 12,
                  "status": "healthy"
            },
            "recovery_time_objective": "4 hours",
            "recovery_point_objective": "1 hour",
            "last_recovery_test": "2024-09-15T10:00:00Z",
            "test_result": "successful"
      }
},
  },
  {
    id: "set-of-cards_persistent_volumes",
    label: "Persistent Volumes",
    description: "Example: 'Show me persistent volume status...'",
    dataType: "set-of-cards.dataset",
    payload: {
      "persistent_volumes": [
            {
                  "name": "pvc-database-prod",
                  "namespace": "production-app",
                  "status": "Bound",
                  "size": "100Gi",
                  "used": "78Gi",
                  "storage_class": "gp3-csi",
                  "access_mode": "ReadWriteOnce",
                  "mount_path": "/var/lib/postgresql/data",
                  "last_backup": "2024-10-03T01:00:00Z"
            },
            {
                  "name": "pvc-logs-storage",
                  "namespace": "openshift-logging",
                  "status": "Bound",
                  "size": "500Gi",
                  "used": "423Gi",
                  "storage_class": "gp3-csi",
                  "access_mode": "ReadWriteMany",
                  "mount_path": "/var/log/containers",
                  "last_backup": "2024-10-03T02:30:00Z"
            },
            {
                  "name": "pvc-temp-storage",
                  "namespace": "development",
                  "status": "Pending",
                  "size": "50Gi",
                  "used": "0Gi",
                  "storage_class": "gp3-csi",
                  "access_mode": "ReadWriteOnce",
                  "mount_path": "/tmp/data",
                  "error": "Insufficient storage capacity"
            }
      ]
},
  },
  {
    id: "set-of-cards_cluster_info",
    label: "Cluster Info",
    description: "Example: 'Show me OpenShift cluster status...'",
    dataType: "set-of-cards.dataset",
    payload: [
      {
            "cluster": {
                  "name": "prod-openshift-cluster",
                  "version": "4.14",
                  "provider": "AWS",
                  "region": "us-east-1",
                  "nodes": 5,
                  "status": "healthy",
                  "pods": 234,
                  "namespaces": 45,
                  "cpu_usage": "65%",
                  "memory_usage": "72%",
                  "created": "2024-01-15",
                  "url": "https://console-openshift-console.apps.prod.example.com",
                  "description": "Production OpenShift cluster running critical workloads"
            }
      },
      {
            "cluster": {
                  "name": "prod-openshift-us-east",
                  "status": "healthy",
                  "version": "4.14.8",
                  "nodes": 12,
                  "api_server_status": "running",
                  "etcd_health": "healthy",
                  "uptime_days": 45,
                  "last_backup": "2024-10-03T02:30:00Z",
                  "region": "us-east-1",
                  "cpu_usage_percent": 68,
                  "memory_usage_percent": 72,
                  "storage_usage_percent": 45,
                  "cluster_logo_url": "https://connect.redhat.com/sites/default/files/2021-06/OpenShift-LogoType.svg__0.png",
                  "monitoring_dashboard_url": "https://console-openshift-console.apps.prod.example.com/monitoring",
                  "cluster_overview_video_url": "https://youtu.be/XdlVs37KD1I?si=bKtqtOsPN95IgTGX"
            }
      },
      {
            "cluster": {
                  "name": "dev-openshift-us-west",
                  "status": "degraded",
                  "version": "4.13.12",
                  "nodes": 6,
                  "api_server_status": "running",
                  "etcd_health": "warning",
                  "uptime_days": 12,
                  "last_backup": "2024-10-02T02:30:00Z",
                  "region": "us-west-2",
                  "cpu_usage_percent": 45,
                  "memory_usage_percent": 89,
                  "storage_usage_percent": 78,
                  "cluster_logo_url": "https://connect.redhat.com/sites/default/files/2021-06/OpenShift-LogoType.svg__0.png",
                  "monitoring_dashboard_url": "https://console-openshift-console.apps.prod.example.com/monitoring",
                  "cluster_overview_video_url": "https://youtu.be/XdlVs37KD1I?si=bKtqtOsPN95IgTGX"
            }
      }
],
  },
  {
    id: "set-of-cards_namespaces",
    label: "Namespaces",
    description: "Example: 'Which namespaces consume the most resources?...'",
    dataType: "set-of-cards.dataset",
    payload: {
      "namespaces": [
            {
                  "name": "kube-system",
                  "cpu_requests": "2.1",
                  "cpu_limits": "4.0",
                  "cpu_usage": "1.8",
                  "memory_requests": "4.2Gi",
                  "memory_limits": "8.0Gi",
                  "memory_usage": "3.9Gi",
                  "pod_count": 18,
                  "cost_per_month": 245.5
            },
            {
                  "name": "openshift-monitoring",
                  "cpu_requests": "3.5",
                  "cpu_limits": "6.0",
                  "cpu_usage": "2.9",
                  "memory_requests": "8.1Gi",
                  "memory_limits": "12.0Gi",
                  "memory_usage": "7.8Gi",
                  "pod_count": 12,
                  "cost_per_month": 412.3
            },
            {
                  "name": "production-app",
                  "cpu_requests": "5.2",
                  "cpu_limits": "10.0",
                  "cpu_usage": "4.1",
                  "memory_requests": "12.5Gi",
                  "memory_limits": "20.0Gi",
                  "memory_usage": "11.2Gi",
                  "pod_count": 35,
                  "cost_per_month": 678.9
            },
            {
                  "name": "development",
                  "cpu_requests": "1.8",
                  "cpu_limits": "3.0",
                  "cpu_usage": "0.4",
                  "memory_requests": "3.2Gi",
                  "memory_limits": "6.0Gi",
                  "memory_usage": "1.1Gi",
                  "pod_count": 8,
                  "cost_per_month": 89.2,
                  "waste_percentage": 78
            }
      ]
},
  },
  {
    id: "set-of-cards_nodes",
    label: "Nodes",
    description: "Example: 'Show me all worker nodes...'",
    dataType: "set-of-cards.dataset",
    payload: {
      "nodes": [
            {
                  "name": "worker-01.prod.example.com",
                  "status": "Ready",
                  "cpu_usage": 65,
                  "memory_usage": 78,
                  "disk_usage": 42,
                  "pod_count": 24,
                  "version": "v1.27.6+f67aeb3",
                  "uptime_days": 45
            },
            {
                  "name": "worker-02.prod.example.com",
                  "status": "Ready",
                  "cpu_usage": 71,
                  "memory_usage": 68,
                  "disk_usage": 38,
                  "pod_count": 22,
                  "version": "v1.27.6+f67aeb3",
                  "uptime_days": 45
            },
            {
                  "name": "worker-03.prod.example.com",
                  "status": "NotReady",
                  "cpu_usage": 0,
                  "memory_usage": 0,
                  "disk_usage": 95,
                  "pod_count": 0,
                  "version": "v1.27.6+f67aeb3",
                  "uptime_days": 0,
                  "issue": "DiskPressure"
            }
      ]
},
  },
  {
    id: "set-of-cards_rbac_bindings",
    label: "Rbac Bindings",
    description: "Example: 'Who has cluster-admin access?...'",
    dataType: "set-of-cards.dataset",
    payload: {
      "rbac_bindings": [
            {
                  "user": "admin@redhat.com",
                  "role": "cluster-admin",
                  "type": "ClusterRoleBinding",
                  "namespace": "*",
                  "permissions": [
                        "*"
                  ],
                  "last_login": "2024-10-03T08:30:00Z",
                  "mfa_enabled": true
            },
            {
                  "user": "developer@redhat.com",
                  "role": "edit",
                  "type": "RoleBinding",
                  "namespace": "development",
                  "permissions": [
                        "get",
                        "list",
                        "create",
                        "update",
                        "delete"
                  ],
                  "last_login": "2024-10-03T07:15:00Z",
                  "mfa_enabled": true
            },
            {
                  "user": "viewer@redhat.com",
                  "role": "view",
                  "type": "RoleBinding",
                  "namespace": "production-app",
                  "permissions": [
                        "get",
                        "list"
                  ],
                  "last_login": "2024-10-02T16:45:00Z",
                  "mfa_enabled": false
            }
      ]
},
  },
  {
    id: "set-of-cards_failing_pods",
    label: "Failing Pods",
    description: "Example: 'Show me failing pods...'",
    dataType: "set-of-cards.dataset",
    payload: {
      "failing_pods": [
            {
                  "name": "payment-service-7d4b6c8f9-xk2j9",
                  "namespace": "production-app",
                  "status": "CrashLoopBackOff",
                  "restart_count": 15,
                  "last_restart": "2024-10-03T09:15:23Z",
                  "error_message": "Error: ECONNREFUSED connect to database",
                  "node": "worker-01.prod.example.com",
                  "image": "registry.redhat.io/payment-service:v2.1.3",
                  "cpu_limit": "500m",
                  "memory_limit": "1Gi"
            },
            {
                  "name": "user-auth-6b8d4f7c2-m9n4p",
                  "namespace": "production-app",
                  "status": "ImagePullBackOff",
                  "restart_count": 0,
                  "last_restart": "2024-10-03T08:45:12Z",
                  "error_message": "Failed to pull image: registry.redhat.io/user-auth:v1.5.2 not found",
                  "node": "worker-02.prod.example.com",
                  "image": "registry.redhat.io/user-auth:v1.5.2",
                  "cpu_limit": "200m",
                  "memory_limit": "512Mi"
            }
      ]
},
  },
  {
    id: "one-card_cluster_info",
    label: "Cluster Info",
    description: "Example: 'Tell me about prod-openshift-us-east cluster...'",
    dataType: "one-card.dataset",
    payload: [
      {
            "cluster": {
                  "name": "prod-openshift-cluster",
                  "version": "4.14",
                  "provider": "AWS",
                  "region": "us-east-1",
                  "nodes": 5,
                  "status": "healthy",
                  "pods": 234,
                  "namespaces": 45,
                  "cpu_usage": "65%",
                  "memory_usage": "72%",
                  "created": "2024-01-15",
                  "url": "https://console-openshift-console.apps.prod.example.com",
                  "description": "Production OpenShift cluster running critical workloads"
            }
      },
      {
            "cluster": {
                  "name": "prod-openshift-us-east",
                  "status": "healthy",
                  "version": "4.14.8",
                  "nodes": 12,
                  "api_server_status": "running",
                  "etcd_health": "healthy",
                  "uptime_days": 45,
                  "last_backup": "2024-10-03T02:30:00Z",
                  "region": "us-east-1",
                  "cpu_usage_percent": 68,
                  "memory_usage_percent": 72,
                  "storage_usage_percent": 45,
                  "cluster_logo_url": "https://connect.redhat.com/sites/default/files/2021-06/OpenShift-LogoType.svg__0.png",
                  "monitoring_dashboard_url": "https://console-openshift-console.apps.prod.example.com/monitoring",
                  "cluster_overview_video_url": "https://youtu.be/XdlVs37KD1I?si=bKtqtOsPN95IgTGX"
            }
      },
      {
            "cluster": {
                  "name": "dev-openshift-us-west",
                  "status": "degraded",
                  "version": "4.13.12",
                  "nodes": 6,
                  "api_server_status": "running",
                  "etcd_health": "warning",
                  "uptime_days": 12,
                  "last_backup": "2024-10-02T02:30:00Z",
                  "region": "us-west-2",
                  "cpu_usage_percent": 45,
                  "memory_usage_percent": 89,
                  "storage_usage_percent": 78,
                  "cluster_logo_url": "https://connect.redhat.com/sites/default/files/2021-06/OpenShift-LogoType.svg__0.png",
                  "monitoring_dashboard_url": "https://console-openshift-console.apps.prod.example.com/monitoring",
                  "cluster_overview_video_url": "https://youtu.be/XdlVs37KD1I?si=bKtqtOsPN95IgTGX"
            }
      }
],
  },
  {
    id: "set-of-cards_cost_efficiency",
    label: "Cost Efficiency",
    description: "Example: 'Show me cost analysis...'",
    dataType: "set-of-cards.dataset",
    payload: {
      "cost_efficiency": [
            {
                  "namespace": "production-app",
                  "monthly_cost": 1245.67,
                  "cpu_waste_percentage": 23,
                  "memory_waste_percentage": 31,
                  "suggested_savings": 387.45,
                  "right_sizing_recommendations": [
                        "Reduce payment-service memory from 2Gi to 1.2Gi",
                        "Reduce user-auth CPU from 1000m to 400m"
                  ]
            },
            {
                  "namespace": "development",
                  "monthly_cost": 456.23,
                  "cpu_waste_percentage": 67,
                  "memory_waste_percentage": 72,
                  "suggested_savings": 312.18,
                  "right_sizing_recommendations": [
                        "Use spot instances for dev workloads",
                        "Scale down replicas during off-hours"
                  ]
            }
      ]
},
  },
  {
    id: "table_cluster_info",
    label: "Cluster Info",
    description: "Example: 'Are all my clusters healthy?...'",
    dataType: "table.dataset",
    payload: [
      {
            "cluster": {
                  "name": "prod-openshift-cluster",
                  "version": "4.14",
                  "provider": "AWS",
                  "region": "us-east-1",
                  "nodes": 5,
                  "status": "healthy",
                  "pods": 234,
                  "namespaces": 45,
                  "cpu_usage": "65%",
                  "memory_usage": "72%",
                  "created": "2024-01-15",
                  "url": "https://console-openshift-console.apps.prod.example.com",
                  "description": "Production OpenShift cluster running critical workloads"
            }
      },
      {
            "cluster": {
                  "name": "prod-openshift-us-east",
                  "status": "healthy",
                  "version": "4.14.8",
                  "nodes": 12,
                  "api_server_status": "running",
                  "etcd_health": "healthy",
                  "uptime_days": 45,
                  "last_backup": "2024-10-03T02:30:00Z",
                  "region": "us-east-1",
                  "cpu_usage_percent": 68,
                  "memory_usage_percent": 72,
                  "storage_usage_percent": 45,
                  "cluster_logo_url": "https://connect.redhat.com/sites/default/files/2021-06/OpenShift-LogoType.svg__0.png",
                  "monitoring_dashboard_url": "https://console-openshift-console.apps.prod.example.com/monitoring",
                  "cluster_overview_video_url": "https://youtu.be/XdlVs37KD1I?si=bKtqtOsPN95IgTGX"
            }
      },
      {
            "cluster": {
                  "name": "dev-openshift-us-west",
                  "status": "degraded",
                  "version": "4.13.12",
                  "nodes": 6,
                  "api_server_status": "running",
                  "etcd_health": "warning",
                  "uptime_days": 12,
                  "last_backup": "2024-10-02T02:30:00Z",
                  "region": "us-west-2",
                  "cpu_usage_percent": 45,
                  "memory_usage_percent": 89,
                  "storage_usage_percent": 78,
                  "cluster_logo_url": "https://connect.redhat.com/sites/default/files/2021-06/OpenShift-LogoType.svg__0.png",
                  "monitoring_dashboard_url": "https://console-openshift-console.apps.prod.example.com/monitoring",
                  "cluster_overview_video_url": "https://youtu.be/XdlVs37KD1I?si=bKtqtOsPN95IgTGX"
            }
      }
],
  }];
