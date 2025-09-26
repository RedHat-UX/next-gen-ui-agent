# Node.js Upgrade Guide

## Issue

You're currently using Node.js v12.22.12, but this project requires Node.js 18+ to run Vite 7.

**Error you're seeing:**

```
SyntaxError: Unexpected token '.'
    at Loader.moduleStrategy (internal/modules/esm/translators.js:140:18)
```

## Solution: Upgrade Node.js

### Option 1: Using Homebrew (Recommended for macOS)

```bash
# Install latest Node.js LTS
brew install node

# Verify installation
node --version
```

### Option 2: Using Node Version Manager (nvm)

```bash
# Install nvm (if not already installed)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Restart terminal or run:
source ~/.bashrc

# Install and use Node.js 18 LTS
nvm install 18
nvm use 18
nvm alias default 18

# Verify installation
node --version
```

### Option 3: Download from Official Website

1. Go to [https://nodejs.org/](https://nodejs.org/)
2. Download the LTS version (18.x or 20.x)
3. Run the installer
4. Restart your terminal

## After Upgrading

1. **Verify Node.js version:**

   ```bash
   node --version
   # Should show v18.x.x or v20.x.x
   ```

2. **Clear npm cache (optional but recommended):**

   ```bash
   npm cache clean --force
   ```

3. **Reinstall dependencies:**

   ```bash
   cd /Users/anujrajak/Projects/research/ngui-e2e/NGUI-e2e
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

## Expected Result

After upgrading, `npm run dev` should start successfully and you'll see:

```
  VITE v7.x.x  ready in Xms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

## Features Available After Fix

- ✅ Full-screen AI chatbot interface
- ✅ Dark mode toggle (sun/moon icons in header)
- ✅ Two pre-loaded mock messages
- ✅ Real-time message input with send button
- ✅ Typing indicator when AI is responding
- ✅ Auto-scroll to latest messages
- ✅ Keyboard shortcuts (Enter to send)
- ✅ Professional PatternFly styling

Your chatbot will be ready to use with all the features you requested!
