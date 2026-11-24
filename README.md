# EarthTrend 2.0

### Earth Observation Intelligence | Geospatial Analytics | Precipitation Forecasting

EarthTrend 2.0 is a browser-based Earth observation and precipitation analytics platform built around NASA's Global Precipitation Measurement (GPM) Integrated Multi-satellitE Retrievals for GPM (IMERG) Final Half-Hourly Version 07B dataset.

The platform transforms satellite-derived precipitation observations into an interactive scientific workspace for exploring regional precipitation, examining historical time series, evaluating statistical forecasts, and understanding data characteristics through evidence-based analytics.

---

## 1. Project Overview

EarthTrend 2.0 brings together geospatial visualization, historical precipitation analysis, statistical forecasting, and scientific data interpretation in one web application.

The project uses a 30-day historical GPM IMERG dataset covering January 1–30, 2020, for a small regional area around the geographic origin (0°, 0°).

The application provides five integrated workspace sections:

- Overview
- Geospatial Analysis
- Time Series
- Forecasting
- AI Insights

The goal is to make satellite precipitation observations easier to explore and interpret while maintaining transparency about data coverage, methodology, and limitations.

## 2. Key Features

### Overview

A central workspace providing:
- Earth visualization and application navigation.
- Regional precipitation snapshot.
- Observation metadata and spatial coverage.
- Selected-timestep precipitation statistics.
- Scientific information about the underlying data.

### Geospatial Analysis

Provides regional spatial exploration through geographic visualization and precipitation observations.

### Time Series Analysis

Provides historical precipitation exploration using half-hourly observations, enabling users to examine temporal variations in the regional dataset.

### Forecasting

Provides a six-hour precipitation forecast using statistically evaluated baseline methods.

Implemented forecasting capabilities include:
- Persistence baseline.
- Previous-day seasonal baseline.
- Rolling-origin holdout evaluation.
- MAE, RMSE, and bias reporting.
- Automatic selection of the baseline with lower holdout MAE.
- Twelve half-hourly forecast steps.

The current evaluation selected the persistence baseline.

### AI Insights

Provides evidence-based descriptive analytics, including:
- Regional precipitation summary statistics.
- Historical precipitation visualization.
- Upper-tail precipitation observations.
- Grid-cell comparisons.
- Daily precipitation accumulation summaries.
- Scientific limitations and interpretation guidance.

The current implementation uses transparent statistical calculations. It does not claim to use an external generative AI interpretation engine.

## 3. Data Source

**Primary source:** NASA Global Precipitation Measurement (GPM) IMERG Final Half-Hourly Version 07B.

- Product: GPM IMERG Final Half-Hourly
- Collection: `GPM_3IMERGHH`
- Version: V07B
- Temporal resolution: 30 minutes
- Spatial resolution: 0.1 degree
- Primary variable: Precipitation
- Measurement units: mm/hr
- Timestamp standard: UTC

Official data information:

https://gpm.nasa.gov/data/imerg

### Study Region

The current historical analysis uses a fixed regional area around:

- Center latitude: 0°
- Center longitude: 0°
- Latitude bounds: approximately -0.06° to +0.06°
- Longitude bounds: approximately -0.06° to +0.06°

The selected subset contains a 2 × 2 grid, representing four spatial grid cells.

**Important:** EarthTrend 2.0 currently analyzes a regional subset of the NASA GPM IMERG product. It does not provide a complete global precipitation analysis.

## 4. Historical Dataset

The expanded historical dataset covers:

**January 1, 2020 – January 30, 2020**

| Dataset characteristic | Value |
|---|---:|
| Historical duration | 30 days |
| Temporal observations | 1,440 |
| Temporal interval | 30 minutes |
| Latitude cells | 2 |
| Longitude cells | 2 |
| Total grid-cell observations | 5,760 |
| Missing observations | 0 |
| Measurement variable | Precipitation |
| Units | mm/hr |

The validated historical dataset is stored locally in Zarr format:

`data/processed/gpm_imerg/historical_20200101_20200130.zarr`

Raw source files and generated scientific data artifacts are maintained separately from the application source code.

## 5. Forecasting Methodology

EarthTrend 2.0 implements a statistical baseline forecasting workflow using the regional spatial-mean precipitation time series.

Two baseline approaches are evaluated:

**Persistence baseline**

Uses the most recently observed precipitation value as the forecast value.

**Previous-day seasonal baseline**

Uses the corresponding precipitation observation from the previous day.

### Evaluation Configuration

- Evaluation period: Final seven days of the historical dataset.
- Evaluation observations: 336.
- Forecast horizon: Six hours.
- Forecast frequency: 30 minutes.
- Forecast steps: 12.
- Evaluation approach: Rolling-origin six-hour blocks.

### Observed Evaluation Results

