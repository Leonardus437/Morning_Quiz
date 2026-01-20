import { sveltekit } from '@sveltejs/kit/vite';

export default {
  plugins: [sveltekit()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    hmr: false,
    watch: {
      usePolling: false
    },
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined,
<<<<<<< HEAD
        entryFileNames: `[name].${Date.now()}.js`,
        chunkFileNames: `[name].${Date.now()}.js`,
        assetFileNames: `[name].${Date.now()}.[ext]`
      }
    },
    cssCodeSplit: false,
    minify: false
=======
        entryFileNames: '[name].[hash].js',
        chunkFileNames: '[name].[hash].js',
        assetFileNames: '[name].[hash].[ext]'
      }
    },
    cssCodeSplit: false
>>>>>>> a6f256911bd91da0b979b46a8d9484a08d4142a9
  },
  optimizeDeps: {
    exclude: ['@sveltejs/kit']
  }
};