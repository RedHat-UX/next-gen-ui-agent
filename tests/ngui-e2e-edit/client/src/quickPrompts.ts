// Quick prompt suggestions for testing different component types through the LLM

export type QuickPromptCategory = 'cards' | 'tables' | 'charts' | 'media' | 'mixed';

export interface QuickPrompt {
  id: string;
  category: QuickPromptCategory;
  prompt: string;
  description: string;
  expectedComponent: string;
  icon?: string;
}

export const quickPrompts: QuickPrompt[] = [
  // Cards
  {
    id: 'card-single',
    category: 'cards',
    prompt: 'Show me details about Toy Story',
    description: 'Single movie card with details',
    expectedComponent: 'one-card',
    icon: '🎴'
  },
  {
    id: 'card-multiple',
    category: 'cards',
    prompt: 'Show me Christopher Nolan movies',
    description: 'Multiple movie cards',
    expectedComponent: 'set-of-cards',
    icon: '🎴'
  },
  {
    id: 'card-top-rated',
    category: 'cards',
    prompt: 'Show me top rated movies',
    description: 'Card grid of highly rated movies',
    expectedComponent: 'set-of-cards',
    icon: '⭐'
  },

  // Tables
  {
    id: 'table-all',
    category: 'tables',
    prompt: 'Show me all movies in a table',
    description: 'Table with all movie data',
    expectedComponent: 'table',
    icon: '📋'
  },
  {
    id: 'table-comparison',
    category: 'tables',
    prompt: 'Compare Toy Story, The Matrix, and Inception',
    description: 'Side-by-side movie comparison table',
    expectedComponent: 'table',
    icon: '📊'
  },
  {
    id: 'table-ratings',
    category: 'tables',
    prompt: 'Show me a table of movie ratings and revenue',
    description: 'Table focused on ratings and financials',
    expectedComponent: 'table',
    icon: '💰'
  },

  // Charts - Bar
  {
    id: 'chart-revenue',
    category: 'charts',
    prompt: 'Compare box office revenue of all movies',
    description: 'Bar chart of total revenue',
    expectedComponent: 'chart',
    icon: '📊'
  },
  {
    id: 'chart-opening-weekend',
    category: 'charts',
    prompt: 'Compare opening weekend revenue',
    description: 'Bar chart of opening weekends',
    expectedComponent: 'chart',
    icon: '🎬'
  },
  {
    id: 'chart-roi',
    category: 'charts',
    prompt: 'Show me ROI comparison for all movies',
    description: 'Bar chart comparing return on investment',
    expectedComponent: 'chart',
    icon: '💹'
  },

  // Charts - Line
  {
    id: 'chart-weekly',
    category: 'charts',
    prompt: 'Show weekly box office for Toy Story',
    description: 'Line chart of weekly revenue trends',
    expectedComponent: 'chart',
    icon: '📈'
  },
  {
    id: 'chart-trends',
    category: 'charts',
    prompt: 'Compare weekly revenue trends for The Dark Knight and Inception',
    description: 'Multi-line chart comparison',
    expectedComponent: 'chart',
    icon: '📉'
  },
  {
    id: 'chart-weekly-trends',
    category: 'charts',
    prompt: 'Weekly Revenue Trends',
    description: 'Multi-series line chart with nested time-series data',
    expectedComponent: 'chart',
    icon: '📈'
  },
  {
    id: 'chart-mirrored',
    category: 'charts',
    prompt: 'Compare ROI and budget for all movies',
    description: 'Mirrored bar chart showing two metrics',
    expectedComponent: 'chart',
    icon: '⚖️'
  },

  // Charts - Pie & Donut
  {
    id: 'chart-genre-pie',
    category: 'charts',
    prompt: 'Show genre distribution as a pie chart',
    description: 'Pie chart of movie genres',
    expectedComponent: 'chart',
    icon: '🥧'
  },
  {
    id: 'chart-rating-donut',
    category: 'charts',
    prompt: 'Show rating distribution as a donut chart',
    description: 'Donut chart of rating categories',
    expectedComponent: 'chart',
    icon: '🍩'
  },

  // Charts - More Mirrored Bar
  {
    id: 'chart-revenue-profit',
    category: 'charts',
    prompt: 'Compare revenue and profit for all movies',
    description: 'Mirrored bar showing revenue vs profit',
    expectedComponent: 'chart',
    icon: '💰'
  },
  {
    id: 'chart-opening-total',
    category: 'charts',
    prompt: 'Compare opening weekend and total revenue',
    description: 'Mirrored bar showing opening vs total',
    expectedComponent: 'chart',
    icon: '🎬'
  },

  // Charts - More Bar & Line
  {
    id: 'chart-directors',
    category: 'charts',
    prompt: 'Show average ratings by director',
    description: 'Horizontal bar chart (long labels)',
    expectedComponent: 'chart',
    icon: '🎭'
  },
  {
    id: 'chart-long-titles',
    category: 'charts',
    prompt: 'Show revenue for movies with long titles',
    description: 'Horizontal bar chart with long movie titles',
    expectedComponent: 'chart',
    icon: '📏'
  },
  {
    id: 'chart-daily-box-office',
    category: 'charts',
    prompt: 'Show daily box office for opening week of The Dark Knight',
    description: 'Line chart of daily performance',
    expectedComponent: 'chart',
    icon: '📊'
  },
  {
    id: 'chart-yearly-trends',
    category: 'charts',
    prompt: 'Show movie rating trends over the years',
    description: 'Line chart of rating trends by year',
    expectedComponent: 'chart',
    icon: '📅'
  },

  // Media
  {
    id: 'media-poster',
    category: 'media',
    prompt: 'Show me the poster for Toy Story',
    description: 'Image display of movie poster',
    expectedComponent: 'image',
    icon: '🖼️'
  },
  {
    id: 'media-trailer',
    category: 'media',
    prompt: 'Play Toy Story trailer',
    description: 'Video player with trailer',
    expectedComponent: 'video-player',
    icon: '🎥'
  },
  {
    id: 'media-interstellar',
    category: 'media',
    prompt: 'Show me Interstellar trailer',
    description: 'Video player for different movie',
    expectedComponent: 'video-player',
    icon: '🚀'
  },

  // Mixed / Complex
  {
    id: 'mixed-details',
    category: 'mixed',
    prompt: 'Tell me about Toy Story including poster and trailer',
    description: 'Multiple components (poster, details, video)',
    expectedComponent: 'multiple',
    icon: '🎭'
  },
  {
    id: 'mixed-analysis',
    category: 'mixed',
    prompt: 'Show me highest grossing movies with a chart',
    description: 'Table + Chart combination',
    expectedComponent: 'multiple',
    icon: '📊'
  },
];

// Group prompts by category
export const groupedPrompts = {
  cards: quickPrompts.filter(p => p.category === 'cards'),
  tables: quickPrompts.filter(p => p.category === 'tables'),
  charts: quickPrompts.filter(p => p.category === 'charts'),
  media: quickPrompts.filter(p => p.category === 'media'),
  mixed: quickPrompts.filter(p => p.category === 'mixed'),
};

// Get a random prompt from a category
export const getRandomPrompt = (category?: QuickPromptCategory): QuickPrompt => {
  const prompts = category ? quickPrompts.filter(p => p.category === category) : quickPrompts;
  return prompts[Math.floor(Math.random() * prompts.length)];
};

