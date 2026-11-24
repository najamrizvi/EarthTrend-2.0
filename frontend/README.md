# EarthTrend 2.0 — Frontend

The React-based web interface for EarthTrend 2.0, a scientific Earth-observation analytics platform built around NASA GPM IMERG precipitation data.

## Features

- **Overview:** Regional precipitation metrics and observation summaries.
- **Geospatial Analysis:** Explore the selected geographic region.
- **Time Series:** Examine historical precipitation observations.
- **Forecasting:** View short-term baseline forecasts and evaluation metrics.
- **AI Insights:** Explore statistical insights, evidence and analytical limitations.

## Technology

- React
- Vite
- React Leaflet and Leaflet
- react-globe.gl

## Requirements

- Node.js and npm
- The EarthTrend 2.0 backend running locally

## Run locally

From the `frontend` directory:

```bash
npm install
npm run dev
```

Vite starts the frontend development server and proxies `/api` requests to the backend at `http://127.0.0.1:8000`.

Start the backend separately using the instructions in the root project README.

## Production note

The Vite API proxy is for local development only. Production deployment requires the frontend and backend API connection to be configured for the deployment environment.