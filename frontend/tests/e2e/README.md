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

# Update golden screenshots (all browsers except Firefox on Linux — see note below)
npm run test:e2e:update-snapshots

# Update Firefox-Linux golden screenshots (Linux only, requires xvfb-run and Mesa)
LIBGL_ALWAYS_SOFTWARE=1 MESA_GL_VERSION_OVERRIDE=4.5 npm run test:e2e:update-snapshots:firefox-linux
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
Snapshots are named `<test>-<browser>-<platform>.png` (e.g. `3d-view-first-frame-firefox-linux.png`).

### First-time Setup
1. Run `npm run test:e2e:update-snapshots` to generate initial golden images
2. Manually verify screenshots look correct
3. Commit golden images to git

### Updating Golden Images
When intentional visual changes are made:
1. Run `npm run test:e2e:update-snapshots`
2. Review the diff carefully
3. Commit updated golden images

### Firefox on Linux

Firefox headless on Linux cannot initialise WebGL without a real X11 display — it bypasses
the Mesa/GLX stack entirely, producing a blank canvas. The workaround is to run Firefox in
headed mode behind an Xvfb virtual display with Mesa software rendering (`LIBGL_ALWAYS_SOFTWARE`).

**Consequences for snapshot management:**

- `npm run test:e2e:update-snapshots` run on Linux **without** Xvfb will regenerate
  `*firefox-linux*` snapshots as blank white images. Do not commit those.
- To regenerate Firefox-Linux snapshots on Linux, use the dedicated script instead:
  ```bash
  LIBGL_ALWAYS_SOFTWARE=1 MESA_GL_VERSION_OVERRIDE=4.5 npm run test:e2e:update-snapshots:firefox-linux
  ```
  This requires `xvfb-run` and Mesa (`mesa-utils` / `libgl1-mesa-dri`) to be installed.
- On **Windows and macOS**, Firefox headless renders WebGL normally, so
  `npm run test:e2e:update-snapshots` is fine for `*firefox-win32*` and `*firefox-darwin*`
  snapshots but will not produce a `*firefox-linux*` snapshot at all.
- The CI `frontend-e2e` job applies the Xvfb workaround automatically and is the canonical
  source for `*firefox-linux*` baselines. After a CI run passes, download the
  `playwright-test-results` artifact and commit any updated `*firefox-linux*.png` files.

## Tolerance

Screenshots allow 0.2% pixel difference to account for minor rendering variations across machines.
