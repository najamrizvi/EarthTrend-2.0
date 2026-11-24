from fastapi import APIRouter, HTTPException, Query

from app.services.gpm_catalog import get_gpm_dataset_metadata
from app.services.gpm_regional import get_regional_gpm_data

router = APIRouter()


@router.get("/gpm/catalog", tags=["GPM IMERG"])
async def gpm_catalog():
    """Return metadata for the processed GPM IMERG dataset."""

    try:
        return get_gpm_dataset_metadata()

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to read GPM dataset metadata."
        ) from exc


@router.get("/gpm/regional", tags=["GPM IMERG"])
async def gpm_regional(
    variable: str = Query("precipitation"),
    min_latitude: float = Query(..., ge=-90, le=90),
    max_latitude: float = Query(..., ge=-90, le=90),
    min_longitude: float = Query(..., ge=-180, le=180),
    max_longitude: float = Query(..., ge=-180, le=180),
    time_index: int = Query(0, ge=0, le=1),
):
    """Return a bounded geographic subset of a GPM variable."""

    try:
        return get_regional_gpm_data(
            variable=variable,
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude,
            time_index=time_index,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve regional GPM data."
        ) from exc
