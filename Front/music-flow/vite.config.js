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
      port: 3000,
      host: "127.0.0.1",
      https: false,
      strictPort: true,
      hmr: { protocol: 'wss' },
      allowedHosts: [DOMAIN, '.serveousercontent.com'],
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
