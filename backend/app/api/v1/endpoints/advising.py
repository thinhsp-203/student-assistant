from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_advising_service
from app.schemas.advising import AdvisingResponse
from app.services.advising_service import AdvisingService

router = APIRouter()


@router.get("/{student_id}/recommendations", response_model=AdvisingResponse)
async def recommendations(
    student_id: str,
    target_semester: int | None = Query(default=None, ge=1, le=20),
    advising_service: AdvisingService = Depends(get_advising_service),
):
    try:
        result = await advising_service.recommend(student_id, target_semester)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return result
