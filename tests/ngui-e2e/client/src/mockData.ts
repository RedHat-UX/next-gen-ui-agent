// Mock component configurations for testing UI rendering without the agent

export type MockDataItem = {
  name: string;
  description: string;
  config: any;
};

export const mockComponentData: MockDataItem[] = [
  {
    name: "One Card - Movie Details",
    description: "Single movie card with detailed information",
    config: {
      component: "one-card",
      id: "toy-story-card",
      title: "Toy Story Details",
      image: "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
      fields: [
        {
          data: ["Toy Story"],
          data_path: "movie.title",
          name: "Title"
        },
        {
          data: [1995],
          data_path: "movie.year",
          name: "Year"
        },
        {
          data: [8.3],
          data_path: "movie.imdbRating",
          name: "IMDB Rating"
        },
        {
          data: ["1995-11-22"],
          data_path: "movie.released",
          name: "Release Date"
        },
        {
          data: ["Jim Varney", "Tim Allen", "Tom Hanks", "Don Rickles"],
          data_path: "actors[*]",
          name: "Actors"
        }
      ]
    }
  },
  {
    name: "Image - Movie Poster",
    description: "Simple image display component",
    config: {
      component: "image",
      id: "toy-story-poster",
      image: "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
      title: "Toy Story Poster"
    }
  },
  {
    name: "Video Player - Trailer",
    description: "YouTube video player for movie trailer",
    config: {
      component: "video-player",
      id: "toy-story-trailer",
      title: "Toy Story Trailer",
      video: "https://www.youtube.com/embed/v-PjgYDrg70",
      video_img: "https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg"
    }
  },
  {
    name: "Chart - Box Office Revenue",
    description: "Bar chart showing box office comparison",
    config: {
      component: "chart",
      id: "box-office-chart",
      title: "Box Office Revenue Comparison",
      chartType: "bar",
      data: [
        {
          name: "Revenue (Millions)",
          data: [
            { x: "Toy Story", y: 373 },
            { x: "The Dark Knight", y: 1004 },
            { x: "Inception", y: 836 },
            { x: "The Matrix", y: 463 },
            { x: "Interstellar", y: 677 }
          ]
        }
      ],
      themeColor: "blue"
    }
  },
  {
    name: "Chart - Weekly Box Office",
    description: "Line chart showing weekly box office trends",
    config: {
      component: "chart",
      id: "weekly-box-office-chart",
      title: "Toy Story - Weekly Box Office",
      chartType: "line",
      data: [
        {
          name: "Revenue",
          data: [
            { x: "Week 1", y: 29140617 },
            { x: "Week 2", y: 18923456 },
            { x: "Week 3", y: 15234567 },
            { x: "Week 4", y: 12345678 }
          ]
        }
      ],
      themeColor: "green"
    }
  },
  {
    name: "Chart - Multi-line Revenue Trends",
    description: "Multi-line chart comparing multiple movies",
    config: {
      component: "chart",
      id: "multi-line-chart",
      title: "Weekly Revenue Comparison",
      chartType: "line",
      data: [
        {
          name: "Toy Story",
          data: [
            { x: "Week 1", y: 29140617 },
            { x: "Week 2", y: 18923456 },
            { x: "Week 3", y: 15234567 },
            { x: "Week 4", y: 12345678 }
          ]
        },
        {
          name: "The Dark Knight",
          data: [
            { x: "Week 1", y: 158411483 },
            { x: "Week 2", y: 75165786 },
            { x: "Week 3", y: 42674614 },
            { x: "Week 4", y: 26088337 }
          ]
        }
      ],
      themeColor: "multi"
    }
  },
  {
    name: "Chart - Mirrored Bar (ROI vs Budget)",
    description: "Mirrored bar chart comparing two metrics",
    config: {
      component: "chart",
      id: "mirrored-bar-chart",
      title: "ROI vs Budget Comparison",
      chartType: "mirrored-bar",
      data: [
        {
          name: "ROI",
          data: [
            { x: "Toy Story", y: 11.45 },
            { x: "The Dark Knight", y: 4.43 },
            { x: "Inception", y: 4.23 },
            { x: "The Matrix", y: 6.36 },
            { x: "Interstellar", y: 3.11 }
          ]
        },
        {
          name: "Budget (Millions)",
          data: [
            { x: "Toy Story", y: 30 },
            { x: "The Dark Knight", y: 185 },
            { x: "Inception", y: 160 },
            { x: "The Matrix", y: 63 },
            { x: "Interstellar", y: 165 }
          ]
        }
      ]
    }
  },
  {
    name: "Chart - Pie (Genre Distribution)",
    description: "Pie chart showing genre popularity",
    config: {
      component: "chart",
      id: "genre-pie-chart",
      title: "Movies by Genre",
      chartType: "pie",
      data: [
        {
          name: "Genres",
          data: [
            { x: "Action", y: 12 },
            { x: "Drama", y: 18 },
            { x: "Sci-Fi", y: 8 },
            { x: "Comedy", y: 15 },
            { x: "Thriller", y: 10 }
          ]
        }
      ]
    }
  },
  {
    name: "Chart - Donut (Rating Distribution)",
    description: "Donut chart showing rating categories",
    config: {
      component: "chart",
      id: "rating-donut-chart",
      title: "Movies by Rating Category",
      chartType: "donut",
      data: [
        {
          name: "Ratings",
          data: [
            { x: "Excellent (9-10)", y: 8 },
            { x: "Great (8-9)", y: 15 },
            { x: "Good (7-8)", y: 22 },
            { x: "Average (6-7)", y: 12 },
            { x: "Below Average (<6)", y: 5 }
          ]
        }
      ],
      donutSubTitle: "Total Movies"
    }
  },
  {
    name: "Chart - Line (Box Office Trends)",
    description: "Line chart showing daily box office performance",
    config: {
      component: "chart",
      id: "box-office-line-chart",
      title: "Daily Box Office - Opening Week",
      chartType: "line",
      data: [
        {
          name: "The Dark Knight",
          data: [
            { x: "Fri", y: 67165092 },
            { x: "Sat", y: 55647673 },
            { x: "Sun", y: 35598718 },
            { x: "Mon", y: 24834515 },
            { x: "Tue", y: 20456789 },
            { x: "Wed", y: 18234567 },
            { x: "Thu", y: 16543210 }
          ]
        },
        {
          name: "Inception",
          data: [
            { x: "Fri", y: 21512120 },
            { x: "Sat", y: 28567890 },
            { x: "Sun", y: 21234567 },
            { x: "Mon", y: 15678901 },
            { x: "Tue", y: 13456789 },
            { x: "Wed", y: 12345678 },
            { x: "Thu", y: 11234567 }
          ]
        }
      ],
      themeColor: "multi"
    }
  },
  {
    name: "Chart - Mirrored Bar (Revenue vs Profit)",
    description: "Mirrored bar comparing revenue and profit",
    config: {
      component: "chart",
      id: "revenue-profit-mirrored",
      title: "Revenue vs Profit Analysis",
      chartType: "mirrored-bar",
      data: [
        {
          name: "Total Revenue (Millions)",
          data: [
            { x: "Toy Story", y: 373.55 },
            { x: "The Dark Knight", y: 1004.56 },
            { x: "Inception", y: 836.85 },
            { x: "The Matrix", y: 463.52 },
            { x: "Interstellar", y: 677.47 }
          ]
        },
        {
          name: "Profit (Millions)",
          data: [
            { x: "Toy Story", y: 343.55 },
            { x: "The Dark Knight", y: 819.56 },
            { x: "Inception", y: 676.85 },
            { x: "The Matrix", y: 400.52 },
            { x: "Interstellar", y: 512.47 }
          ]
        }
      ]
    }
  },
  {
    name: "Chart - Bar (Director Comparison)",
    description: "Bar chart comparing directors by average rating",
    config: {
      component: "chart",
      id: "director-bar-chart",
      title: "Average Rating by Director",
      chartType: "bar",
      data: [
        {
          name: "Average Rating",
          data: [
            { x: "Christopher Nolan", y: 8.7 },
            { x: "Quentin Tarantino", y: 8.5 },
            { x: "Steven Spielberg", y: 8.3 },
            { x: "Martin Scorsese", y: 8.6 },
            { x: "Ridley Scott", y: 8.1 }
          ]
        }
      ],
      themeColor: "blue",
      horizontal: true
    }
  },
  {
    name: "Chart - Horizontal Bar (Long Movie Titles)",
    description: "Horizontal bar chart with long movie titles",
    config: {
      component: "chart",
      id: "long-titles-horizontal",
      title: "Top Revenue by Movie Title",
      chartType: "bar",
      data: [
        {
          name: "Revenue (Millions)",
          data: [
            { x: "The Shawshank Redemption", y: 58.3 },
            { x: "The Lord of the Rings: The Return of the King", y: 1119.9 },
            { x: "Pirates of the Caribbean: Dead Man's Chest", y: 1066.2 },
            { x: "Harry Potter and the Deathly Hallows – Part 2", y: 1342.0 },
            { x: "The Dark Knight Rises", y: 1081.0 }
          ]
        }
      ],
      themeColor: "green",
      horizontal: true
    }
  },
  {
    name: "Chart - Line (Rating Trends Over Time)",
    description: "Line chart showing rating trends by release year",
    config: {
      component: "chart",
      id: "rating-trend-line",
      title: "Average Movie Ratings by Year",
      chartType: "line",
      data: [
        {
          name: "Average IMDB Rating",
          data: [
            { x: "1995", y: 7.8 },
            { x: "2000", y: 8.1 },
            { x: "2005", y: 8.3 },
            { x: "2010", y: 8.7 },
            { x: "2015", y: 8.4 },
            { x: "2020", y: 8.2 }
          ]
        }
      ],
      themeColor: "green"
    }
  },
  {
    name: "Chart - Mirrored Bar (Opening vs Total)",
    description: "Mirrored bar comparing opening weekend to total revenue",
    config: {
      component: "chart",
      id: "opening-total-mirrored",
      title: "Opening Weekend vs Total Revenue",
      chartType: "mirrored-bar",
      data: [
        {
          name: "Opening Weekend (Millions)",
          data: [
            { x: "Toy Story", y: 29.14 },
            { x: "The Dark Knight", y: 158.41 },
            { x: "Inception", y: 62.79 },
            { x: "The Matrix", y: 27.79 },
            { x: "Interstellar", y: 47.51 }
          ]
        },
        {
          name: "Total Revenue (Millions)",
          data: [
            { x: "Toy Story", y: 373.55 },
            { x: "The Dark Knight", y: 1004.56 },
            { x: "Inception", y: 836.85 },
            { x: "The Matrix", y: 463.52 },
            { x: "Interstellar", y: 677.47 }
          ]
        }
      ]
    }
  },
  {
    name: "Table - Movie Comparison",
    description: "Table displaying multiple movies",
    config: {
      component: "table",
      id: "movies-table",
      title: "Top Rated Movies",
      fields: [
        {
          data: ["Toy Story", "The Shawshank Redemption", "The Dark Knight"],
          data_path: "movie.title",
          name: "Title"
        },
        {
          data: [1995, 1994, 2008],
          data_path: "movie.year",
          name: "Year"
        },
        {
          data: [8.3, 9.3, 9.0],
          data_path: "movie.imdbRating",
          name: "IMDB Rating"
        },
        {
          data: [373554033, 28341469, 1004558444],
          data_path: "movie.revenue",
          name: "Revenue"
        }
      ]
    }
  },
  {
    name: "Set of Cards - Multiple Movies",
    description: "Card grid displaying multiple movies",
    config: {
      component: "set-of-cards",
      id: "movies-cards",
      title: "Christopher Nolan Films",
      fields: [
        {
          data: ["The Dark Knight", "Inception", "Interstellar"],
          data_path: "movie.title",
          name: "Title"
        },
        {
          data: [2008, 2010, 2014],
          data_path: "movie.year",
          name: "Year"
        },
        {
          data: [9.0, 8.8, 8.6],
          data_path: "movie.imdbRating",
          name: "Rating"
        },
        {
          data: [
            ["Christian Bale", "Heath Ledger", "Aaron Eckhart"],
            ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page"],
            ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"]
          ],
          data_path: "actors[*]",
          name: "Cast"
        }
      ]
    }
  }
];

// Helper to get mock data by name
export const getMockDataByName = (name: string): any | undefined => {
  const item = mockComponentData.find(item => item.name === name);
  return item?.config;
};

// Helper to get all mock data names for selection
export const getMockDataNames = (): string[] => {
  return mockComponentData.map(item => item.name);
};

