export type InlineDataset = {
  id: string;
  label: string;
  description: string;
  dataType?: string;
  payload: unknown;
};

export const INLINE_DATASETS: InlineDataset[] = [
  {
    id: "movies-default",
    label: "🎬 Current Movies Dataset",
    description:
      "Sample of the movies payload returned by the live agent (titles, genres, box office).",
    dataType: "movies.dataset",
    payload: [
      {
        movie: {
          title: "The Dark Knight",
          director: "Christopher Nolan",
          genres: ["Action", "Drama"],
          imdbRating: 9.0,
          budgetMillions: 185,
          revenueMillions: 1004,
        },
        metrics: {
          openingWeekendMillions: 158.4,
          weeksInTop10: 8,
        },
      },
      {
        movie: {
          title: "Interstellar",
          director: "Christopher Nolan",
          genres: ["Sci-Fi", "Drama"],
          imdbRating: 8.6,
          budgetMillions: 165,
          revenueMillions: 677,
        },
        metrics: {
          openingWeekendMillions: 47.5,
          weeksInTop10: 6,
        },
      },
      {
        movie: {
          title: "The Shawshank Redemption",
          director: "Frank Darabont",
          genres: ["Drama"],
          imdbRating: 9.3,
          budgetMillions: 25,
          revenueMillions: 28,
        },
        metrics: {
          openingWeekendMillions: 0.7,
          weeksInTop10: 5,
        },
      },
    ],
  },
  {
    id: "infra-kpis",
    label: "⚙️ Service Reliability KPIs",
    description:
      "Uptime, incidents, and deployment stats for three internal services.",
    dataType: "kpi.reliability",
    payload: [
      {
        service: "Identity API",
        owner: "Platform",
        uptimePercent: 99.97,
        incidentsThisQuarter: 1,
        avgResponseMs: 180,
        deploymentsPerWeek: 5,
      },
      {
        service: "Billing Engine",
        owner: "Finance",
        uptimePercent: 99.89,
        incidentsThisQuarter: 3,
        avgResponseMs: 240,
        deploymentsPerWeek: 2,
      },
      {
        service: "Notifications Hub",
        owner: "Eng Enablement",
        uptimePercent: 99.72,
        incidentsThisQuarter: 5,
        avgResponseMs: 310,
        deploymentsPerWeek: 7,
      },
    ],
  },
];

