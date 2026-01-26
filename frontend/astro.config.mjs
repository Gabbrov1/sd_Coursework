// @ts-check
import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import node from "@astrojs/node";

import cloudflare from "@astrojs/cloudflare";

export default defineConfig({
  integrations: [react()],

  
  output: "server",

  adapter: cloudflare()
});