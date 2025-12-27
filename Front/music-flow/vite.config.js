import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import mkcert from 'vite-plugin-mkcert';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd());
  const DOMAIN = env.VITE_DOMAIN;

  return {
    plugins: [vue(), mkcert()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      port: 443,
      https: true,
      strictPort: true,
      hmr: { protocol: 'wss' },
      allowedHosts: [DOMAIN],
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          rewrite: path => path.replace(/^\/api/, ''),
        },
        '/ws': {
          target: 'ws://localhost:8000',
          ws: true,
          changeOrigin: true,
          rewrite: path => path.replace(/^\/ws/, ''),
        },
      },
      cors: true,
      headers: {
        'Access-Control-Allow-Origin': '*',
      },
    },
  };
});
