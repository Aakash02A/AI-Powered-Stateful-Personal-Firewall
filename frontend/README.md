# AI-Powered Stateful Personal Firewall - Frontend

This is the frontend component for the AI-Powered Stateful Personal Firewall, built with React, TypeScript, and Vite.

## Architecture

The frontend is a single-page application (SPA) that provides a real-time dashboard and management interface for the firewall.

### Core Technologies
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + Lucide Icons
- **State Management**: Zustand (for UI state) + React Query (for server state)
- **Real-time Data**: WebSockets (using a custom `useWebSocket` hook)
- **Data Visualization**: Recharts
- **Virtualization**: `@tanstack/react-virtual` for high-performance data tables

### Key Components
- **Dashboard**: Real-time overview of active connections, total packets, and threat alerts. Integrates both REST APIs and live WebSocket streams.
- **Connections / Analytics / Alerts**: Detailed views for specific data types, utilizing virtualized tables for rendering thousands of rows efficiently.
- **ConnectionStatus**: Real-time monitor showing the health of the REST API and WebSocket stream.

## Setup and Development

### Requirements
- Node.js >= 18
- npm

### Installation
```bash
npm install
```

### Running Locally
To start the development server:
```bash
npm run dev
```

> **Note**: The frontend relies on the FastAPI backend running on port 8000. Ensure the backend is running before launching the frontend.

## Testing

The frontend has a comprehensive testing suite comprising Unit, Integration, and End-to-End (E2E) tests.

### Unit & Integration Tests (Vitest + React Testing Library)
Tests cover all React components, custom hooks, and mock network interactions using MSW (Mock Service Worker).

```bash
# Run tests
npm run test

# Run tests with coverage report
npm run test -- --coverage
```

Current unit test coverage targets >85%.

### End-to-End Tests (Playwright)
Playwright E2E tests run against the built application to verify the dashboard and navigation flows in a real browser engine (Chromium).

```bash
# Install Playwright browsers (first time only)
npx playwright install chromium

# Run E2E tests
npx playwright test

# View HTML report
npx playwright show-report
```

## Available Scripts

- `npm run dev`: Starts the development server.
- `npm run build`: Compiles TypeScript and builds for production.
- `npm run preview`: Locally previews the production build.
- `npm run lint`: Runs Oxlint for ultra-fast linting.
- `npm run test`: Runs unit/integration tests using Vitest.
