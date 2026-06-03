import { dirname, resolve } from "path";
import { fileURLToPath } from "url";
import { defineConfig } from "vite";

const __dirname = dirname(fileURLToPath(import.meta.url));

function privacyRouteMiddleware(req, _res, next) {
  const url = req.url?.split("?")[0];
  if (url === "/privacy" || url === "/privacy/") {
    req.url = "/privacy/index.html";
  }
  next();
}

function mpaDevRoutes() {
  return {
    name: "mpa-dev-routes",
    configureServer(server) {
      server.middlewares.use(privacyRouteMiddleware);
    },
    configurePreviewServer(server) {
      server.middlewares.use(privacyRouteMiddleware);
    },
  };
}

export default defineConfig({
  plugins: [mpaDevRoutes()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, "index.html"),
        privacy: resolve(__dirname, "privacy/index.html"),
      },
    },
  },
});
