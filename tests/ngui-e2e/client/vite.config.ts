import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";
import fs from "fs";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    // Serve web component TypeScript sources at /ngui-elements/ paths
    {
      name: 'serve-web-components',
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          if (req.url?.startsWith('/ngui-elements/')) {
            // Map /ngui-elements/ngui-card.js → libs/next_gen_ui_web/elements/ngui-card.ts
            const filename = req.url.replace('/ngui-elements/', '').replace('.js', '.ts');
            const tsPath = path.resolve(__dirname, '../../../libs/next_gen_ui_web/elements', filename);

            if (fs.existsSync(tsPath)) {
              // Rewrite the URL so Vite processes the TypeScript file
              req.url = '/@fs/' + tsPath;
            }
          }
          next();
        });
      },
    },
  ],
  resolve: {
    alias: {
      // Point to TypeScript sources - Vite will compile on the fly
      '@rhngui/web/ngui-card.js': path.resolve(__dirname, '../../../libs/next_gen_ui_web/elements/ngui-card.ts'),
      '@rhngui/web/ngui-image.js': path.resolve(__dirname, '../../../libs/next_gen_ui_web/elements/ngui-image.ts'),
    },
  },
  optimizeDeps: {
    // Exclude web components from pre-bundling to preserve import map resolution
    exclude: ['@rhngui/web'],
  },
  server: {
    fs: {
      // Allow serving files from the project root
      allow: ['../../..'],
    },
  },
});
