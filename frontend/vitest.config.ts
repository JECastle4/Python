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
    exclude: [
      'tests/e2e/**', // Exclude Playwright E2E tests from Vitest
      'node_modules/meshoptimizer/*.test.js', // Exclude meshoptimizer test files
    ],
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
        'src/three/scene.ts',     // Requires WebGL/GPU context, covered by E2E tests
        'src/services/config.ts', // Production validation code (environment-dependent)
        'src/components/AstronomyScene.vue', // Complex Three.js component - validation tested, rendering needs E2E
        'tests/e2e/**/*.ts', // Exclude Playwright E2E tests from Vitest
      ],
      all: true,
      // Per-file coverage thresholds enforce high coverage on business logic
      // scene.ts excluded from coverage (requires WebGL/GPU context)
      thresholds: {
        // Global thresholds
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
        
        // Per-file thresholds enforce high standards on business logic
        perFile: true,
        'src/services/api.ts': {
          lines: 95,
          functions: 100,
          branches: 80,      // Current: 80%, keep as-is
          statements: 95,
        },
        'src/services/config.ts': {
          lines: 50,         // Production validation not tested
          functions: 100,
          branches: 25,      // Production validation branches
          statements: 50,
        },
        'src/composables/**': {
          lines: 100,
          functions: 100,
          branches: 87,      // Current: 87.5%, allow slight margin
          statements: 100,
        },
        'src/three/objects/**': {
          lines: 100,
          functions: 100,
          branches: 90,
          statements: 100,
        },
      },
    },
  },
})
