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
    prompt: 'Show details about Toy Story',
    description: 'Single movie card with details',
    expectedComponent: 'one-card',
    icon: '🎴'
  },
  {
    id: 'card-multiple',
    category: 'cards',
    prompt: 'Show Christopher Nolan movies as cards',
    description: 'Multiple movie cards',
    expectedComponent: 'set-of-cards',
    icon: '🎴'
  },

  // Tables
  {
    id: 'table-list',
    category: 'tables',
    prompt: 'List all movies',
    description: 'Test "list" keyword for table selection',
    expectedComponent: 'table',
    icon: '📝'
  },
  {
    id: 'table-comparison',
    category: 'tables',
    prompt: 'Compare movie ratings and revenue in a table',
    description: 'Explicit table request with multiple fields',
    expectedComponent: 'table',
    icon: '📊'
  },

  // Charts - Bar
  {
    id: 'chart-revenue',
    category: 'charts',
    prompt: 'Compare box office revenue',
    description: 'Bar chart - single metric comparison',
    expectedComponent: 'chart',
    icon: '📊'
  },
  {
    id: 'chart-revenue-all',
    category: 'charts',
    prompt: 'Compare revenue across all movies',
    description: 'Bar chart - multiple items, single metric',
    expectedComponent: 'chart',
    icon: '📊'
  },
  {
    id: 'chart-directors',
    category: 'charts',
    prompt: 'Compare average ratings by director',
    description: 'Horizontal bar - long labels test',
    expectedComponent: 'chart',
    icon: '🎭'
  },

  // Charts - Line
  {
    id: 'chart-weekly',
    category: 'charts',
    prompt: 'Show weekly revenue trends',
    description: 'Line chart - time series data',
    expectedComponent: 'chart',
    icon: '📈'
  },

  // Charts - Mirrored Bar
  {
    id: 'chart-two-metrics',
    category: 'charts',
    prompt: 'Compare ROI and budget for all movies',
    description: 'Mirrored bar - two different metrics',
    expectedComponent: 'chart',
    icon: '⚖️'
  },

  // Charts - Pie & Donut
  {
    id: 'chart-genre-distribution',
    category: 'charts',
    prompt: 'Show genre distribution',
    description: 'Test if LLM picks pie/donut naturally',
    expectedComponent: 'chart',
    icon: '🥧'
  },
  {
    id: 'chart-genre-pie',
    category: 'charts',
    prompt: 'Show genre distribution as a pie chart',
    description: 'Explicit pie chart request',
    expectedComponent: 'chart',
    icon: '🥧'
  },
  {
    id: 'chart-rating-donut',
    category: 'charts',
    prompt: 'Show rating distribution as a donut chart',
    description: 'Explicit donut chart request',
    expectedComponent: 'chart',
    icon: '🍩'
  },

  // Media
  {
    id: 'media-poster',
    category: 'media',
    prompt: 'Show the Toy Story poster',
    description: 'Image display',
    expectedComponent: 'image',
    icon: '🖼️'
  },
  {
    id: 'media-trailer',
    category: 'media',
    prompt: 'Play the Toy Story trailer',
    description: 'Video player',
    expectedComponent: 'video-player',
    icon: '🎥'
  },

  // Mixed / Ambiguous
  {
    id: 'mixed-movies',
    category: 'mixed',
    prompt: 'Show me all movies',
    description: 'Ambiguous - could be cards or table',
    expectedComponent: 'multiple',
    icon: '🎬'
  },
  {
    id: 'mixed-best-rated',
    category: 'mixed',
    prompt: 'Which movies have the best ratings?',
    description: 'Question format - test component selection',
    expectedComponent: 'multiple',
    icon: '⭐'
  },
  {
    id: 'mixed-analysis',
    category: 'mixed',
    prompt: 'Show highest grossing movies',
    description: 'Could be table or chart',
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

