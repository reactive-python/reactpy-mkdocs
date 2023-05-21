// vite.config.js
import { resolve } from "path";
import { defineConfig } from "vite";
import pkg from "./package.json";

export default defineConfig({
  build: {
    lib: {
      // Could also be a dictionary or array of multiple entry points
      entry: resolve(__dirname, "src/index.js"),
      name: pkg.name,
    },
    outDir: "../reactpy_mkdocs/static",
    emptyOutDir: true,
  },
  define: {
    "process.env": {},
  },
});
