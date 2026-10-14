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
    
    # Calculate houses and angles using Swiss Ephemeris in Lahiri sidereal mode
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    )
    # Using Placidus ('P') sidereal houses
    raw_cusps, angles = swe.houses_ex(jd, lat, lon, b"P", swe.FLG_SIDEREAL)

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
    raw_longitudes = {}
    for planet, data in results["positions"].items():
        longitude = data["longitude"]
        sign_index = int(longitude / 30) % 12
        degree_in_sign = longitude % 30
        raw_longitudes[planet] = longitude
        
        formatted_positions[planet] = {
            "sign": signs[sign_index],
            "sign_index": sign_index,
            "degree": round(degree_in_sign, 2),
            "abs_degree": round(longitude, 2),
            "nakshatra_index": data["nakshatra_index"],
            "pada": data["pada"],
            "is_retrograde": data.get("speed", 1) < 0
        }

    # Format Ascendant and Midheaven (MC)
    asc_lon = angles[0] % 360
    mc_lon = angles[1] % 360
    asc_sign_index = int(asc_lon / 30) % 12
    mc_sign_index = int(mc_lon / 30) % 12

    ascendant_data = {
        "longitude": round(asc_lon, 2),
        "sign": signs[asc_sign_index],
        "sign_index": asc_sign_index,
        "degree": round(asc_lon % 30, 2),
    }

    mc_data = {
        "longitude": round(mc_lon, 2),
        "sign": signs[mc_sign_index],
        "sign_index": mc_sign_index,
        "degree": round(mc_lon % 30, 2),
    }

    # Format 12 Houses
    houses_data = []
    for i, cusp in enumerate(raw_cusps):
        c_lon = cusp % 360
        s_idx = int(c_lon / 30) % 12
        houses_data.append({
            "house": i + 1,
            "longitude": round(c_lon, 2),
            "sign": signs[s_idx],
            "sign_index": s_idx,
            "degree": round(c_lon % 30, 2),
        })

    # Major aspects calculation
    # Conjunction: 0 deg (orb 8)
    # Sextile: 60 deg (orb 6)
    # Square: 90 deg (orb 7)
    # Trine: 120 deg (orb 8)
    # Opposition: 180 deg (orb 8)
    aspect_defs = [
        {"type": "Conjunction", "angle": 0, "orb": 8.0, "nature": "neutral", "symbol": "☌", "name_ru": "Соединение"},
        {"type": "Sextile", "angle": 60, "orb": 6.0, "nature": "harmonious", "symbol": "⚹", "name_ru": "Секстиль"},
        {"type": "Square", "angle": 90, "orb": 7.0, "nature": "challenging", "symbol": "□", "name_ru": "Квадрат"},
        {"type": "Trine", "angle": 120, "orb": 8.0, "nature": "harmonious", "symbol": "△", "name_ru": "Трин"},
        {"type": "Opposition", "angle": 180, "orb": 8.0, "nature": "challenging", "symbol": "☍", "name_ru": "Оппозиция"},
    ]

    aspects_list = []
    planet_keys = list(raw_longitudes.keys())
    for i in range(len(planet_keys)):
        for j in range(i + 1, len(planet_keys)):
            p1 = planet_keys[i]
            p2 = planet_keys[j]
            lon1 = raw_longitudes[p1]
            lon2 = raw_longitudes[p2]
            
            diff = abs(lon1 - lon2) % 360
            if diff > 180:
                diff = 360 - diff
                
            for asp in aspect_defs:
                orb_diff = abs(diff - asp["angle"])
                if orb_diff <= asp["orb"]:
                    aspects_list.append({
                        "planet1": p1,
                        "planet2": p2,
                        "aspect": asp["type"],
                        "name_ru": asp["name_ru"],
                        "symbol": asp["symbol"],
                        "angle": asp["angle"],
                        "orb": round(orb_diff, 2),
                        "nature": asp["nature"],
                    })

    return {
        "ayanamsa": results["ayanamsa"],
        "planets": formatted_positions,
        "ascendant": ascendant_data,
        "mc": mc_data,
        "houses": houses_data,
        "aspects": aspects_list,
        "profile": {
            "name": profile.name,
            "birth_date": profile.birth_date.strftime("%Y-%m-%d"),
            "birth_time": profile.birth_time_str or "12:00",
            "lat": profile.lat,
            "lon": profile.lon,
            "timezone": profile.timezone,
        }
    }

