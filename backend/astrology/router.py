from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime
from backend.api.deps import get_current_user
from backend.database.models import User
from backend.astrology.life_areas import LifeAreasState, evaluate_life_areas

router = APIRouter(prefix="/astrology", tags=["Astrology"])

@router.get("/life-areas", response_model=LifeAreasState)
async def get_life_areas(current_user: User = Depends(get_current_user)):
    """
    Get the astrological state of various life areas for the current user.
    Uses the user's birth profile to generate deterministic factors.
    """
    # In a real scenario, fetch the primary profile of the user from the database
    # using current_user.id. Here we use a mock birth_data dict.
    mock_birth_data = {
        "birth_date": "1990-01-01",
        "birth_time": "12:00",
        "lat": 55.7558,
        "lon": 37.6173
    }
    
    current_time = datetime.utcnow()
    state = evaluate_life_areas(birth_data=mock_birth_data, current_time=current_time)
    
    return state
