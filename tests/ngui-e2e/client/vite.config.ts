import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@ngui/web/ngui-card.js': path.resolve(__dirname, 'public/ngui-elements/ngui-card.js'),
      '@ngui/web/ngui-image.js': path.resolve(__dirname, 'public/ngui-elements/ngui-image.js'),
    },
  },
});
