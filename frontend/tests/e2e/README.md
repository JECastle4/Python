# E2E Tests

This directory contains end-to-end tests for the astronomy animation frontend.

## Overview

E2E tests use Playwright to test the full integration of:
- Frontend UI components
- API integration with FastAPI backend
- Three.js rendering (3D scene and Sky View)
- User workflows

## Running Tests

```bash
# Run all E2E tests (headless)
npm run test:e2e

# Run with UI mode (interactive)
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Debug tests
npm run test:e2e:debug

# Update golden screenshots
npm run test:e2e:update-snapshots
```

## Prerequisites

Before running E2E tests, ensure:
1. Backend is running: `uvicorn api.main:app --reload` (from project root)
2. Backend is accessible at `http://localhost:8000`
3. Vite dev server will be started automatically by Playwright

## Test Structure

- `astronomy-scene.spec.ts` - Main scene rendering and interaction tests
- `screenshots/` - Golden images for visual regression testing (auto-generated)

## Golden Images

Visual regression tests compare current screenshots against baseline "golden" images.

### First-time Setup
1. Run `npm run test:e2e:update-snapshots` to generate initial golden images
2. Manually verify screenshots look correct
3. Commit golden images to git

### Updating Golden Images
When intentional visual changes are made:
1. Run `npm run test:e2e:update-snapshots`
2. Review the diff carefully
3. Commit updated golden images

## Tolerance

Screenshots allow 0.2% pixel difference to account for minor rendering variations across machines.
