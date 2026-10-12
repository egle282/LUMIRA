"""Basic Panchanga-based date screening. This is not a full classical muhurta election."""
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.astrology.engine import engine
from backend.database.database import get_db
from backend.database.models import Profile, User

router = APIRouter(prefix="/muhurta", tags=["Muhurta"])

# Traditional Panchanga screening heuristics. They are deliberately disclosed and
# should not be presented as a guarantee or as a substitute for a full election.
FAVORABLE_TITHIS = {2, 3, 5, 7, 10, 11, 13, 15, 17, 18, 20, 22, 25, 27, 29, 30}
FAVORABLE_NAKSHATRAS = {1, 4, 5, 7, 8, 13, 14, 17, 21, 22, 23, 26, 27}
ACTIVITY_TITHI_PENALTIES = {
    "business": {4, 9, 14, 19, 24, 29},
    "marriage": {4, 6, 9, 14, 19, 24, 29},
    "travel": {4, 9, 14, 19, 24, 29},
    "health": {4, 9, 14, 19, 24, 29},
}
TITHI_NAMES = ["Shukla Pratipada", "Shukla Dvitiya", "Shukla Tritiya", "Shukla Chaturthi", "Shukla Panchami", "Shukla Shashthi", "Shukla Saptami", "Shukla Ashtami", "Shukla Navami", "Shukla Dashami", "Shukla Ekadashi", "Shukla Dvadashi", "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima", "Krishna Pratipada", "Krishna Dvitiya", "Krishna Tritiya", "Krishna Chaturthi", "Krishna Panchami", "Krishna Shashthi", "Krishna Saptami", "Krishna Ashtami", "Krishna Navami", "Krishna Dashami", "Krishna Ekadashi", "Krishna Dvadashi", "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya"]
NAKSHATRA_NAMES = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]

@router.get("/calculate")
async def calculate_muhurta(
    event_date: date = Query(..., alias="date"),
    activity: str = Query("business", pattern="^(business|marriage|travel|health)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Profile).where(Profile.user_id == current_user.id).limit(1))
    profile = result.scalars().first()
    if profile is None:
        raise HTTPException(status_code=400, detail="Сначала заполните профиль рождения и укажите часовой пояс.")
    try:
        zone = ZoneInfo(profile.timezone)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="В профиле указан некорректный часовой пояс.") from exc

    samples = []
    # Daytime screening in the profile's local timezone. A proper muhurta also
    # needs local sunrise/sunset, location-specific dosha checks and tradition settings.
    for hour in range(6, 22):
        local_dt = datetime.combine(event_date, time(hour, 0), tzinfo=zone)
        utc_dt = local_dt.astimezone(timezone.utc)
        panchanga = engine.calculate_panchanga(utc_dt, profile.lon, profile.lat)
        tithi = int(panchanga["tithi"])
        nakshatra = int(panchanga["nakshatra"])
        score = 5 + (2 if tithi in FAVORABLE_TITHIS else 0) + (2 if nakshatra in FAVORABLE_NAKSHATRAS else 0)
        if tithi in ACTIVITY_TITHI_PENALTIES[activity]:
            score -= 3
        score = max(1, min(9, score))
        samples.append({
            "time": local_dt.strftime("%H:%M"),
            "score": score,
            "tithi": tithi,
            "tithi_name": TITHI_NAMES[(tithi - 1) % 15],
            "nakshatra": nakshatra,
            "nakshatra_name": NAKSHATRA_NAMES[(nakshatra - 1) % 27],
            "yoga": panchanga["yoga"],
            "karana": panchanga["karana"],
        })
    best = max(samples, key=lambda x: x["score"])
    return {
        "date": event_date.isoformat(),
        "activity": activity,
        "timezone": profile.timezone,
        "method": "Hourly Panchanga screening (tithi and nakshatra heuristic)",
        "best_hour": best,
        "samples": samples,
        "limitations": "Предварительный скрининг Панчанги, не полный расчёт мухурты: не учтены восход/закат, лагна, Раху-кала, местные традиции и персональная карта. Не является гарантией результата.",
    }
