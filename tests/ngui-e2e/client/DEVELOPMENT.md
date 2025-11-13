# Development Setup

This guide covers local development setup for the NGUI E2E Client, including linking the `@rhngui/patternfly-react-renderer` package for active development.

## Local Package Linking

When actively developing the UI components alongside this client application, you'll need to link the `@rhngui/patternfly-react-renderer` package locally.

### Setup @rhngui/patternfly-react-renderer

The `@rhngui/patternfly-react-renderer` package comes from the [next-gen-ui-react](https://github.com/RedHat-UX/next-gen-ui-react) repository.

1. **Clone and setup the package repository:**

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/RedHat-UX/next-gen-ui-react.git
cd next-gen-ui-react

# Install dependencies
npm install

# Build the package
npm run build

# Create a global npm link
npm link
```

2. **Link the package to this client:**

```bash
# Navigate to the client directory
cd /path/to/next-gen-ui-agent/tests/ngui-e2e/client

# Install dependencies
npm install

# Link to the local @rhngui/patternfly-react-renderer package
npm link @rhngui/patternfly-react-renderer
```

### Verifying the Link

You can verify the link is working by checking the `node_modules` directory:

```bash
ls -la node_modules/@rhngui/patternfly-react-renderer
```

This should show a symlink pointing to your local `next-gen-ui-react` directory.

### Working with Linked Packages

When the package is linked:

- Changes to the `next-gen-ui-react` package require rebuilding:
  ```bash
  cd /path/to/next-gen-ui-react
  npm run build
  ```
- The Vite dev server may need to be restarted to pick up changes
- Hot reload will work for changes in the client code, but not for linked package changes

### Unlinking

To remove the link and use the published npm package instead:

```bash
npm unlink @rhngui/patternfly-react-renderer
npm install
```

## Development Workflow

### Recommended Setup

1. **Terminal 1** - Run the backend server:
   ```bash
   cd tests/ngui-e2e/server
   ./start_server.sh
   ```

2. **Terminal 2** - Run the client dev server:
   ```bash
   cd tests/ngui-e2e/client
   npm run dev
   ```

3. **Terminal 3** - (Optional) Watch and rebuild linked packages:
   ```bash
   cd /path/to/next-gen-ui-react
   npm run build -- --watch  # If watch mode is available
   ```

### Debug Mode

For development and testing, use debug mode to access additional tools:

```
http://localhost:5173/?debug=true
```

See the main README for more information about debug mode features.

## Troubleshooting

### "Cannot find module '@rhngui/patternfly-react-renderer'"

This usually means the link is broken or not established. Try:

```bash
# Re-establish the link
npm unlink @rhngui/patternfly-react-renderer
npm link @rhngui/patternfly-react-renderer
```

### Changes not reflecting

1. Rebuild the linked package:
   ```bash
   cd /path/to/next-gen-ui-react
   npm run build
   ```

2. Restart the Vite dev server:
   ```bash
   # In the client directory
   # Ctrl+C to stop, then:
   npm run dev
   ```

### Multiple versions error

If you see React version conflicts:

```bash
# In next-gen-ui-react directory, link React from the client
cd /path/to/next-gen-ui-react
npm link ../../../tests/ngui-e2e/client/node_modules/react
```

