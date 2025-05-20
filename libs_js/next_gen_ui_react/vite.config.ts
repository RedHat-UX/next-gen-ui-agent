
import react from "@vitejs/plugin-react";
import dts from "vite-plugin-dts";
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react(), dts()],
  build: {
    lib: {
      entry: "./src/index.tsx", // Ensure this exists
      name: "DynamicUI",
      formats: ["es", "cjs"],
      fileName: (format) => `index.${format}.js`,
    },
    rollupOptions: {
      external: ["react", "react-dom"],
      output: {
        exports: "named",
        globals: {
          react: "React",
          "react-dom": "ReactDOM",
        },
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
});
