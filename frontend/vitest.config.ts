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
      // Coverage thresholds explanation:
      // - Low thresholds (45-65%) account for scene.ts (0% - requires WebGL/GPU context)
      // - Business logic (API client, composables, Three.js objects) has 100% coverage
      // - Branch coverage (80%) is the primary quality gate
      // - E2E tests (Playwright) will cover scene rendering and integration testing
      // TODO: Gradually increase thresholds as E2E tests are added:
      //   - Target: lines 70%, functions 80%, statements 70% after E2E implementation
      //   - Consider per-file coverage requirements for critical business logic
      lines: 45,        // Current: 48.14%
      functions: 65,    // Current: 66.66%
      branches: 80,     // Current: 89.47% - PRIMARY GATE
      statements: 45,   // Current: 48.14%
    },
  },
})
