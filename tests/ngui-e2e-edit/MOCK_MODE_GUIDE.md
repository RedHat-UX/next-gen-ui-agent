# Mock Mode Guide

## Overview

Mock Mode allows you to test and preview UI components without running the full agent pipeline. This is perfect for:

- **UI Development**: Quickly iterate on component styling and layout
- **Component Testing**: Verify component rendering with different data
- **Demo Preparation**: Show specific components without agent delays
- **Debugging**: Isolate component rendering issues from agent logic

## How to Use Mock Mode

### 1. Enable Mock Mode

Toggle the **"Mock Mode (Test UI without Agent)"** switch at the top of the chatbot interface.

When enabled:
- The chatbot won't send requests to the backend agent
- You can select pre-configured mock components or provide custom JSON

### 2. Select Pre-configured Mock Components

Use the dropdown menu to select from 8 pre-configured component examples:

#### Available Mock Components:

1. **One Card - Movie Details**
   - Single movie card with detailed information (title, year, rating, actors)
   
2. **Image - Movie Poster**
   - Simple image display component

3. **Video Player - Trailer**
   - YouTube video player for movie trailers

4. **Chart - Box Office Revenue**
   - Bar chart comparing box office revenue across movies

5. **Chart - Weekly Box Office**
   - Line chart showing weekly revenue trends

6. **Chart - Multi-line Revenue Trends**
   - Multi-line chart comparing multiple movies

7. **Table - Movie Comparison**
   - Table displaying multiple movies with sortable columns

8. **Set of Cards - Multiple Movies**
   - Card grid displaying multiple movie cards

### 3. Use Custom JSON

Click **"Show Custom JSON Input"** to test your own component configurations:

1. Paste your component JSON into the text area
2. Click **"Send Custom JSON"** to render it
3. If there's a JSON syntax error, you'll see an error message

#### Example Custom JSON:

```json
{
  "component": "one-card",
  "id": "custom-card",
  "title": "Custom Component",
  "fields": [
    {
      "data": ["Test Value"],
      "data_path": "test.field",
      "name": "Field Name"
    }
  ]
}
```

### 4. Switch Back to Live Mode

Toggle the switch off to return to the live agent mode and use the real backend.

## Component Schemas

All mock components follow the schema definitions in `/spec/component/`. See:

- `one-card.schema.json`
- `image.schema.json`
- `video-player.schema.json`
- `chart.schema.json`
- `table.schema.json`
- `set-of-cards.schema.json`

For detailed schema documentation, see: `/spec/component/README.md`

## Adding New Mock Data

To add new mock component configurations:

1. Open `src/mockData.ts`
2. Add a new object to the `mockComponentData` array:

```typescript
{
  name: "Your Component Name",
  description: "Brief description",
  config: {
    // Your component configuration JSON
  }
}
```

3. Save the file and refresh the app
4. Your new mock will appear in the dropdown

## Tips

- **Development Workflow**: Use mock mode to rapidly test styling changes
- **Custom JSON Testing**: Test edge cases by providing unusual data configurations
- **Demo Mode**: Pre-select specific mocks to show during presentations
- **Debug Raw Config**: The `showRawConfig` prop is enabled, so you can always see the raw JSON being passed to components

## Troubleshooting

### Component Not Rendering

1. Check the raw config in the error message
2. Verify JSON syntax in custom JSON input
3. Ensure required fields are present (id, component, etc.)
4. Check browser console for detailed error messages

### Mock Not Appearing

- Ensure mock mode is enabled (switch is on)
- Check that the component name exists in `mockData.ts`
- Refresh the page if you recently added new mocks

## Technical Details

### Files Modified

- `src/mockData.ts` - Mock component data library
- `src/components/MockModeToggle.tsx` - Mock mode UI controls
- `src/components/ChatBot.tsx` - Integrated mock mode logic

### How It Works

1. When mock mode is enabled, `handleSend` returns early with a message
2. Mock selection triggers `handleMockSend` which injects the component directly
3. Custom JSON is validated and sent through the same `handleMockSend` function
4. Components are rendered using the same `DynamicComponent` as live mode

This ensures mock components render identically to live components.

