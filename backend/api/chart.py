from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.api.deps import get_current_user
from backend.database.database import get_db
from backend.database.models import User, Profile
from backend.astrology.engine import engine
from datetime import datetime

router = APIRouter(prefix="/chart", tags=["Chart"])

@router.get("/natal")
async def get_natal_chart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns the deterministic natal chart data (Rasi) calculated via Swiss Ephemeris.
    """
    stmt = select(Profile).where(Profile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalars().first()
    
    if not profile:
        raise HTTPException(status_code=400, detail="Профиль не заполнен. Пожалуйста, укажите дату рождения в Настройках.")

    import zoneinfo
    
    # The database stores naive datetime representing local time
    local_dt = profile.birth_date
    user_tz = zoneinfo.ZoneInfo(profile.timezone)
    
    # Localize the naive datetime
    localized_dt = local_dt.replace(tzinfo=user_tz)
    
    # Convert to UTC
    utc_dt = localized_dt.astimezone(zoneinfo.ZoneInfo("UTC"))
    
    # Swiss Ephemeris engine assumes UTC datetime, but it uses dt.year/month/day/hour/minute/second directly.
    # Therefore, we pass the utc_dt which has the correct UTC values.
    
    lon = profile.lon
    lat = profile.lat

    results = engine.calculate_natal_chart(utc_dt, lon, lat)
    
    # We will format it for frontend consumption.
    # Map signs: 1 Rasi (Zodiac sign) = 30 degrees
    # 0 = Aries, 1 = Taurus, ...
    signs = [
        "Овен (Aries)", "Телец (Taurus)", "Близнецы (Gemini)", 
        "Рак (Cancer)", "Лев (Leo)", "Дева (Virgo)", 
        "Весы (Libra)", "Скорпион (Scorpio)", "Стрелец (Sagittarius)", 
        "Козерог (Capricorn)", "Водолей (Aquarius)", "Рыбы (Pisces)"
    ]

    formatted_positions = {}
    for planet, data in results["positions"].items():
        longitude = data["longitude"]
        sign_index = int(longitude / 30)
        degree_in_sign = longitude % 30
        
        formatted_positions[planet] = {
            "sign": signs[sign_index],
            "degree": round(degree_in_sign, 2),
            "nakshatra_index": data["nakshatra_index"],
            "pada": data["pada"],
            "is_retrograde": data.get("speed", 1) < 0
        }
        
    return {
        "ayanamsa": results["ayanamsa"],
        "planets": formatted_positions
    }
