from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timezone
from backend.api.deps import get_current_user
from backend.database.models import User
from backend.briefing.schemas import DailyBriefing
from backend.briefing.service import BriefingService

router = APIRouter(prefix="/briefing", tags=["Briefing"])

@router.get("/daily", response_model=DailyBriefing)
async def get_daily_briefing(
    target_date: str = Query(None, description="Target date in YYYY-MM-DD format. Defaults to today."),
    current_user: User = Depends(get_current_user)
):
    """
    Generate or retrieve the personalized daily AI briefing for the user.
    """
    if target_date:
        try:
            date_obj = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    else:
        date_obj = datetime.now(timezone.utc)
        
    service = BriefingService(user_id=current_user.id)
    return await service.generate_daily_briefing(target_date=date_obj)