| Metric | Persistence | Previous-day |
|---|---:|---:|
| MAE | 0.00900 | 0.01111 |
| RMSE | 0.04539 | 0.05797 |
| Bias | -0.00155 | 0.00033 |
| Evaluation observations | 336 | 336 |

The persistence baseline was selected because it achieved lower MAE and RMSE on the evaluated holdout observations.

The current six-hour forecast is generated from the selected baseline.

**Forecasting limitations:**
- The forecast is based on historical observations, not a live satellite data stream.
- The evaluation covers one historical regional dataset.
- No calibrated prediction intervals or uncertainty estimates are currently provided.
- Baseline performance should not be interpreted as proof of general forecasting accuracy under different climatic or geographical conditions.

## 6. Technology Stack

### Frontend

- React 19
- Vite 8
- JavaScript
- Leaflet
- React Leaflet
- React Globe GL
- CSS

### Backend

- Python
- FastAPI
- Uvicorn
- NumPy
- Xarray
- Zarr
- h5py

### Scientific Data Processing

- NASA GPM IMERG V07B
- NetCDF/HDF5-compatible scientific data workflows
- Zarr-based historical data storage
- Regional spatial aggregation
- Time-series analysis
- Statistical baseline forecasting

## 7. Application Architecture

EarthTrend 2.0 follows a frontend/backend architecture.

**Frontend**
- Provides the interactive browser-based workspace.
- Displays geospatial visualizations and analytical results.
- Communicates with the backend API.

**Backend**
- Exposes REST API endpoints using FastAPI.
- Provides access to GPM metadata and regional observations.
- Serves historical precipitation data.
- Generates statistical forecast results.

**Data layer**
- Stores processed GPM IMERG observations.
- Maintains the expanded historical dataset in Zarr format.
- Supports scientific analysis through Xarray and NumPy.

## 8. Project Structure

```text
EarthTrend-2.0/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── inspect_gpm.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── data/
│   └── processed/
│       └── gpm_imerg/
│
├── docs/
│
├── outputs/
│
└── README.md
```

Generated datasets and local virtual environments are maintained separately from the source-code repository.

## 9. Installation and Local Setup

### Prerequisites

- Python environment compatible with the backend dependencies.
- Node.js version compatible with Vite 8.
- npm.
- Git.

### Step 1: Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd EarthTrend-2.0
```

Replace the placeholder with the actual repository URL after publication.

### Step 2: Configure the backend

Open a terminal in the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

The backend will normally be available at:

`http://127.0.0.1:8000`

### Step 3: Configure the frontend

Open another terminal:

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local frontend URL displayed by Vite in the terminal.

### Step 4: Access API documentation

FastAPI interactive documentation:

`http://127.0.0.1:8000/docs`

**Data requirement:** The application depends on the processed GPM datasets at their expected local paths. These datasets must be obtained or generated using the project's documented data-processing workflow before running the corresponding data-dependent endpoints.

## 10. Backend API Endpoints

The current backend exposes the following endpoints:

| Endpoint | Purpose |
|---|---|
| `/api/health` | Backend health check |
| `/api/gpm/catalog` | GPM dataset metadata |
| `/api/gpm/regional` | Regional precipitation observations |
| `/api/gpm/historical` | Original historical pilot |
| `/api/gpm/historical-expanded` | Expanded 30-day historical dataset |
| `/api/gpm/forecast` | Six-hour statistical forecast |

Interactive API documentation is available through FastAPI Swagger UI at `/docs`.

## 11. Scientific Integrity and Limitations

EarthTrend 2.0 emphasizes transparent scientific interpretation.

Important considerations:

- The application uses a small regional subset of GPM IMERG observations.
- Historical data covers January 2020, not current real-time conditions.
- Precipitation measurements are expressed in mm/hr.
- Historical timestamps are interpreted using UTC.
- Forecasting uses statistical baselines rather than a trained machine-learning model.
- Forecast performance is evaluated on the available historical holdout period.
- Descriptive analytics do not establish causal relationships.
- The four-cell regional subset cannot represent all local precipitation variability.

Results should therefore be interpreted within the spatial, temporal, and methodological scope of the available observations.

## 12. Future Development

Potential future enhancements include:

- Additional historical observation periods.
- User-selectable geographical regions.
- Expanded spatial coverage.
- Additional precipitation forecasting models.
- Forecast uncertainty estimation.
- More comprehensive model validation.
- Enhanced scientific reporting.
- Production deployment and operational monitoring.

These are development opportunities, not claims about currently implemented functionality.

## 13. Acknowledgements

EarthTrend 2.0 uses precipitation observations from NASA's Global Precipitation Measurement mission and its IMERG data product.

We acknowledge NASA and the GPM science and data teams for providing satellite-derived precipitation observations for research and analysis.

---

**EarthTrend 2.0**

*Exploring Earth's precipitation through satellite observations, geospatial analytics, and evidence-driven intelligence.*