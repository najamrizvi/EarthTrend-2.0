
from fastapi import APIRouter, HTTPException

from app.services.historical import get_historical_gpm_data
from app.services.historical_expanded import (
    get_historical_gpm_expanded_data,
)
from app.services.forecasting import get_gpm_forecast_data


router = APIRouter()


@router.get(
    "/gpm/historical",
    tags=["GPM IMERG Historical"],
)
async def gpm_historical():
    """Return the validated historical precipitation pilot."""

    try:
        return get_historical_gpm_data()

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve historical GPM data.",
        ) from exc


@router.get(
    "/gpm/historical-expanded",
    tags=["GPM IMERG Historical"],
)
async def gpm_historical_expanded():
    """Return the validated 30-day historical precipitation dataset."""

    try:
        return get_historical_gpm_expanded_data()

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve expanded historical GPM data.",
        ) from exc


@router.get(
    "/gpm/forecast",
    tags=["GPM IMERG Forecasting"],
)
async def gpm_forecast():
    """Return the evaluated six-hour precipitation baseline forecast."""

    try:
        return get_gpm_forecast_data()

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to generate the GPM precipitation forecast.",
        ) from exc
