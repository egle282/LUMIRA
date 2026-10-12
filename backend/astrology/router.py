from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.database.database import get_db
from backend.database.models import Profile, User
from backend.astrology.life_areas import LifeAreasState, evaluate_life_areas

router = APIRouter(prefix="/astrology", tags=["Astrology"])


@router.get("/life-areas", response_model=LifeAreasState)
async def get_life_areas(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return a life-area reading only when backed by the user's own profile."""
    result = await db.execute(
        select(Profile)
        .where(Profile.user_id == current_user.id)
        .order_by(Profile.created_at.asc())
        .limit(1)
    )
    profile = result.scalars().first()
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Birth profile not found. Create a profile before requesting a reading.",
        )

    birth_data = {
        "birth_date": profile.birth_date.date().isoformat()
        if isinstance(profile.birth_date, datetime)
        else profile.birth_date.isoformat(),
        "birth_time": profile.birth_time_str,
        "lat": profile.lat,
        "lon": profile.lon,
        "timezone": profile.timezone,
    }
    try:
        return evaluate_life_areas(
            birth_data=birth_data,
            current_time=datetime.now(timezone.utc),
        )
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=501,
            detail="Personalized life-area calculations are not available yet; no sample data was substituted.",
        ) from exc
