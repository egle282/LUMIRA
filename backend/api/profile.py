from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator
import zoneinfo

from backend.api.deps import get_current_user
from backend.database.database import get_db
from backend.database.models import User, Profile

router = APIRouter(prefix="/profile", tags=["Profile"])


class ProfileCreateUpdate(BaseModel):
    name: str
    birth_date: str  # YYYY-MM-DD format
    birth_time_str: str # HH:MM format
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    timezone: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value or len(value) > 120:
            raise ValueError("Name must contain between 1 and 120 characters")
        return value

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value: str) -> str:
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("Birth date must use YYYY-MM-DD format") from exc
        if parsed.isoformat() != value:
            raise ValueError("Birth date must use YYYY-MM-DD format")
        if parsed > date.today():
            raise ValueError("Birth date cannot be in the future")
        return value

    @field_validator("birth_time_str")
    @classmethod
    def validate_birth_time(cls, value: str) -> str:
        try:
            parsed = datetime.strptime(value, "%H:%M")
        except ValueError as exc:
            raise ValueError("Birth time must use HH:MM format") from exc
        if parsed.strftime("%H:%M") != value:
            raise ValueError("Birth time must use HH:MM format")
        return value

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        if v not in zoneinfo.available_timezones():
            raise ValueError(f"Invalid timezone: {v}")
        return v

class ProfileResponse(BaseModel):
    id: str
    name: str
    birth_date: datetime
    birth_time_str: str
    lat: float
    lon: float
    timezone: str

@router.get("/me", response_model=Optional[ProfileResponse])
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Profile).where(Profile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalars().first()
    if profile:
        return profile
    return None

@router.post("/me", response_model=ProfileResponse)
async def update_my_profile(
    data: ProfileCreateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        bdate = datetime.strptime(data.birth_date, "%Y-%m-%d")
        # Combine date and time if needed, but we keep time string separate in the DB model
        btime = datetime.strptime(data.birth_time_str, "%H:%M").time()
        combined_datetime = datetime.combine(bdate, btime)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date/time format. Use YYYY-MM-DD and HH:MM.")

    stmt = select(Profile).where(Profile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalars().first()

    if profile:
        profile.name = data.name
        profile.birth_date = combined_datetime
        profile.birth_time_str = data.birth_time_str
        profile.lat = data.lat
        profile.lon = data.lon
        profile.timezone = data.timezone
    else:
        profile = Profile(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            name=data.name,
            birth_date=combined_datetime,
            birth_time_str=data.birth_time_str,
            lat=data.lat,
            lon=data.lon,
            timezone=data.timezone
        )
        db.add(profile)

    await db.commit()
    return profile
