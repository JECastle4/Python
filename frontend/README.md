# Astronomy Animation Frontend

Vue 3 + TypeScript + Three.js frontend for astronomy visualizations.

## Prerequisites

- Node.js 18+ and npm
- FastAPI backend running on `http://localhost:8000`

## Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Development

The dev server runs on `http://localhost:5173` by default.

API calls are proxied to `http://localhost:8000` during development (configured in `vite.config.ts`).

## Project Structure

```
src/
├── components/       # Vue components
├── composables/      # Vue composables for state management
├── services/         # API client and configuration
├── three/            # Three.js scene and objects
├── types/            # TypeScript type definitions
└── main.ts           # Application entry point
```

## Configuration

Environment variables:
- `.env.local` - Local development (git-ignored)
- `.env.production` - Production deployment

Set `VITE_API_BASE_URL` to your API endpoint.
