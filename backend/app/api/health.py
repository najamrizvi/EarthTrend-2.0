from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "application": "EarthTrend 2.0",
        "message": "EarthTrend API is operational."
    }
