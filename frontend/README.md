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

### Environment Variables

The application uses environment variables for API configuration:

**Development (.env.local)**
Create a `.env.local` file for local development (git-ignored):
```env
VITE_API_BASE_URL=http://localhost:8000
```

**Production (.env.production)**
For production deployment, use the provided template:
```bash
# Copy the example file
cp .env.production.example .env.production

# Edit with your production API URL
# Example: VITE_API_BASE_URL=https://api.yourdomain.com
```

The `.env.production.example` file contains detailed deployment instructions.

**Default Behavior:**
- If `VITE_API_BASE_URL` is not set, defaults to `http://localhost:8000`
- Production builds will warn if using http instead of https
- Production builds will warn if environment variable is missing
