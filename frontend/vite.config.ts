import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  base: '/static/',
  plugins: [react()],
  build: {
    manifest: true,
    outDir: resolve('./dist'),
    rollupOptions: {
      input: {
        main: resolve('./src/main.tsx'),
      },
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    cors: true,
  },
});
