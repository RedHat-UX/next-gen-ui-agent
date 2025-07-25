# Dynamic UI NPM Package

A collection of reusable React components to support dynamic UI rendering. This package includes wrappers for markdown, tables, accordions, messages, and more.

## Project Structure

public/ # Public static assets
src/
├── components/ # Core reusable components
├── constants/ # Component mapping logic
├── index.tsx # Entry point
└── test
        └── components
           └──/ # Unit tests
        └── setup.ts
└── index.html
└── vite.config.ts
└── package.json
└── package-lock.json
└── README.md


## Installation

npm install <package-name>
Note: Requires React 18+ and TypeScript.

Available Components:
- AccordianWrapper
- CodeBlockWrapper
- CustomLink
- DynamicComponents
- ListWrapper
- MarkdownWrapper
- Message
- QuickResponse
- TableWrapper


## Usage Example
```js
// <-- Accordian Component -->
import { AccordianWrapper } from '<package-name>';

function App() {
  return (
    <AccordianWrapper title="Click me">
      <p>This is hidden content!</p>
    </AccordianWrapper>
  );
}

// <-- OneCard Component -->
import { OneCardWrapper } from '<package-name>';

const mockData = {
  title: "Movie Details",
  image: "https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
  fields: [
    {
      name: "Title",
      data_path: "movie.title",
      data: ["Toy Story"]
    },
    {
      name: "Year",
      data_path: "movie.year",
      data: [1995]
    },
    {
      name: "Genres",
      data_path: "movie.genres",
      data: ["Animation", "Adventure"]
    }
  ],
  imageSize: "md",
  id: "movie-card",
};

function App() {
  return <OneCardWrapper {...mockData} />;
}
```

## Development

npm install
npm run build #Generates the package in /dist
npm link dynamicui


## Testing
- Running Tests

Below are detailed instructions for running your tests.

`Install Dependencies`
npm install
-Installs all project dependencies, including the internal test setup package.

1. Run All Tests (Watch Mode)
npm test
-Starts Jest in watch mode, re-running relevant tests as you save changes.

2. Run Tests Once (CI Mode)
npm run test:ci
-Executes the entire test suite a single time without watching.

3. Run a Specific Test File
You can target a single test file like so:

npm test -- src/test/components/ComponentName.test.tsx 

Or using the run keyword:

npm run test -- src/test/components/ComponentName.test.tsx 

Replace ComponentName with the actual file name you wish to test.

`NPM Scripts`
The following scripts are available via package.json:

{
  "scripts": {
    "test": "jest",
  }
}
npm test → Runs all tests in watch mode.
npm run test:ci → Runs all tests once, useful for CI pipelines.

`Test Setup Details`
Global config (e.g., @testing-library/jest-dom) is handled by setupTests.ts via our internal npm package.
Test files follow the pattern *.test.tsx or *.test.js and are placed in: tests folders


## License
For open source projects, say how it is licensed.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.