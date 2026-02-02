import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    globals: true,
    environment: 'happy-dom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/**/*.d.ts',
        'src/main.ts',
        'src/vite-env.d.ts',
        '**/*.config.ts',
        'dist/',
      ],
      all: true,
      lines: 45,        // Current: 48.14%
      functions: 65,    // Current: 66.66%
      branches: 80,     // Current: 89.47% - PRIMARY GATE
      statements: 45,   // Current: 48.14%
    },
  },
})
