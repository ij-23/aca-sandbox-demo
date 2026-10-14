import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({ plugins: [react()], build: { outDir: '../backend/static', emptyOutDir: true, rollupOptions: { output: { manualChunks: { identity: ['@azure/msal-browser'] } } } }, server: { proxy: { '/api': 'http://127.0.0.1:8000' } } });
