
from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.gpm import router as gpm_router
from app.api.historical import router as historical_router


app = FastAPI(
    title="EarthTrend 2.0 API",
    description=(
        "Scientific Earth observation and environmental "
        "trend investigation platform."
    ),
    version="2.0.0",
)

app.include_router(health_router, prefix="/api")
app.include_router(gpm_router, prefix="/api")
app.include_router(historical_router, prefix="/api")


@app.get("/", tags=["System"])
async def root():
    return {
        "application": "EarthTrend 2.0",
        "version": "2.0.0",
        "message": "Welcome to the EarthTrend API.",
    }
